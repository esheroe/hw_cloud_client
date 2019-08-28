# encoding:utf8
'''
业务方法模块，需要选手实现

选手也可以另外创造模块，在本模块定义的方法中填入调用逻辑。这由选手决定

所有方法的参数均已经被解析成json，直接使用即可

所有方法的返回值为dict对象。客户端会在dict前面增加字符个数。
'''
import ballclient.service.constants as constants
from ballclient.service.GameMap import gameMap as gameMap
from ballclient.service.AI import Team
from ballclient.service.Log import logger

#import random

def leg_start(msg):
    '''
    :param msg:
    :return: None
    '''
    gameMap.leg += 1
    print("round start no ", gameMap.leg)
    gameMap.handleMsg(msg)
    
    for i in range(len(gameMap.map)):
        print (gameMap.map[i])
        logger.finfo(gameMap.map[i])
        
    global moyu
    moyu=Team()
    
def leg_end(msg):
    '''

    :param msg:
    {
        "msg_name" : "leg_end",
        "msg_data" : {
            "teams" : [
            {
                "id" : 1001,				#队ID
                "point" : 770             #本leg的各队所得点数
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
    print("round over")
    # teams = msg["msg_data"]['teams']
    # for team in teams:
        # print("teams:%s" % team['id'])
        # print("point:%s" % team['point'])
        # print("\n\n")


def game_over(msg):
    gameMap.printAll()
    print("game over!")


def round(msg):
    '''
    :param msg: dict
    :return:
    return type: dict
    '''
    #print("round")
 
    gameMap.updateMsg(msg)
    round_id = int(msg['msg_data']['round_id'])
    players = msg['msg_data']['players']
    print('        ########',round_id,'#########   ')
    logger.fwarning('        ########',round_id,'#########   ')
    direction = {0:'',1: 'up', 2: 'down', 3: 'left', 4: 'right'}
    result = {
        "msg_name": "action",
        "msg_data": {
            "round_id": round_id
        }
    }
    action = []
    moves = []
    moves.clear()
    moves=moyu.process()
    # print "神秘代码：临兵斗者皆阵列前行"
    if moyu.stupid.isvalid:
        action.append({"team": constants.team_id, "player_id": gameMap.ourPlayer[0],
                   "move": [direction[moves[0]]]})
    if moyu.idiot.isvalid:
        action.append({"team": constants.team_id, "player_id": gameMap.ourPlayer[1],
                   "move": [direction[moves[1]]]})
    if moyu.fool.isvalid:
        action.append({"team": constants.team_id, "player_id": gameMap.ourPlayer[2],
                   "move": [direction[moves[2]]]})
    if moyu.git.isvalid:
        action.append({"team": constants.team_id, "player_id": gameMap.ourPlayer[3],
                   "move": [direction[moves[3]]]})
    result['msg_data']['actions'] = action
    return result

