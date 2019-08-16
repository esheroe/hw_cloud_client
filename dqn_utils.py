# -*- coding: utf-8 -*-
"""
Created on Sun Aug 11 13:48:04 2019

@author: Yan JY
"""

import tensorflow as tf
import numpy as np
import random
import pickle
import os

batch_size = 32 #How many experiences to use for each training step.
update_freq = 4 #How often to perform a training step.
buffer_size = 100000 # expreience buffer size
start_train_size = 1000 # if the number of experiences in buffer greater than 1000, starting the training
gamma = 0.98 #Discount factor on the target Q-values
action_num = 4 # number of vaild action 
epsilon = 0.5 # chance of random action
tau = 1e-3 #Rate to update target network toward primary network
learning_rate = 1e-4 # learning rate

class buildNet():
    def __init__(self, scopeName, fc1_size = 512, fc2_size = 512, h_size = 256):
        with tf.variable_scope(scopeName):
            self.Input = tf.placeholder(shape=[None,9,9],dtype=tf.float32)
            self.FlattedInput = tf.contrib.layers.flatten(self.Input)
            # FC1
            self.w1 = tf.Variable(tf.random_normal([9*9,fc1_size]))
            self.b1 = tf.Variable(tf.random_normal([1,fc1_size]))
            self.fc1 = tf.nn.relu(tf.matmul(self.FlattedInput, self.w1) + self.b1)
            # FC2
            self.w2 = tf.Variable(tf.random_normal([fc1_size,fc2_size]))
            self.b2 = tf.Variable(tf.random_normal([1,fc2_size]))
            self.fc2 = tf.nn.relu(tf.matmul(self.fc1, self.w2) + self.b2)        
            # split to two stream
            self.streamA , self.streamV =  tf.split(self.fc2, 2, 1)
            # FC1_Advantage
            self.fc1_AW = tf.Variable(tf.random_normal([256,h_size]))
            self.fc1_Ab = tf.Variable(tf.random_normal([1,h_size]))
            self.fc1_A = tf.nn.relu(tf.matmul(self.streamA, self.fc1_AW) + self.fc1_Ab)
            # FC1_Value
            self.fc1_VW = tf.Variable(tf.random_normal([256,h_size]))
            self.fc1_Vb = tf.Variable(tf.random_normal([1,h_size]))
            self.fc1_V = tf.nn.relu(tf.matmul(self.streamV, self.fc1_AW) + self.fc1_Vb)
            # FC2_Advantage
            self.fc2_AW = tf.Variable(tf.random_normal([h_size,action_num]))
            self.Advantage = tf.matmul(self.fc1_A, self.fc2_AW)
            # FC2_Advantage
            self.fc2_VW = tf.Variable(tf.random_normal([h_size,1]))
            self.Value = tf.matmul(self.fc1_V, self.fc2_VW)
            #Then combine them together to get our final Q-values.
            self.Qout = self.Value + tf.subtract(self.Advantage,\
                tf.reduce_mean(self.Advantage,reduction_indices=1,keep_dims=True))
    
            self.predict = tf.argmax(self.Qout,1)
    
            #Below we obtain the loss by taking the sum of squares difference between the target and prediction Q values.
            self.targetQ = tf.placeholder(shape=[None],dtype=tf.float32)
            self.actions = tf.placeholder(shape=[None],dtype=tf.int32)
            self.actions_onehot = tf.one_hot(self.actions, action_num, dtype=tf.float32)
    
            self.Q = tf.reduce_sum(tf.multiply(self.Qout, self.actions_onehot), \
                reduction_indices=1)
    
            self.td_error = tf.square(self.targetQ - self.Q)
            self.loss = tf.reduce_mean(self.td_error)
            self.trainer = tf.train.AdamOptimizer(learning_rate)
            self.updateModel = self.trainer.minimize(self.loss)

class Qnetwork():
    def __init__(self, sess, netName):
        self.sess = sess 
        self.mainQN = buildNet('mainQN' + netName)
        self.targetQN = buildNet('targetQN' + netName)
        mainVar = tf.trainable_variables('mainQN' + netName)
        targetVar = tf.trainable_variables('targetQN' + netName)  
        self.targetOps = self.updateTargetGraph(mainVar, targetVar)
        self.sess.run(tf.global_variables_initializer())

        # saving and loading networks and memory
        self.path = './%s_model'% netName
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.Buffer = experience_buffer(self.path)
        self.saver = tf.train.Saver()
        checkpoint = tf.train.get_checkpoint_state(self.path)
        if checkpoint and checkpoint.model_checkpoint_path:
            self.saver.restore(self.sess, checkpoint.model_checkpoint_path)
            print("Successfully loaded" + self.path , checkpoint.model_checkpoint_path)
            print ("\n\n")
        else:
            print("Could not find old network weights")
        ''''''

    def trainNet(self):
        if len(self.Buffer.buffer) > 1000:
            #Get a random batch of experiences.
            trainBatch = self.Buffer.sample(batch_size) 
            #Below we perform the Double-DQN update to the target Q-values
            A = self.sess.run(self.mainQN.predict, feed_dict={self.mainQN.Input:np.vstack(trainBatch[:,3])})
            Q = self.sess.run(self.targetQN.Qout, feed_dict={self.targetQN.Input:np.vstack(trainBatch[:,3])})
            doubleQ = Q[range(batch_size), A]
            targetQ = trainBatch[:, 2] + gamma*doubleQ
            #Update the network with our target values.
            _ = self.sess.run(self.mainQN.updateModel, feed_dict={
                    self.mainQN.Input: np.vstack(trainBatch[: , 0]),
                    self.mainQN.targetQ: targetQ,
                    self.mainQN.actions: trainBatch[: , 1]})
            #Set the target network to be equal to the primary network.
            self.updateTarget(self.targetOps, self.sess) 
            
    def save_model_memory(self):
        # save model
        self.saver.save(self.sess, self.path +'/model.cptk')
        print("Saved %s Model Successfully!"%self.path)
        # save memory
        file = open(self.path + '/memory.bin','wb')
        pickle.dump(self.Buffer.buffer, file)
        file.close()
        print("Saved %s Memory Successfully!"%self.path)


    def updateTargetGraph(self,mainVar,targetVar):
        op_holder = []
        for idx,var in enumerate(mainVar):
            op_holder.append(targetVar[idx].assign((var.value()*tau) + \
             ((1-tau)*targetVar[idx].value())))
        return op_holder

    def updateTarget(self,op_holder,sess):
        for op in op_holder:
            sess.run(op)

    def explore(self, state):
        if np.random.rand(1) < epsilon:
            a = random.randint(0,3)
        else:
            a = self.getAction(state)
        return a

    def getAction(self, state):
        a = self.sess.run(self.mainQN.predict,feed_dict={self.mainQN.Input: [state]})[0]
        return a

class experience_buffer():
    def __init__(self, path):
        if os.path.exists(path + '/memory.bin'):
            file = open(path + '/memory.bin','rb')
            self.buffer = pickle.load(file)
            print("Successfully loaded" + path + '/memory.bin')
            print ("\n\n")
        else:
            self.buffer = []
        self.buffer_size = buffer_size

    def add(self,experience):
        if len(self.buffer) + len(experience) >= self.buffer_size:
            self.buffer[0:(len(experience)+len(self.buffer))-self.buffer_size] = []
        self.buffer.extend(experience)

    def sample(self,size):
        return np.reshape(np.array(random.sample(self.buffer,size)),[size,5])


