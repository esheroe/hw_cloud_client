# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 14:04:34 2019

@author: GP63
"""
#from ballclient.service.Log import logger

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

class StateMachine:
    def __init__(self): 
        self.handlers = {}        # 状态转移函数字典
        self.startState = None    # 初始状态
        self.endStates = []       # 最终状态集合
        self.handler = 0          # 状态转移函数
        self.nowState   = None
        '''
        
        '''
        self.transation = {}
    
    # 参数name为状态名,handler为状态转移函数,end_state表明是否为最终状态
    def add_state(self, name, handler, end_state=0):
        name = name.upper() # 转换为大写
        self.handlers[name] = handler
        if end_state:
            self.endStates.append(name)

    def set_start(self, name):
        self.startState = name.upper()
        self.nowState = name.upper()

    def run(self, newTrans):
        if self.nowState == self.startState:
            try:
                self.handler = self.handlers[self.startState]
            except:
                raise InitializationError("must call .set_start() before .run()")
            if not self.endStates:
                raise  InitializationError("at least one state must be an end_state")
        
        # 从Start状态开始进行处理
        '''
        while True: 
            (newState, cargo) = handler(cargo)     # 经过状态转移函数变换到新状态
            if newState.upper() in self.endStates: # 如果跳到终止状态,则打印状态并结束循环
                print("reached ", newState)
                break 
            else:                        # 否则将转移函数切换为新状态下的转移函数 
                handler = self.handlers[newState.upper()] 
        '''
 
        #newTrans = newTrans     # 经过状态转移函数变换到新状态
        newState = self.handler(newTrans)
        self.nowState = newState
        #logger.info("nowState: %s",self.nowState)
        #print("startState",self.startState)
        if newState.upper() in self.endStates: # 如果跳到终止状态,则打印状态并结束循环
            #logger.ferror("reached ", newState, " Trans: ",newTrans)
            #logger.ferror("return to ",self.startState)
            self.nowState = self.startState
             
        else:                        # 否则将转移函数切换为新状态下的转移函数 
            self.handler = self.handlers[newState.upper()]



'''
class Transition:
    def __init__(self):
        self.N = 0
        self.P = 1
        self.SEE = 2
        self.BIGFISH = 16
        
class State:
    def __init__(self):
        self.START = "START_STATE"
        self.RUNAWAY = "RUNAWAY_STATE"
        self.SEARCH = "SEARCH_STATE"
        self.CATCH = "CATCH"

t = Transition()
s = State()
def origin_trans(txt):
    txt = txt & 0x0f
    if(txt == t.P):
        newState = s.SEARCH
    elif(txt == t.N):
        newState = s.SEARCH
    elif(txt == t.SEE):
         newState = s.RUNAWAY
    elif(txt == t.P | t.SEE):
        newState = s.SEARCH
    else:
        newState = "error_state"
    print("origin state->",newState)
    return newState

#search score state
def sss_trans(txt):  
    txt_l = txt & 0x0f
    if(txt == t.P | t.BIGFISH | t.SEE):
        newState = s.CATCH
    elif(txt_l == t.N):
        newState = s.SEARCH
    elif(txt_l == t.SEE):
         newState = s.RUNAWAY
    elif(txt_l == t.P | t.SEE):
        newState = s.SEARCH
    else:
        newState = "error_state"
    print("search_score_state->",newState)
    return newState

def rw_trans(txt):
    txt_l = txt & 0x0f
    if(txt == t.P | t.BIGFISH | t.SEE):
        newState = s.CATCH
    elif(txt_l == t.N):
        newState = s.SEARCH
    elif(txt_l == t.SEE):
         newState = s.RUNAWAY
    elif(txt_l == t.P | t.SEE):
        newState = s.SEARCH
    else:
        newState = "error_state"
    print("run_away_state->",newState)

    return newState

def c_trans(txt):
    txt_l = txt & 0x0f
    if(txt == t.P | t.BIGFISH | t.SEE):
        newState = s.CATCH
    elif(txt_l == t.N):
        newState = s.SEARCH
    elif(txt_l == t.SEE):
         newState = s.RUNAWAY
    elif(txt_l == t.P | t.SEE):
        newState = s.SEARCH
    else:
        newState = "error_state"
    print("catch_state->",newState)

    return newState
        

    

if __name__== "__main__":
    m = StateMachine()
    m.add_state(s.START,origin_trans)
    m.add_state(s.SEARCH,sss_trans)
    m.add_state(s.RUNAWAY,rw_trans)
    m.add_state(s.CATCH,c_trans)
    m.add_state("error_state", None, end_state=1)
    
    m.set_start(s.START) # 设置开始状态
    m.run(0)
    m.run(t.SEE)
'''
