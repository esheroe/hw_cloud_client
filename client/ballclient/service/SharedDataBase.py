# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 09:51:16 2019

@author: GP63
"""
import copy
from ballclient.service.Log import logger

from ballclient.service.GameMap import gameMap as gameMap
import math

class point:
    def __init__(self,x,y,power = 0):
        self.x=x
        self.y=y
        self.power = power #当这个坐标表示分数的时候，这个值表示分值
        
    #自定义了个打印函数
    def __str__(self):
        return "(%d, %d)"%(self.x,self.y)
    
    def distance(self,p):
        if math.fabs(self.x-p.x)>math.fabs(self.y-p.y):
            return math.fabs(self.x-p.x)
        else:
            return math.fabs(self.y-p.y)
    def equals(self,p):
        return self.x == p.x and self.y == p.y
    
    def SymPoint(self):#算中心中心对称点
        w = gameMap.width
        h = gameMap.height
        sx = w-self.x
        sy = h-self.y
        return point(sx,sy)
    
    def pointTo(self,p):
        x = p.x - self.x
        y = p.y - self.y
        return Vector(x,y)
    
    def alongVector(self,v):
        weight = 0
        if math.fabs(v.x) > math.fabs(v.y):
            weight = 1/math.fabs(v.x)
        else:
            weight = 1/math.fabs(v.y)
        v.weighting(weight)
        x = self.x
        y = self.y
        while x > 0 and x < 19 and y > 0 and y < 19:
            x += v.x
            y += v.y
        
        return point(int(x),int(y))

class Vector:
    def __init__(self,x,y):        
        self.x = x
        self.y = y
        
    
    def plus(self,v):
        x = self.x + v.x
        y = self.y + v.y
        return Vector(x,y)
    
    
    def weighting(self,weight):#算加权
        self.x = self.x * weight
        self.y = self.y * weight
        
    def length(self):
        eps = 1e-20        #防止零向量计算模长的除零计算error
        return math.sqrt(pow(self.x,2)+pow(self.y,2))+eps
    
    def dotMul(self,v):#点乘
        return self.x*v.x + self.y*v.y
    
    def xMul(self,v):#叉乘
        return self.x*v.y - self.y*v.x
    
    def angleWith(self,v):
        cos_theta = self.dotMul(v) / (self.length()*v.length()) 
        if cos_theta > 1: 
            cos_theta = 1
        elif cos_theta < -1:
            cos_theta = -1
        
        r = math.acos(cos_theta)
        return math.degrees(r)
    
    def norm(self):
        x = self.x/self.length()
        y = self.y/self.length()
        return Vector(x,y)
    
    def normPlus(self,v):
        if self.isParallel(v):
            if self.dotMul(v) < 0:
                v.y = v.y + 0.00001
                print("反向相加")
        return self.norm().plus(v.norm())
    
    def vertical(self):
        x = (-self.y)
        y = self.x
        return Vector(x,y)
    
    def isParallel(self,v):
        return self.xMul(v) == 0
    
    def isVertical(self,v):
        return self.dotMul(v) == 0
 
'''   
v1 = Vector(1,1)
v2 = Vector(3,3)
v3 = v1.plus(v2)
v4 = Vector(3,1)  
v5 = Vector(-3,-1)
'''
    
    


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
            
            
    def pointPower(self,dic,name): #返回这个人的得分列表
        pp = []
        for power in dic[name]:
            p = point(power[1],power[2])
            pp.append(p)
        return pp
            
        
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
        if name not in self.useNames:
            self.useNames.append(name)
        return self.returnPowers[name]
            
        
        
    
db = SharedDataBase()