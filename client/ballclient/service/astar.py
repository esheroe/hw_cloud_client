# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 21:46:41 2019

@author: tom
"""
# -*- coding: utf-8 -*-
import math
import copy
from ballclient.service.GameMap import gameMap as gameMap
#地图
test_map = [
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,97],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,8 ,8 ],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 0, 0, 0, 8, 8, 0, 0, 8, 8, 0, 0, 0, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 0,20,23,23,23,23,23,23,23,23,23, 0, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 0,20, 0, 0, 0, 0, 0, 0, 0,98,21, 0, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 8,20, 0, 0, 0, 0, 0, 0, 0, 0,21, 8, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 8,20, 0, 0, 0, 0, 0, 0, 0, 0,21, 8, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 0,20, 0, 0, 0, 0, 0, 0, 0, 0,21, 0, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 0,20, 0, 0, 0, 0, 0, 0, 0, 0,21, 0, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 8,20, 0, 0, 0, 0, 0, 0, 0, 0,21, 8, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 8,20, 0, 0, 0, 0, 0, 0, 0, 0,21, 8, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 0,20,97, 0, 0, 0, 0, 0, 0, 0,21, 0, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 0,22,22,22,22,22,22,22,22,22,21, 0, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 0, 0, 0, 8, 8, 0, 0, 8, 8, 0, 0, 0, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0 ],
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0 ],
[8, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0 ],
[98,0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0 ,0 ]]
 
#########################################################
class Node_Elem:
    """
    开放列表和关闭列表的元素类型，parent用来在成功的时候回溯路径
    """
    def __init__(self, parent, x, y, value,dist,action,isskip,skip_point):
        self.parent = parent
        self.x = x
        self.y = y
        self.value=value
        self.dist = dist
        self.action=action
        self.isskip=isskip
        self.skip_point=skip_point
        self.id=0  #id为1表示openset，id为-1表示closedset，id为0表示未拓展
        
class A_Star:
    """
    A星算法实现类
    """
    #注意w,h两个参数，如果你修改了地图，需要传入一个正确值或者修改这里的默认参数
    def __init__(self, s_x, s_y, e_x, e_y, w=20, h=20):
        self.s_x = 2
        self.s_y = 3
        self.e_x = 8
        self.e_y = 8        
        self.width = w
        self.height = h        
        self.open = []
        self.close = []
        self.path = []
        self.gridmap=[]
        self.init_gridmap()
    
    def init_gridmap(self):
        warmholes=[]
        self.width=gameMap.width
        self.height=gameMap.height
        print(self.width,self.height)
        for i in range(self.height):
            self.gridmap.append([])
            for j in range(self.width):
                p=Node_Elem(None,j,i,gameMap.map[i][j],0.0,0,0,None)
                if p.value>18:
                    p.isskip=True
                if p.value>24:
                    warmholes.append(p)
                self.gridmap[i].append(p) 

        for i in range(self.height):
            for j in range(self.width):
                #处理时空隧道
                if self.gridmap[i][j].isskip and self.gridmap[i][j].value<24:
                    cur=self.gridmap[i][j]   
                    while cur.isskip:
                        if cur.skip_point:
                            cur=cur.skip_point
                            break;
                        if 20==cur.value and cur.y-1>=0:
                            cur=self.gridmap[cur.y-1][cur.x]
                        elif 21==cur.value and cur.y+1<self.height:
                            cur=self.gridmap[cur.y+1][cur.x]
                        elif 22==cur.value and cur.x-1>=0:
                            cur=self.gridmap[cur.y][cur.x-1]   
                        elif 23==cur.value and cur.x+1<self.width:
                            cur=self.gridmap[cur.y][cur.x+1]
                    self.gridmap[i][j].skip_point=cur;
        print('test',self.gridmap[0][19].value)
        print('init grid map')
        for warmhole1 in warmholes:
            x1=warmhole1.x
            y1=warmhole1.y
            if self.gridmap[y1][x1].skip_point:
                    continue
            for warmhole2 in warmholes:
                x2=warmhole2.x
                y2=warmhole2.y
                if self.gridmap[y2][x2].skip_point:
                    continue
                if warmhole1.value==warmhole2.value and (x1!=x2 or y1!=y2):
                    self.gridmap[y1][x1].skip_point=self.gridmap[y2][x2]
                    self.gridmap[y2][x2].skip_point=self.gridmap[y1][x1]            
                    
    def resetmap(self):
        for i in range(self.height):
            for j in range(self.width):
                self.gridmap[i][j].parent=None
                self.gridmap[i][j].dist=10000
                self.gridmap[i][j].action=0
                self.gridmap[i][j].id=0
                self.open.clear()
                self.path.clear()
                self.close.clear()
             
    #查找路径的入口函数
    def find_path(self,s_x,s_y,e_x,e_y,name):
        self.resetmap()
        #构建开始节点  
        self.s_x=s_x
        self.s_y=s_y
        self.e_x=e_x
        self.e_y=e_y
        print(name,'find path',self.s_y,' ',self.s_x,'  ',self.e_y,'  ',self.e_x)
        if self.s_x==self.e_x and self.s_y==self.e_y:
            print(self.s_y,'arrive',self.s_x)
            return 0
        if self.gridmap[self.s_y][self.s_x].value==8 or self.gridmap[self.e_y][self.e_x].value==8:
            print('obstacle')
            return 0
        if self.gridmap[self.s_y][self.s_x].value<24 and self.gridmap[self.s_y][self.s_x].value>=20:
            print(self.s_y,'start tunnel',self.s_x)
            return 0
        if self.gridmap[self.e_y][self.e_x].value<24 and self.gridmap[self.e_y][self.e_x].value>=20:
            print(self.e_y,'end tunnel',self.e_x)
            return 0

        p=self.gridmap[self.s_y][self.s_x]
        while True:
            #扩展F值最小的节点
            self.extend_round(p,self.gridmap)
            #如果开放列表为空，则不存在路径，返回0，表示停止不动
            if not self.open:
                print('nopath')
                return 0
            #获取F值最小的节点
            idx, p = self.get_best()
            #找到路径，生成路径，返回
            if self.is_target(p):
                print(self.e_y,'find path',self.e_x)
                self.make_path(p)
                node=self.path[len(self.path)-1]
                return node.action
            #把此节点压入关闭列表，并从开放列表里删除
            self.close.append(p)
            del self.open[idx]
    
    def find_run_path(self,s_x,s_y,e_x,e_y,name,opps):
        self.resetmap()
        runMap = copy.deepcopy(self.gridmap)
        
        print("find_run_path!!!")
        for opp in opps:
            print("opp: ",opp)
            print("self: ",self.gridmap[opp[1]][opp[0]].value)
            print("runmap: ",runMap[opp[1]][opp[0]].value)# = 8
            runMap[opp[1]][opp[0]].value = 8
        print("176")
        #构建开始节点  
        self.s_x=s_x
        self.s_y=s_y
        self.e_x=e_x
        self.e_y=e_y
        print(name,'find path',self.s_y,' ',self.s_x,'  ',self.e_y,'  ',self.e_x)
        if self.s_x==self.e_x and self.s_y==self.e_y:
            print(self.s_y,'arrive',self.s_x)
            return 0
        if self.gridmap[self.s_y][self.s_x].value==8 or self.gridmap[self.e_y][self.e_x].value==8:
            print('obstacle')
            return 0
        if self.gridmap[self.s_y][self.s_x].value<24 and self.gridmap[self.s_y][self.s_x].value>=20:
            print(self.s_y,'start tunnel',self.s_x)
            return 0
        if self.gridmap[self.e_y][self.e_x].value<24 and self.gridmap[self.e_y][self.e_x].value>=20:
            print(self.e_y,'end tunnel',self.e_x)
            return 0
        print("195")

        p=self.gridmap[self.s_y][self.s_x]
        while True:
            #扩展F值最小的节点
            self.extend_round(p,runMap)
            #如果开放列表为空，则不存在路径，返回0，表示停止不动
            if not self.open:
                print('nopath')
                return 0
            #获取F值最小的节点
            idx, p = self.get_best()
            #找到路径，生成路径，返回
            if self.is_target(p):
                print(self.e_y,'find path',self.e_x)
                self.make_path(p)
                node=self.path[len(self.path)-1]
                return node.action
            #把此节点压入关闭列表，并从开放列表里删除
            self.close.append(p)
            del self.open[idx]
    

    def make_path(self,p):
        #从结束点回溯到开始点，开始点的parent == None
        while p.x!=self.s_x or p.y!=self.s_y:
            self.path.append(p)
            p = p.parent
            #print(p.x,p.y,p.action)
    #判断是否到达目的地    
    def is_target(self, i):
        return i.x == self.e_x and i.y == self.e_y
        
    def get_best(self):
        best = None
        bv = 1000000 #如果你修改的地图很大，可能需要修改这个值
        bi = -1
        for idx, i in enumerate(self.open):
            value = self.get_dist(i)#获取F值
            if value < bv:#比以前的更好，即F值更小
                best = i
                bv = value
                bi = idx
        return bi, best
        
    def get_dist(self, i):
        # F = G + H
        # G 为已经走过的路径长度， H为估计还要走多远
        # 这个公式就是A*算法的精华了。
        return i.dist + math.fabs(self.e_x-i.x)+ math.fabs(self.e_y-i.y)
        
    def extend_round(self, p, map_):
        #可以从5个方向走,上下左右停
        xs = (0, 0, -1, 1, 0)
        ys = (-1, 1, 0, 0, 0)
        for x, y in zip(xs, ys):
            if x==0 and y==0:
                action=0
            elif x==0 and y==-1:
                action=1
            elif x==0 and y==1:
                action=2
            elif x==-1 and y==0:
                action=3
            elif x==1 and y==0:
                action=4
            new_x, new_y = x + p.x, y + p.y
            #无效或者不可行走区域，则勿略
            if not self.is_valid_coord(new_x, new_y):
                continue
            #构造新的节点
            node=map_[new_y][new_x]
            if node.value==8:
                continue
            #新节点在关闭列表，则忽略
            #剔除掉关闭节点中的虫洞
            if node.id==-1 and node.value<24 :
                continue
            if node.isskip:
                node=node.skip_point
            if node.value==8 or node.id==-1:
                continue;
            #如果该节点已经在openset中
            if node.id==1:
                #新节点在开放列表
                if node.dist > p.dist+1:
                    #现在的路径到比以前到这个节点的路径更好~
                    #则使用现在的路径
                    node.parent = p
                    node.dist = p.dist+1
                    node.action=action
            #如果该节点第一次添加到openset中
            else:
                node.id=1
                node.parent=p
                node.dist=p.dist+1.0
                node.action=action
                self.open.append(node)
        
        
    def is_valid_coord(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return True
"""
def find_path(s_x,s_y,e_x,e_y):
    a_star = A_Star(s_x, s_y, e_x, e_y,20,20)
    a_star.resetmap()
    a_star.find_path(2,3,8,8)
"""    
"""
"if __name__ == ""__main__:"
if 1:
    #把字符串转成列表
    print('test')        
    find_path(0,0,19,19)
    print('test')
"""