# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 09:51:16 2019

@author: GP63
"""
import copy
from ballclient.service.Log import logger




#共享数据库，每个legstart AI类的东西都会清空，用这个保存所有的数据
'''这里的power是以 [power,x,y]方式储存注意！'''
class SharedDataBase:
    def __init__(self):
        self.names  = []
        self.powers = {}#最终跑位点 为 powers + returnPowers
        self.allPowers = []
        self.returnPowers = {} #死亡的鲲把自己的power释放在这
        self.returnNames = []
        self.unseeMap   = [] #未看见的地图
        
        self.useNames = [] #return 回来的分数被使用
        
        

        
    def register(self,name):#注册就在这里开辟空间了
        if name not in self.names:
            self.names.append(name)
            self.powers[name] = []
            
            
     
        
    def updatePower(self,name,power):
        if power not in self.allPowers:
            #p = point(power[1],power[2],power[0])
            self.powers[name].append(power)
            self.allPowers.append(power)
    
    def returnPower(self,name):
        if name not in self.returnNames:
            rname = copy.deepcopy(name)
            self.returnNames.append(rname)
            self.returnPowers[name] = copy.deepcopy(self.powers[name])
            logger.ferror(name,"return power: ", self.returnPowers[name])
        
    def restorePower(self,name):
        if name in self.returnNames:
            logger.ferror(name,"restore power: ", self.returnPowers[name])
            self.returnNames.remove(name)
            self.returnPowers.pop(name)
        if name in self.useNames:
            self.useNames.remove(name)
            
    def useReturnPower(self,name):
        self.useNames.append(name)
        return self.returnPowers[name]
            
        
        
    
db = SharedDataBase()