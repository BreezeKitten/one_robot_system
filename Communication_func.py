# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 21:44:46 2020

@author: BreezeCat
"""

import socket
import json
import threading


Doki_msg = json.dumps({'header':'Doki'})

class Subscriber:
    def __init__(self, host, port, cb_func=None):
        self.connect_info = (host,port)
        self.callback = cb_func
        self.connect_flag = False
    
    def connect(self):
        self.socket = socket.socket()
        retry = 0
        while(retry<100):
            retry += 1
            try:
                self.socket.connect(self.connect_info)
                self.connect_flag = True
                print('connect success!')
                break
            except:                
                print('connect error! retry:', retry)
    
    def disconnect(self):
        self.socket.close()
        self.connect_flag = False
        print('disconnect!')        
        
    def start_callback(self):
        if self.connect_flag == False:
            print('still not connect!')
        else:
            self.callback_flag = True
            self.socket.settimeout(3)
            while(self.callback_flag):
                try:
                    raw_data = self.socket.recv(4096).decode()
                    if raw_data == '':
                        print('empty data, close connect!')
                        self.callback_flag = False
                    else:
                        data = json.loads(raw_data)
                        if 'header' in data:
                            if data['header'] == 'Doki':
                                print('still alive!')
                                self.socket.send(b'alive')
                            elif data['header'] == 'Message':
                                self.callback(data)
                            else:
                                print('header error!')
                        else:
                            print('no header in data!')
                except:
                    continue
            self.disconnect()
    
    def background_callback(self):
        t = threading.Thread(target=self.start_callback)
        t.start()
        return t
    
        
class Publisher:
    def __init__(self, host, port, cb_func=None):
        self.connect_info = (host,port)
        self.callback = cb_func

    def set_pub(self):
        self.socket = socket.socket()
        self.socket.bind(self.connect_info)        
        self.socket.listen(5)
                
    def accept_connect(self):
        self.c, self.addr = self.socket.accept()     # 建立客户端连接
        print('连接地址：', self.addr)
        self.receive_msg()
        return        
        
    def wait_connect(self):
        t = threading.Thread(target=self.accept_connect)
        t.start()
        return t
    
    def publish_msg(self, msg):
        self.socket.settimeout(3)
        self.c.send(msg.encode())
        self.socket.settimeout(None)
        
    def receive_msg(self):
        while True:
            raw_data = self.c.recv(4096).decode()
            if not raw_data:
                print('disconnect!')
                self.c.shutdown(2)
                break
            try:
                data = json.loads(raw_data)
                if 'header' in data:
                    if data['header'] == 'Message':
                        if self.callback != None:
                            self.callback(data)
                        else:
                            print('no callback func')
                            print('receive data: ',data)
                    else:
                        print('header error!')
                else:
                    print('no header in data!')
            except Exception as e:
                print('except error:', e)
                continue                
        

        
