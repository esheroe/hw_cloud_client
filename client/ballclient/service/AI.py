# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 20:00:57 2019

@author: tom
"""
from ballclient.service.astar import A_Star
from ballclient.service.GameMap import gameMap as gameMap
import math
class point:
    def __init__(self,x,y):
        self.x=x
        self.y=y
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
        
    def update(self):
        self.isvalid=False
        for pinfo in gameMap.ourCurrentPlayer:
            if pinfo[0]==self.id:
                self.isvalid=True
                self.mpoint=point(pinfo[1],pinfo[2])
        
    def run(self):
        if len(self.powers):
            self.target.x=self.powers[0].x
            self.target.y=self.powers[0].y
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

      
class Team:
    def __init__(self):
        self.stupid=AI(gameMap.ourPlayer[0],gameMap.vision,'stupid')
        self.idiot=AI(gameMap.ourPlayer[1],gameMap.vision,'idiot')
        self.fool=AI(gameMap.ourPlayer[2],gameMap.vision,'fool')
        self.git=AI(gameMap.ourPlayer[3],gameMap.vision,'git')
        self.stupid.waypoint.append(point(3,13))
        self.stupid.waypoint.append(point(3,8))
        self.stupid.waypoint.append(point(3,3))
        self.stupid.waypoint.append(point(8,3))
        self.stupid.waypoint.append(point(13,3))
        
        self.idiot.waypoint.append(point(16,3))
        self.idiot.waypoint.append(point(16,8))
        self.idiot.waypoint.append(point(16,13))
        self.idiot.waypoint.append(point(16,16))
        
        self.fool.waypoint.append(point(11,8))
        self.fool.waypoint.append(point(10,10))
        self.fool.waypoint.append(point(8,11))
        
        self.git.waypoint.append(point(13,16))
        self.git.waypoint.append(point(8,16))
        self.git.waypoint.append(point(3,16))
        self.a_star = A_Star(0, 0, 0, 0,gameMap.height,gameMap.width)
    
    def update(self):
        self.stupid.update()
        self.idiot.update()
        self.fool.update()
        self.git.update()
        
    def process(self):
        self.update()
        self.power_all()
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
                continue
            if getdis(self.idiot.mpoint,point(cur_power[1],cur_power[2]))<=self.idiot.vision:
                self.idiot.powers.append(point(cur_power[1],cur_power[2]))
                continue
            if getdis(self.fool.mpoint,point(cur_power[1],cur_power[2]))<=self.fool.vision:
                self.fool.powers.append(point(cur_power[1],cur_power[2]))
                continue
            if getdis(self.git.mpoint,point(cur_power[1],cur_power[2]))<=self.git.vision:
                self.git.powers.append(point(cur_power[1],cur_power[2]))
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
        