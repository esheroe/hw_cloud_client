# encoding:utf8
'''
业务方法模块，需要选手实现

选手也可以另外创造模块，在本模块定义的方法中填入调用逻辑。这由选手决定

所有方法的参数均已经被解析成json，直接使用即可

所有方法的返回值为dict对象。客户端会在dict前面增加字符个数。
'''
import tensorflow as tf
import numpy as np
import random
import ballclient.service.constants as constants
from ballclient.service.buildMap import GameMap
from ballclient.service.dqn_utils import Qnetwork

class Service():
    def __init__(self):
        self.force = 'think'
        self.mode = 'think'
        self.IS_attack = True
        self.createMap = GameMap()
        
        '''dqn 初始化'''
        tf.reset_default_graph()
        self.sess = tf.InteractiveSession()
        self.attackQN = Qnetwork(self.sess, 'attack')
        self.defenseQN = Qnetwork(self.sess, 'defense')

        
    def leg_start(self,msg):
        '''
        :param msg:
        :return: None
        '''
        # create global map
        self.createMap.handleMsg(msg) 
        
        print("round start")
        print("msg_name:%s" % msg['msg_name'])
        # print("map_width:%s" % msg['msg_data']['map']['width'])
        # print("map_height:%s" % msg['msg_data']['map']['height'])
        # print("vision:%s" % msg['msg_data']['map']['vision'])
        # print("meteor:%s" % msg['msg_data']['map']['meteor'])
        # print("tunnel:%s" % msg['msg_data']['map']['tunnel'])
        # print("wormhole:%s" % msg['msg_data']['map']['wormhole'])
        # print("teams:%s" % msg['msg_data']['teams'])
        print ("\n\n")

        teams = msg['msg_data']['teams']
        for team in teams:
            if team['id'] == constants.team_id:
                self.force = team['force']
                self.players_id = team['players']
                
        # create s and a and score for each player
        self.pre_state = {}
        self.pre_a = {}
        self.pre_score = {}
        for player_id in self.players_id:
            self.pre_state[player_id] = np.zeros((9,9))
            self.pre_a[player_id] = 0
            self.pre_score[player_id] = 0
            
        # print('pre_state:%s' % self.pre_state)
        # print('pre_a:%s' % self.pre_a)
        # print('pre_score:%s' % self.pre_score)

    def leg_end(self,msg):
        '''
        :param msg:
        {
            "msg_name" : "leg_end",
            "msg_data" : {
            "teams" : [
                {
                    "id" : 1001,          #队ID
                    "point" : 770         #本leg的各队所得点数
                },
                {
                "id" : 1002,
                "point" : 450
                 }
                ]
            }
        }
    
        :return:
        '''
        print ("round over")
        teams = msg["msg_data"]['teams']
        for team in teams:
            print ("teams:%s" % team['id'])
            print ("point:%s" % team['point'])
            print ("\n\n")
    
    
    def game_over(self,msg):
        print ("game over!")
        print ("\n\n")
        print ("=======================")
        self.attackQN.save_model_memory()
        self.defenseQN.save_model_memory()
    
    def round(self,msg):
        '''
        :param msg: dict
        :return:
        return type: dict
        '''
        # update local map
        self.createMap.updateMsg(msg) 
        
        self.mode = msg['msg_data']['mode']
        round_id = msg['msg_data']['round_id']
        players = msg['msg_data']['players']

        if self.force == self.mode:
            self.IS_attack = True
        else:
            self.IS_attack = False
    
        direction = {0: 'up', 1: 'down', 2: 'left', 3: 'right'}
        result = {
            "msg_name": "action",
            "msg_data": {
                "round_id": round_id
            }
        }
        action = []
        alive_players = []
        for player in players:
            if player['team'] == constants.team_id:
                alive_players.append(player['id'])
                state = self.createMap.paddedmap[self.createMap.dh//2 + player['y'] - 4: \
                                                 self.createMap.dh//2 + player['y'] + 5, \
                                                 self.createMap.dw//2 + player['x'] - 4: \
                                                 self.createMap.dw//2 + player['x'] + 5]
                d = False
                r = player['score'] - self.pre_score[player['id']]
                if self.IS_attack:
                    a = self.attackQN.explore(state)
                else:
                    a = self.defenseQN.explore(state)
                action.append({"team": player['team'], "player_id": player['id'],
                               "move": [direction[a]]})
                
                if round_id == 0 or round_id == 150:
                    pass
                else:
                    if self.IS_attack:
                        self.attackQN.Buffer.add(np.reshape(np.array([[self.pre_state[player['id']]], self.pre_a[player['id']], r, [state], d]),[1,5]))
                        self.attackQN.trainNet()
                    else:
                        self.defenseQN.Buffer.add(np.reshape(np.array([[self.pre_state[player['id']]], self.pre_a[player['id']], r, [state], d]),[1,5]))
                        self.defenseQN.trainNet()
                # swap observation
                self.pre_state[player['id']] = state
                self.pre_a[player['id']] = a
                self.pre_score[player['id']] = player['score'] 
        result['msg_data']['actions'] = action

        # 处理死亡的玩家
        if len(alive_players) != len(self.players_id): # 当活着的数量不等于初始玩家，代表有我方玩家死亡
            for player_id in self.players_id:
                # 如果player_id不在存活名单里，且该玩家上一时刻转态的中心点不是敌人，则表明该玩家死亡
                if player_id not in alive_players and self.pre_state[player_id][4,4] != 80: 
                    d = True
                    r = -100 - self.pre_score[player_id]
                    state = self.pre_state[player_id].copy()
                    state[np.where(state==80)] = 0 # 把敌人所在格子置为0
                    state[4,4] = 80 # 把玩家所在格子(中心)设置为80(敌方玩家编码)
                    if self.IS_attack:
                        self.attackQN.Buffer.add(np.reshape(np.array([[self.pre_state[player_id]], self.pre_a[player_id], r, [state], d]),[1,5]))
                    else:
                        self.defenseQN.Buffer.add(np.reshape(np.array([[self.pre_state[player_id]], self.pre_a[player_id], r, [state], d]),[1,5]))
                    self.pre_state[player_id] = state
                    self.pre_score[player_id] = 0 
        return result
