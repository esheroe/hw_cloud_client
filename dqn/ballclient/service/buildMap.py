# encoding:utf8
import numpy as np
import matplotlib.pyplot as plt
import ballclient.service.constants as constants

class GameMap():
    def __init__(self):
        '''地图最大为25*25,使用最大地图'''
        self.h  = 30
        self.w   = 30
        self.paddedmap = 50*np.ones((self.h,self.w)) # 全部填充为陨石坐标
 
    '''处理leg_start消息'''
    def handleMsg(self, msg):
        '''初始化地图'''
        self.height = msg['msg_data']['map']['height']
        self.width  = msg['msg_data']['map']['width']
        self.dh = self.h - self.height # 尺寸差值
        self.dw = self.w - self.width  # 尺寸差值
        self.golbalmap = np.zeros((self.height,self.width))
        
        '''生成陨石坐标'''
        meteors = msg['msg_data']['map']['meteor']
        for meteor in meteors:
            self.golbalmap[meteor['y']][meteor['x']] = 50
        
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
            self.golbalmap[tunnel['y']][tunnel['x']] = d
                    
        '''wormhole坐标'''
        wormholes = msg['msg_data']['map']['wormhole']
        for wormhole in wormholes:
            self.golbalmap[wormhole['y']][wormhole['x']] = ord(wormhole['name'].lower())
                    
    '''更新地图消息'''
    def updateMsg(self, msg):
        self.map = self.golbalmap.copy()
        try:
            '''power坐标'''
            powers = msg['msg_data']['power']
            for power in powers:
                self.map[power['y']][power['x']] = power['point']
        except:
            pass
        
        try:
            '''player坐标'''
            players = msg['msg_data']['players']
            for player in players:
                if player['team'] == constants.team_id: # 我方玩家
                    self.map[player['y']][player['x']] = 40
                else: # 敌方玩家
                    self.map[player['y']][player['x']] = 80 # 修改此处编码，需要同步修改service里的死亡玩家处理部分
        except:
            pass
        
        # padding map
        self.paddedmap[self.dh//2:(self.dh//2 + self.height), self.dw//2:(self.dw//2 + self.width)] = self.map
        
if __name__ == '__main__':
    round_msg = {"msg_data":{"mode":"think","players":[{"id":4,"score":2,"sleep":0,"team":1112,"x":13,"y":7},{"id":5,"score":6,"sleep":0,"team":1112,"x":13,"y":2},{"id":6,"score":4,"sleep":0,"team":1112,"x":1,"y":13},{"id":7,"score":4,"sleep":0,"team":1112,"x":17,"y":4}],"power":[{"point":1,"x":12,"y":2},{"point":1,"x":16,"y":2},{"point":1,"x":17,"y":3},{"point":1,"x":10,"y":8},{"point":2,"x":11,"y":8},{"point":5,"x":10,"y":9},{"point":1,"x":11,"y":9},{"point":1,"x":2,"y":12},{"point":1,"x":2,"y":16}],"round_id":146,"teams":[{"id":1111,"point":24,"remain_life":4},{"id":1112,"point":16,"remain_life":4}]},"msg_name":"round"}
    start_msg  = {"msg_data":{"map":{"height":20,"meteor":[{"x":18,"y":1},{"x":19,"y":1},{"x":7,"y":4},{"x":8,"y":4},{"x":11,"y":4},{"x":12,"y":4},{"x":4,"y":7},{"x":15,"y":7},{"x":4,"y":8},{"x":15,"y":8},{"x":4,"y":11},{"x":15,"y":11},{"x":4,"y":12},{"x":15,"y":12},{"x":7,"y":15},{"x":8,"y":15},{"x":11,"y":15},{"x":12,"y":15},{"x":0,"y":18},{"x":1,"y":18}],"tunnel":[{"direction":"up","x":5,"y":5},{"direction":"right","x":6,"y":5},{"direction":"right","x":7,"y":5},{"direction":"right","x":8,"y":5},{"direction":"right","x":9,"y":5},{"direction":"right","x":10,"y":5},{"direction":"right","x":11,"y":5},{"direction":"right","x":12,"y":5},{"direction":"right","x":13,"y":5},{"direction":"right","x":14,"y":5},{"direction":"up","x":5,"y":6},{"direction":"down","x":14,"y":6},{"direction":"up","x":5,"y":7},{"direction":"down","x":14,"y":7},{"direction":"up","x":5,"y":8},{"direction":"down","x":14,"y":8},{"direction":"up","x":5,"y":9},{"direction":"down","x":14,"y":9},{"direction":"up","x":5,"y":10},{"direction":"down","x":14,"y":10},{"direction":"up","x":5,"y":11},{"direction":"down","x":14,"y":11},{"direction":"up","x":5,"y":12},{"direction":"down","x":14,"y":12},{"direction":"up","x":5,"y":13},{"direction":"down","x":14,"y":13},{"direction":"left","x":5,"y":14},{"direction":"left","x":6,"y":14},{"direction":"left","x":7,"y":14},{"direction":"left","x":8,"y":14},{"direction":"left","x":9,"y":14},{"direction":"left","x":10,"y":14},{"direction":"left","x":11,"y":14},{"direction":"left","x":12,"y":14},{"direction":"left","x":13,"y":14},{"direction":"down","x":14,"y":14},{"direction":"left","x":8,"y":16},{"direction":"left","x":9,"y":16},{"direction":"left","x":10,"y":16}],"vision":3,"width":20,"wormhole":[{"name":"A","x":19,"y":0},{"name":"b","x":13,"y":6},{"name":"a","x":6,"y":13},{"name":"B","x":0,"y":19}]},"teams":[{"force":"beat","id":1111,"players":[0,1,2,3]},{"force":"think","id":1112,"players":[4,5,6,7]}]},"msg_name":"leg_start"}

    m = GameMap()
    m.handleMsg(start_msg)
    m.updateMsg(round_msg)
    plt.figure()
    plt.imshow(m.golbalmap)
    plt.figure()
    plt.imshow(m.map)
    plt.figure()
    plt.imshow(m.paddedmap)
    plt.show()