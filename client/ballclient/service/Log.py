# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 11:19:40 2019

@author: GP63
"""
import os
import logging
import sys


# 单例模式
#logger = spider_log(log_name='test')
class Log:
        
    def __init__(self,log_name,level=logging.INFO):
        '''
        self.file_folder = './LOG/'
        if not os.path.exists(self.file_folder):
            os.mkdir(self.file_folder)
        '''
            
            # 创建一个logger
        #self.printf = logging.getLogger(log_name+'_')
        self.print  = logging.getLogger(log_name)
        self.logname = log_name + '.log'
        
        # 设置日志级别
        self.print.setLevel(level)
        self.level = level
        

        # 创建文件处理器
        '''
        file_handler = logging.FileHandler(self.file_folder+'/'+self.logname+'.txt','w')
        file_handler.setLevel(logging.DEBUG)   
        
        self.fh = logging.FileHandler(self.file_folder+'/'+self.logname+'.txt','a')
        self.fh.setLevel(level)   
        '''

        
            # 创建输出处理器
        self.stream_handler = logging.StreamHandler()
        
        # 定义输出格式
        self.formatter = logging.Formatter('[%(levelname)s] : %(message)s')
        #file_handler.setFormatter(self.formatter)
        #self.fh.setFormatter(self.formatter)
        self.stream_handler.setFormatter(self.formatter)
        
            # 给logger添加处理器
        #self.printf.addHandler(file_handler)
        self.print.addHandler(self.stream_handler)
        #self.logger.debug("Begin!")
        
        #初始化文件
        with open('./'+self.logname,'w') as f:
            print("Begin!")
    
    
    def setLevel(self,level):
        self.level = level
        self.print.setLevel(level)
        
    def setFLevel(self,flevel):
        self.level = flevel
        
    def info(self,msg,*args,**kargs):
        self.print.addHandler(self.stream_handler)
        self.print.info(msg,*args,**kargs)
        #logging.info(msg,*args,**kargs)
        self.print.removeHandler(self.stream_handler)
        
    def warning(self,msg,*args,**kargs):
        self.print.addHandler(self.stream_handler)
        self.print.warning(msg,*args,**kargs)
        self.print.removeHandler(self.stream_handler)
        
    def error(self,msg,*args,**kargs):
        self.print.addHandler(self.stream_handler)
        self.print.error(msg,*args,**kargs)
        self.print.removeHandler(self.stream_handler)        
    
    def finfo(self,msg,*args,**kargs):
        if self.level <= logging.INFO:
            with open('./'+self.logname,'a+') as f:
                print("[INFO] ",msg,*args,**kargs,file=f)
        
    def fwarning(self,msg,*args,**kargs):
        if self.level <= logging.WARNING:
            with open('./'+self.logname,'a+') as f:
                print("[WARN] ",msg,*args,**kargs,file=f)        
        
    def ferror(self,msg,*args,**kargs):
        if self.level <= logging.ERROR:
            with open('./'+self.logname,'a+') as f:
                print("[ERROR] ",msg,*args,**kargs,file=f)
logger = Log('log')

if __name__ == '__main__':
    logger = Log('log')
    #logger = l.getLog()
    a = [1,2,3]
    logger.info('warn message %s', a)
    logger.warning('info message')
    
    logger.fwarning('info message')
    logger.finfo('warn meesage %s',a)

    
    logger.setLevel(logging.FATAL)
    logger.warning('warn message')
    logger.info('info message')
    
    logger.finfo('warn meesage %s',a)
    logger.fwarning('info message')
   
def function():
    print(sys._getframe().f_code.co_filename)  #当前位置所在的文件名
    print(sys._getframe().f_code.co_name)      #当前位置所在的函数名
    print(sys._getframe().f_lineno)            #当前位置所在的行号 

function()
    
        
        
        