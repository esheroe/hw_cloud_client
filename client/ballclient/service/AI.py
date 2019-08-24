# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 20:00:57 2019

@author: tom
"""
from ballclient.service.astar import A_Star
from ballclient.service.GameMap import gameMap as gameMap
from ballclient.service.StateMachine import StateMachine
import math
class point:
    def __init__(self,x,y):
        self.x=x
        self.y=y
    
    def distance(self,p):
        if math.fabs(self.x-p.x)>math.fabs(self.y-p.y):
            return math.fabs(self.x-p.x)
        else:
            return math.fabs(self.y-p.y)
        
class Transition:
    def __init__(self):
        '''
        t.P | t.SEE | t.BIGFISH = 19
        t.P | t.SEE             = 3
        t.SEE | t.BIGFISH       = 18
        t.SEE                   = 2
        UNSEE                   = 0
        '''
        self.N = 0
        self.P = 1
        self.SEE = 2
        self.BIGFISH = 16
        
class State:
    def __init__(self):
        self.START = "START_STATE"
        self.RUNAWAY = "RUNAWAY_STATE"
        self.SEARCH = "SEARCH_STATE"
        self.CATCH = "CATCH_STATE"
        self.ERROR = "ERROR_STATE"

class AI:
    def __init__(self, id,vision,name):
        self.isvalid=True
        self.id=id
        self.vision=vision
        self.mpoint=point(0,0)
        self.vis_num=0
        self.waypoint=[]
        self.powers=[]
        self.target=point(0,0)
        self.name=name
        
        #保存看到过但还没吃的分值 
        self.seePowers = []
        
        #状态转移条件

        self.nowTState = 0 # P|SEE 
        #初始化状态机
        self.stateMachine = StateMachine()
        #转移条件 
        self.t = Transition()
        #状态转移加入到状态机中
        self.s = State()
        self.stateMachine.add_state(self.s.START,self.origin_transition)
        self.stateMachine.add_state(self.s.SEARCH,self.search_transition)
        self.stateMachine.add_state(self.s.RUNAWAY,self.runaway_transition)
        self.stateMachine.add_state(self.s.CATCH,self.catch_transition)
        self.stateMachine.add_state(self.s.ERROR, None, end_state=1)#终止状态
        self.stateMachine.set_start(self.s.START)#设置初始状态
        
        #状态动作函数，在某个状态执行某个函数
        self.stateAction = {}
        self.stateAction[self.s.START] = self.start
        self.stateAction[self.s.SEARCH] = self.search
        self.stateAction[self.s.RUNAWAY] = self.runaway
        self.stateAction[self.s.CATCH] = self.catch
        
        self.test = 0#测试用的
        

        
    def update(self):
        self.isvalid=False
        for pinfo in gameMap.ourCurrentPlayer:
            if pinfo[0]==self.id:
                self.isvalid=True
                self.mpoint=point(pinfo[1],pinfo[2])
                
        #吃分检测
        for power in self.seePowers:
            if power not in gameMap.curpowers: #吃到分了
                self.seePowers.remove(power)
                
        #todo 我想把power all放在这个里面来，但是放进来后机器人就不动了，暂时没找到bug在哪    
        for cur_power in gameMap.curpowers:
            if(self.mpoint.distance(point(cur_power[1],cur_power[2])) <= self.vision):
                if cur_power not in self.seePowers:
                    self.seePowers.append(cur_power)
                    gameMap.curpowers.remove(cur_power) #从中取走这个点，避免和其他机器人冲突
                print ("new ",self.name,": ",cur_power)
                print("gCurpowers:",gameMap.curpowers)
                break


        
        
        #todo 这个更新状态还没做，参考run下面的代码做状态更新
        '''更新状态'''
        self.nowTState = 0 #每回合状态清零
        if gameMap.isOurPower():
            self.nowTState |= self.t.P #优势
        else:
            self.nowTState |= self.t.N #劣势
        
        for opp in gameMap.oppPlayer:
            if self.mpoint.distance(point(opp[1],opp[2])) <= self.vision:
                self.nowTState |= self.t.SEE     #看到敌人了
                if opp[3] >= 20:                     #大于20分的敌人认为是大鱼
                    self.nowTState |= self.t.BIGFISH #看到大鱼了
        
        
        
        
        
        
        
        #状态转移
    def origin_transition(self,TState):
        t = TState & 0x0f #取低四位
        if(t == self.t.P):
            newState = self.s.SEARCH
        elif(t == self.t.N):
            newState = self.s.SEARCH
        elif(t == self.t.SEE):
             newState = self.s.RUNAWAY
        elif(t == self.t.P | self.t.SEE):
            newState = self.s.SEARCH
        else:
            newState = "error_state"
        print("origin state->",newState)
        return newState

    #search score state
    def search_transition(self,TState):
        
        t = TState & 0x0f #取低四位
        #这里要注意一下，没用低四位，而是加了可选择位，其他的elif用的低四位
        if(TState == self.t.P | self.t.BIGFISH | self.t.SEE):
            newState = self.s.CATCH
        elif(t == self.t.N):
            newState = self.s.SEARCH
        elif(t == self.t.SEE):
             newState = self.s.RUNAWAY
        elif(t == self.t.P | self.t.SEE):
            newState = self.s.SEARCH
        elif(t == self.t.P):
            newState = self.s.SEARCH
        else:
            newState = "error_state"
        print("search_score_state->",newState)
        return newState
    
    def runaway_transition(self,TState):
        t = TState & 0x0f #取低四位
        if(TState == self.t.P | self.t.BIGFISH | self.t.SEE):
            newState = self.s.CATCH
        elif(t == self.t.N):
            newState = self.s.SEARCH
        elif(t == self.t.SEE):
             newState = self.s.RUNAWAY
        elif(t == self.t.P | self.t.SEE):
            newState = self.s.SEARCH
        elif(t == self.t.P):
            newState = self.s.SEARCH
        else:
            newState = "error_state"
        print("run_away_state->",newState)
    
        return newState
    
    def catch_transition(self,TState):
        t = TState & 0x0f #取低四位
        if(TState == self.t.P | self.t.BIGFISH | self.t.SEE):
            newState = self.s.CATCH
        elif(t == self.t.N):
            newState = self.s.SEARCH
        elif(t == self.t.SEE):
             newState = self.s.RUNAWAY
        elif(t == self.t.P | self.t.SEE):
            newState = self.s.SEARCH
        elif(t == self.t.P):
            newState = self.s.SEARCH
        else:
            newState = "error_state"
        print("catch_state->",newState)
    
        return newState
    
    #state action 在某个状态下做什么事，就在这里写了
    def search(self):
        print("Do search")
        
    def catch(self):
        print("Do catch")
        
    def runaway(self):
        print("Do runaway")
        
    def start(self):
        print("Do start")
        
            
        
        
    def run(self):
        if len(self.seePowers):
            self.target.x=self.seePowers[0][1]
            self.target.y=self.seePowers[0][2]
            print(self.target.y,'choose  power',self.target.x,self.name)
            #必须保证waypoints不为空，否则肯定会出错
        else:
            self.target.x=self.waypoint[self.vis_num].x
            self.target.y=self.waypoint[self.vis_num].y
        if self.mpoint.x ==self.waypoint[self.vis_num].x and self.mpoint.y ==self.waypoint[self.vis_num].y :
            print('arrive waypoint ',self.vis_num,' ',self.mpoint.x,' ',self.mpoint.y)
            self.vis_num=self.vis_num+1
            if self.vis_num>=len(self.waypoint):
                self.vis_num=0
        
        
        #这段代码是测试代码
        #测试序列 理论上转移 origin state-> SEARCH_STATE -> CATCH -> RUNAWAY_STATE
        test_queue = [(self.t.P | self.t.SEE),(self.t.P | self.t.SEE | self.t.BIGFISH),self.t.SEE]
        
        self.test = self.test + 1
        self.test = self.test%3
        print(self.name," nowTState: ",self.nowTState)
        self.stateMachine.run(self.nowTState)
        Do = self.stateAction[self.stateMachine.nowState]
        Do()
        #这段代码是测试代码
        
      
class Team:
    def __init__(self):
        self.stupid=AI(gameMap.ourPlayer[0],gameMap.vision,'stupid')
        self.idiot=AI(gameMap.ourPlayer[1],gameMap.vision,'idiot')
        self.fool=AI(gameMap.ourPlayer[2],gameMap.vision,'fool')
        self.git=AI(gameMap.ourPlayer[3],gameMap.vision,'git')
        self.stupid.waypoint.append(point(4,18))
        #self.stupid.waypoint.append(point(3,8))
        #self.stupid.waypoint.append(point(3,3))
        #self.stupid.waypoint.append(point(8,3))
        self.stupid.waypoint.append(point(4,4))
        
        self.idiot.waypoint.append(point(3,6))
        self.idiot.waypoint.append(point(11,6))
        self.idiot.waypoint.append(point(3,16))
       # self.idiot.waypoint.append(point(16,16))
        
        self.fool.waypoint.append(point(5,16))
        self.fool.waypoint.append(point(11,16))
        self.fool.waypoint.append(point(16,16))
        
        self.git.waypoint.append(point(16,18))
        self.git.waypoint.append(point(16,4))
        #self.git.waypoint.append(point(3,16))
        self.a_star = A_Star(0, 0, 0, 0,gameMap.height,gameMap.width)
    
    def update(self):
        self.stupid.update()
        self.idiot.update()
        self.fool.update()
        self.git.update()
        
    def process(self):
        self.update()
        #self.power_all()
        self.stupid.run()
        self.idiot.run()
        self.fool.run()
        self.git.run()
        action=[]
        if self.stupid.isvalid:
            action.append(self.a_star.find_path(self.stupid.mpoint.x,self.stupid.mpoint.y,self.stupid.target.x,self.stupid.target.y,self.stupid.name))
        else:
            action.append(0)
                
        if self.idiot.isvalid:
            action.append(self.a_star.find_path(self.idiot.mpoint.x,self.idiot.mpoint.y,self.idiot.target.x,self.idiot.target.y,self.idiot.name))
        else:
            action.append(0)
            
        if self.fool.isvalid:
            action.append(self.a_star.find_path(self.fool.mpoint.x,self.fool.mpoint.y,self.fool.target.x,self.fool.target.y,self.fool.name))
        else:
            action.append(0)
            
        if self.git.isvalid:
            action.append(self.a_star.find_path(self.git.mpoint.x,self.git.mpoint.y,self.git.target.x,self.git.target.y,self.git.name))
        else:
            action.append(0)
        return action
        
    def power_all(self):
        self.stupid.powers.clear()
        self.idiot.powers.clear()
        self.fool.powers.clear()
        self.git.powers.clear()
        for cur_power in gameMap.curpowers:
            if getdis(self.stupid.mpoint,point(cur_power[1],cur_power[2]))<=self.stupid.vision:
                self.stupid.powers.append(point(cur_power[1],cur_power[2]))
                #print ("stupid power: ",cur_power)
                continue
            if getdis(self.idiot.mpoint,point(cur_power[1],cur_power[2]))<=self.idiot.vision:
                self.idiot.powers.append(point(cur_power[1],cur_power[2]))
                #print ("idiot power: ",cur_power)
                continue
            if getdis(self.fool.mpoint,point(cur_power[1],cur_power[2]))<=self.fool.vision:
                self.fool.powers.append(point(cur_power[1],cur_power[2]))
                #print ("fool power: ",cur_power)
                continue
            if getdis(self.git.mpoint,point(cur_power[1],cur_power[2]))<=self.git.vision:
                self.git.powers.append(point(cur_power[1],cur_power[2]))
                #print ("git power: ",cur_power)
                continue
            
        
def getdis(p1,p2):
    if math.fabs(p1.x-p2.x)>math.fabs(p1.y-p2.y):
        return math.fabs(p1.x-p2.x)
    else:
        return math.fabs(p1.y-p2.y)
"""    
if 1:
    print('test') 
    player=[]
    power=[]
    for i in range(4):
        player.append(i) 
        power.append(point(i,i))
    moyu=Team(player,3)
    moyu.update()
    moyu.power_all(power)
    moyu.process()
    print('test')
"""
        