# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 20:00:57 2019

@author: tom
"""
from ballclient.service.astar import A_Star
from ballclient.service.GameMap import gameMap as gameMap
from ballclient.service.StateMachine import *
from ballclient.service.Log import logger
from ballclient.service.SharedDataBase import db #共享数据库
from ballclient.service.SharedDataBase import point #共享数据库

import math
import copy

    
    
        
class AI:
    
    '''这一块是类的共享变量，所有类的实例共享一份'''
    #四个分裂子图的中心坐标
    subMapCent = []
    
    #这个unsee map也是 y,x的方式储存坐标
    unseeMap   = []
    
    allUnseeList = []
        
    #stuipid数据

    '''共享变量END'''
    
    def __init__(self, id,vision,name):
        self.isvalid=True
        self.id=id
        self.vision=vision
        self.mpoint=point(0,0)
        self.vis_num=0
        
        #巡逻点 由 power和returnPower组成
        self.waypoint=[]
        self.powers=[]
        self.returnPower = []
        
        
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
        
        #self.test = 0#测试用的
        AI.subMapCent = [point(gameMap.subMap[0][0],gameMap.subMap[0][1]),\
              point(gameMap.subMap[1][0],gameMap.subMap[1][1]),\
              point(gameMap.subMap[2][0],gameMap.subMap[2][1]),\
              point(gameMap.subMap[3][0],gameMap.subMap[3][1])]
        
        AI.unseeMap = [[0 for col in range(gameMap.width)]\
                        for row in range(gameMap.height)]
        
        self.mCentre = point(0,0)#子图中点
        
        #子图的两个边界点 
        self.subMap = []
        
        #没看过的点 [x,y]
        
        
        
        if self.name not in db.names:#注册数据库
            db.register(self.name)
        self.unseeList = []
        AI.allUnseeList.append(self.unseeList)
        
    def update(self):
        self.isvalid=False
        for pinfo in gameMap.ourCurrentPlayer:
            if pinfo[0]==self.id:
                self.isvalid=True
                self.mpoint=point(pinfo[1],pinfo[2])
                if self.name in db.returnNames:
                    db.restorePower(self.name)

        if not self.isvalid:
            #如果被吃掉，那么就要把自己分配的分数归还，然后重新给其他人分配分数点
            
            print(self.name,"not in current player")
            return   

        
            

                
        '''更新 db power'''
        for power in self.seePowers:
            if power not in db.powers[self.name]:
                p = point(power[1],power[2],power[0])
                logger.finfo("update power: ", p,p.power)
                p2 = copy.deepcopy(power)
                db.updatePower(self.name,p2)
        if self.name == 'stupid':
            logger.ferror("db all power: ",db.allPowers)

        logger.ferror(self.name,"db power: ",db.powers[self.name])
        
        


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
        
        '''更新unsee地图'''
        v = self.vision
        if gameMap.leg == 1:
            lx   = 0 if self.mpoint.x-v<0 else self.mpoint.x-v
            ly   = 0 if self.mpoint.y-v<0 else self.mpoint.y-v
            
            hx   = gameMap.width if self.mpoint.x+v >= gameMap.width else self.mpoint.x+v+1
            hy   = gameMap.width if self.mpoint.y+v >= gameMap.width else self.mpoint.y+v+1
            for x in range(lx,hx):
                for y in range(ly,hy):
                    #logger.finfo("range (%s,%s)",x,y)
                    AI.unseeMap[y][x] = 1
                    if [x,y] in self.unseeList:
                        self.unseeList.remove([x,y])
            AI.unseeMap[self.mpoint.y][self.mpoint.x] = 2;
            if (self.name == 'git'):
                logger.finfo("=== unsee map ===")
                for i in range(len(AI.unseeMap)):
                    logger.finfo(AI.unseeMap[i])
            
                logger.finfo("===%s update unseeList===")
                logger.finfo(AI.allUnseeList)
                
            logger.finfo("===",self.name,"unsee List===")
            logger.finfo(self.unseeList)
        #todo unseenlist 还有重叠部分，除了自己看到以外，别人也有可能看到，因此需要同步更新
        
        
        #状态转移
    def origin_transition(self,TState):
        #在状态转移之前，执行一次start函数
        self.start()
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
        logger.finfo("origin state->",newState)
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
        logger.finfo("search_score_state->",newState)
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
        logger.finfo("run_away_state->",newState)
    
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
        logger.finfo("catch_state->",newState)
    
        return newState
    
    
    
    
    
    #state action 在某个状态下做什么事，就在这里写了
    def search(self):
        logger.finfo("%s Do search", self.name)
       
        #选取unsee点游走
        logger.ferror("len useelist",self.unseeList)
        if len(self.unseeList):
            print(point(self.unseeList[0][0],self.unseeList[0][1]))
            p = point(self.unseeList[0][0],self.unseeList[0][1])
            #self.goto(p)
            logger.finfo(self.target)
            
            self.eat(p)
            return
        
        #当搜索过全图以后，选取得分点跑位
        ''' 更新 waypoint  
       
        if len(db.returnNames):#添加 returnpowers到waypoint里去
            rn = db.returnNames[0]
            self.waypoint.append(db.returnPowers[rn][1],\
                                 db.returnPowers[rn][2])
        else:
            self.waypoint.append(db.powers[self.name][1],\
                                 db.powers[self.name][2])
        '''
        
        print("==============更新过全图================")
        if len(db.returnNames):
            print("returnName:", db.returnNames)
            print("returnName[0]",db.returnNames[0])
            print("returnPower: ",db.returnPowers)
            print("returnPower name[0]",db.returnPowers[db.returnNames[0]])
            for name in db.returnNames:
                logger.ferror("发现returnNames")
                if name not in db.useNames:
                    logger.ferror("发现returnNames没被使用")
                    rp = db.useReturnPower(name)
                    for power in rp:
                        logger.ferror("add return power",power)
                        self.returnPower.append(point(power[1],power[2]))
                break
        else:
            self.returnPower.clear()
        print(self.name,"db powers:", db.powers[self.name])
        print(self.name,"return power", self.returnPower)
        logger.ferror("====更新分配点=====")
        logger.ferror("return names:",db.returnNames)
        logger.ferror(self.name,"usenames :",db.useNames)
        logger.ferror(self.name,".returnPower:",self.returnPower)
        logger.ferror(self.name,".powerpoint:",db.pointPower(db.powers,self.name))
        
        logger.ferror("+++++++++++++++++++")
        

        self.waypoint = db.pointPower(db.powers,self.name)+self.returnPower
        logger.ferror("+waypoint: +",self.waypoint)

        #如果跑位的时候看到分优先吃分
        self.eat(self.waypoint[self.vis_num])

        
    def catch(self):
        logger.info("%s Do catch", self.name)
        
    def runaway(self):
        logger.info("%s Do runaway", self.name)
        #simple runaway 
        
        
    #这个函数理论上只在leg start的时候执行，所以在这里分裂子图，初始化搜索
    def start(self):
        logger.info("%s Do start", self.name)
        
        #首先分裂图，成四个子图，选取每个子图的中心，根据距离选取每个人搜索的子图大小
        d = 25
        if self.mCentre.equals(point(0,0)):
            for c in AI.subMapCent:
                if c.distance(self.mpoint) < d:
                    d = c.distance(self.mpoint)
                    self.mCentre = c
            AI.subMapCent.remove(self.mCentre)
            logger.info("%s choose mCentre %s",self.name,self.mCentre)
        #self.waypoint.append(self.mCentre)
        
        
        #选取中心点后建立未搜索子图
        halfx = int((gameMap.width+1)/2)
        halfy = int((gameMap.height+1)/2)
        x = gameMap.width
        y = gameMap.height
        

        #左上角        
        if self.mCentre.equals(point(gameMap.subMap[0][0],gameMap.subMap[0][1])):
            self.subMap = [0,0,halfx,halfy]
           
        #左下角
        elif self.mCentre.equals(point(gameMap.subMap[1][0],gameMap.subMap[1][1])):
            self.subMap = [0,halfy,halfx,y]
            
        #右上角
        elif self.mCentre.equals(point(gameMap.subMap[2][0],gameMap.subMap[2][1])):
            self.subMap = [halfx,0,x,halfy]
            
        #右下角
        elif self.mCentre.equals(point(gameMap.subMap[3][0],gameMap.subMap[3][1])):
            self.subMap = [halfx,halfy,x,y]
            
        #只有第一回合才有unseelist
        if gameMap.leg == 1:
            for x in range(self.subMap[0],self.subMap[2]):
                for y in range(self.subMap[1],self.subMap[3]):
                    if AI.unseeMap[y][x] == 0:
                        self.unseeList.append([x,y])
            logger.finfo("===%s unseeList===",self.name)
            logger.finfo(self.unseeList)
    # end def start()
        
            
        
        
    def run(self):
        
        #测试序列 理论上转移 origin state-> SEARCH_STATE -> CATCH -> RUNAWAY_STATE
        #test_queue = [(self.t.P | self.t.SEE),(self.t.P | self.t.SEE | self.t.BIGFISH),self.t.SEE]

        logger.finfo(self.name," nowTState: ",self.nowTState)
        self.stateMachine.run(self.nowTState)
        Do = self.stateAction[self.stateMachine.nowState]
        Do()
        
        if self.mpoint.equals(self.target):
            #print('arrive waypoint ',self.vis_num,' ',self.mpoint.x,' ',self.mpoint.y)
            logger.info("%s arrive num[%s] waypoint: [%s,%s]",self.name,self.vis_num\
                        ,self.mpoint.x,self.mpoint.y)
            self.vis_num=self.vis_num+1
            if self.vis_num>=len(self.waypoint):
                self.vis_num=0
        
        
    def goto(self,p):#这个函数，用来计算target的，回避掉不可达点
        logger.fwarning("goto map ",p,": ",gameMap.map[p.y][p.x])

        while 30 > gameMap.map[p.y][p.x] > 6:
            '''
            #从隧道滑开
            if(gameMap.map[p.y][p.x] == 20):
                p.y -= 1
            if(gameMap.map[p.y][p.x] == 21):
                p.y += 1
            if(gameMap.map[p.y][p.x] == 22):
                p.x -= 1
            if(gameMap.map[p.y][p.x] == 23):
                p.x += 1
            '''
            
            #如果是障碍物,外围往中心滑，中心往外滑
           # if(gameMap.map[p.y][p.x] == 8):
            halfx = int(gameMap.width/2)
            halfy = int(gameMap.height/2)
            dx = 1 if halfx-p.x>0 else -1
            dy = 1 if halfy-p.y>0 else -1
            if point(halfx,halfy).distance(p) < 3:
                dx = -dx
                dy = -dy
            p.x += dx
            p.y += dy
        logger.fwarning("goto :",p)
                
        self.target.x = p.x
        self.target.y = p.y
        
    def eat(self,p=0):#这个东西放在goto的后面，让游荡的时候优先吃分
        logger.info("%s eat!", self.name)
        if p == 0:
            p = self.mCentre
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
                #print ("new ",self.name,": ",cur_power)
                logger.info("new %s: %s",self.name,cur_power)
                #print("gCurpowers:",gameMap.curpowers)
                break
        
        if len(self.seePowers):
            self.target.x=self.seePowers[0][1]
            self.target.y=self.seePowers[0][2]
            #logger.info("%s target [%s,%s]",)
            #print(self.target.y,'choose  power',self.target.x,self.name)
            logger.info("%s choose power [%s,%s]",self.name,self.target.x,self.target.y)
            #必须保证waypoints不为空，否则肯定会出错
        else:
            self.goto(p)
        '''
            if self.waypoint:#当waypoint不为空才赋值 
                logger.info("%s target为waypoint坐标",self.name)
                #self.target.x=self.waypoint[self.vis_num].x
                #self.target.y=self.waypoint[self.vis_num].y
                self.goto(self.waypoint[self.vis_num])
            else:#否则就给自己坐标，不动
                logger.info("%s target为自身坐标",self.name)
                self.goto(self.mCentre)
        
        if self.mpoint.equals(self.target):
            #print('arrive waypoint ',self.vis_num,' ',self.mpoint.x,' ',self.mpoint.y)
            logger.info("%s arrive num[%s] waypoint: [%s,%s]",self.name,self.vis_num\
                        ,self.mpoint.x,self.mpoint.y)
            self.vis_num=self.vis_num+1
            if self.vis_num>=len(self.waypoint):
                self.vis_num=0
        '''
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
class Team:
    def __init__(self):
        self.stupid=AI(gameMap.ourPlayer[0],gameMap.vision,'stupid')
        self.idiot=AI(gameMap.ourPlayer[1],gameMap.vision,'idiot')
        self.fool=AI(gameMap.ourPlayer[2],gameMap.vision,'fool')
        self.git=AI(gameMap.ourPlayer[3],gameMap.vision,'git')
              
        
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

def goto(p):#这个函数，用来计算target的，回避掉不可达点
    while 30 > gameMap[p.y][p.x] > 6:
        #从隧道滑开
        if(gameMap[p.y][p.x] == 20):
            p.y -= 1
        if(gameMap[p.y][p.x] == 21):
            p.y += 1
        if(gameMap[p.y][p.x] == 22):
            p.x -= 1
        if(gameMap[p.y][p.x] == 23):
            p.x += 1

        #如果是障碍物,外围往中心滑，中心往外滑
        if(gameMap[p.y][p.x] == 8):
            halfx = int(gameMap.width/2)
            halfy = int(gameMap.height/2)
            dx = 1 if halfx-p.x>0 else -1
            dy = 1 if halfy-p.y>0 else -1
            if point(halfx,halfy).distance(p) < 3:
                dx = -dx
                dy = -dy
            p.x += dx
            p.y += dy

            
    return p
 """       