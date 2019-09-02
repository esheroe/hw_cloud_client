# encoding:utf8
#import numpy as np
import copy
#import matplotlib.pyplot as plt
import ballclient.service.constants as constants
from ballclient.service.Log import logger

'''
* 全局地图
* 1、因为涉及到类之间的交互，
* 2、当搜集到得分点后，需要管理得分点的坐标，全局地图只展示地图信息
* 3、全局地图中维护一个动态地图，作为场地当前信息
* 4、全局地图只有一个，因此使用单例


0：地图可行区域
1 - 5：分数奖励
10 - 17：player信息
8：障碍物 
虫洞id的ascii码：表示虫洞对
20 - 23表示滑梯的上下左右
'''
class GameMap(object):

    def __init__(self):

        self.height  = 0
        self.width   = 0
        self.map     = 0
        self.map2    = 0
        
        #[score1,x1,y1],[score2,x2,y2]
        self.powers  = []
        self.curpowers = []
        
        #{name:[[x1,y1],[x2,y2]]}
        #{97: [[6, 13], [19, 0]], 98: [[0, 19], [13, 6]]}
        self.wormholePair = {}
        
        #[[direct, x, y], [direct, x, y]]
        #[[20, 5, 5], [23, 6, 5]
        self.tunnels = []
        
        self.ourCurrentPlayer = []
        self.ourPlayer    = []#[0,1,2,3] or [4,5,6,7]
        
        #当前看到的敌人           [id x, y score]
        self.oppPlayer    = []#[[4, 5, 4, 2], [6, 5, 5, 2], [7, 5, 5, 2]]
        
        self.vision       = 0
        self.roundID      = 0
        self.ourMode      = 0   #表示我方能力 think，beat
        self.currentMode  = 0   #表示当前优势能力 think，beat
        
        #子图的中点坐标[[x1,y1],[x2,y2] ... ]
        self.subMap       = []
        self.leg          = 0   #表示第几个回合
        
    def printAll(self):
        print ('h:',self.height,'w:',self.width)
        print ('powers: ',self.powers)
        print ('wormholePair: ',self.wormholePair)
        print ('tunnels: ', self.tunnels)
        print ('ourPlayer: ', self.ourPlayer)
        print ('vision: ', self.vision)
        print ('roundID: ', self.roundID)
        print ('isourPower? ', self.isOurPower())
        print ('oppPlayer: ', self.oppPlayer)
        print ('ourCurrentPlayer: ', self.ourCurrentPlayer)
 
    '''处理leg_start消息'''
    def handleMsg(self, msg):

        '''初始化地图'''
        self.width  = msg['msg_data']['map']['width']
        self.height = msg['msg_data']['map']['height']
        self.map    = [[0 for col in range(self.width)] for row in range(self.height)]
        self.map2   = [[0 for col in range(self.width)] for row in range(self.height)]

        self.vision = msg['msg_data']['map']['vision']
        

        '''生成陨石坐标'''
        meteor = msg['msg_data']['map']['meteor']
        for dic in meteor:
            y = 0
            x = 0
            for k,v in dic.items():
                if(k=='y'):
                    y = v
                if(k=='x'):
                    x = v
            self.map[y][x] = 8 
        
        '''tunnel坐标'''
        tunnels = msg['msg_data']['map']['tunnel']
        for tunnel in tunnels:
            if tunnel['direction'] == 'up':
                d = 20
            if tunnel['direction'] == 'down':
                d = 21          
            if tunnel['direction'] == 'left':
                d = 22            
            if tunnel['direction'] == 'right':
                d = 23
            
            self.map[tunnel['y']][tunnel['x']] = d
            self.tunnels.append([d,tunnel['x'],tunnel['y']])

        
                    
        '''wormhole坐标'''
        wormhole = msg['msg_data']['map']['wormhole']
        wh = []
        for dic in wormhole:
            temp = []
            x = 0
            y = 0
            name = 0
            for k,v in dic.items():
                if(k=='y'):
                    y = v
                elif(k=='x'):
                    x = v
                else:
                    name = ord(v.lower())
            
            if len(wh):
                for l in wh:
                    if(l[0] == name):
                        self.map[y][x] = l[0]
                        self.map[l[1]][l[2]] = l[0]
                        self.wormholePair[l[0]] = [[x,y],[l[2],l[1]]]
                        wh.remove(l)
                    else:
                        temp = [name,y,x]
            else:
                wh.append([name,y,x])
            if len(temp):
                wh.append(temp)

        
        #ourplayer = []
        '''ourplayer info'''
        teams = msg['msg_data']['teams']
        for team in teams:
            if team['id'] == constants.team_id:
                self.ourPlayer = team['players']
                self.ourMode   = team['force']
                
        '''生成子图中心'''
        lux = int((self.width+4-1)/4) #left up x 向上取整除法
        luy = int((self.height+4-1)/4)#left up y
        self.subMap = [[lux,luy],[lux,luy*3],[lux*3,luy],[lux*3,luy*3]]

                
                    
    '''更新地图消息'''
    def updateMsg(self, msg):
        self.map2 = copy.deepcopy(self.map)
        self.oppPlayer.clear()
        self.ourCurrentPlayer.clear()
        self.curpowers.clear()
        
        '''round 必有的信息'''
        self.currentMode = msg['msg_data']['mode']
        self.roundID     = msg['msg_data']['round_id']
        
        try:
            '''power坐标'''
            powers = msg['msg_data']['power']
            for power in powers:
                l = [power['point'],power['x'],power['y']]
                cl= [power['point'],power['x'],power['y']]
                self.map2[power['y']][power['x']] = power['point']
                self.curpowers.append(cl)
                if l not in self.powers:
                    self.powers.append(l)
           # print(self.powers)
        except:
            pass
        
        try:
            '''player坐标'''
            players = msg['msg_data']['players']
            for player in players:
                self.map2[player['y']][player['x']] = player['id']+10
                if player['team'] != constants.team_id: 
                    opp = [player['id'],player['x'],player['y'],player['score']]
                    self.oppPlayer.append(opp)
                else:
                    our = [player['id'],player['x'],player['y']]
                    self.ourCurrentPlayer.append(our)
            #print (self.oppPlayer)
        except:
            pass     
    
    def isOurPower(self):
        return self.currentMode == self.ourMode
gameMap = GameMap()
'''
if __name__ == '__main__':
    round_msg = {"msg_data":{"mode":"think","players":[{"id":4,"score":2,"sleep":0,"team":1112,"x":13,"y":7},{"id":5,"score":6,"sleep":0,"team":1112,"x":13,"y":2},{"id":6,"score":4,"sleep":0,"team":1112,"x":1,"y":13},{"id":7,"score":4,"sleep":0,"team":1112,"x":17,"y":4}],"power":[{"point":1,"x":12,"y":2},{"point":1,"x":16,"y":2},{"point":1,"x":17,"y":3},{"point":1,"x":10,"y":8},{"point":2,"x":11,"y":8},{"point":5,"x":10,"y":9},{"point":1,"x":11,"y":9},{"point":1,"x":2,"y":12},{"point":1,"x":2,"y":16}],"round_id":146,"teams":[{"id":1111,"point":24,"remain_life":4},{"id":1112,"point":16,"remain_life":4}]},"msg_name":"round"}
    start_msg  = {"msg_data":{"map":{"height":20,"meteor":[{"x":18,"y":1},{"x":19,"y":1},{"x":7,"y":4},{"x":8,"y":4},{"x":11,"y":4},{"x":12,"y":4},{"x":4,"y":7},{"x":15,"y":7},{"x":4,"y":8},{"x":15,"y":8},{"x":4,"y":11},{"x":15,"y":11},{"x":4,"y":12},{"x":15,"y":12},{"x":7,"y":15},{"x":8,"y":15},{"x":11,"y":15},{"x":12,"y":15},{"x":0,"y":18},{"x":1,"y":18}],"tunnel":[{"direction":"up","x":5,"y":5},{"direction":"right","x":6,"y":5},{"direction":"right","x":7,"y":5},{"direction":"right","x":8,"y":5},{"direction":"right","x":9,"y":5},{"direction":"right","x":10,"y":5},{"direction":"right","x":11,"y":5},{"direction":"right","x":12,"y":5},{"direction":"right","x":13,"y":5},{"direction":"right","x":14,"y":5},{"direction":"up","x":5,"y":6},{"direction":"down","x":14,"y":6},{"direction":"up","x":5,"y":7},{"direction":"down","x":14,"y":7},{"direction":"up","x":5,"y":8},{"direction":"down","x":14,"y":8},{"direction":"up","x":5,"y":9},{"direction":"down","x":14,"y":9},{"direction":"up","x":5,"y":10},{"direction":"down","x":14,"y":10},{"direction":"up","x":5,"y":11},{"direction":"down","x":14,"y":11},{"direction":"up","x":5,"y":12},{"direction":"down","x":14,"y":12},{"direction":"up","x":5,"y":13},{"direction":"down","x":14,"y":13},{"direction":"left","x":5,"y":14},{"direction":"left","x":6,"y":14},{"direction":"left","x":7,"y":14},{"direction":"left","x":8,"y":14},{"direction":"left","x":9,"y":14},{"direction":"left","x":10,"y":14},{"direction":"left","x":11,"y":14},{"direction":"left","x":12,"y":14},{"direction":"left","x":13,"y":14},{"direction":"down","x":14,"y":14},{"direction":"left","x":8,"y":16},{"direction":"left","x":9,"y":16},{"direction":"left","x":10,"y":16}],"vision":3,"width":20,"wormhole":[{"name":"A","x":19,"y":0},{"name":"b","x":13,"y":6},{"name":"a","x":6,"y":13},{"name":"B","x":0,"y":19}]},"teams":[{"force":"beat","id":1111,"players":[0,1,2,3]},{"force":"think","id":1112,"players":[4,5,6,7]}]},"msg_name":"leg_start"}

    m = GameMap()
    m.handleMsg(start_msg)
    m.updateMsg(round_msg)
    m.printAll()
    plt.figure('map2')
    plt.imshow(m.map2)
    plt.figure('map')
    plt.imshow(m.map)
'''