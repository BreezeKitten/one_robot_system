# -*- coding: utf-8 -*-
"""
Created on Sun Sep 13 21:44:46 2020

@author: BreezeCat
"""

import socket
import json
import threading
import struct


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
        self.socket.shutdown(2)
        self.socket.close()
        self.connect_flag = False
        print('disconnect!')
        return
    
    def send_msg(self, msg):
        jmsg = json.dumps(msg)
        if self.socket:
            frmt = "=%ds" % len(jmsg)
            packed_msg = struct.pack(frmt, bytes(jmsg, 'ascii'))
            packed_hdr = struct.pack('!I', len(packed_msg))
            self._send(packed_hdr)
            self._send(packed_msg)
    
    def _send(self, msg):
        sent = 0
        while sent < len(msg):
            sent += self.socket.send(msg[sent:])
    
    def _read(self, size):
        data = b''
        while len(data) < size:
            data_tmp = self.socket.recv(size-len(data))
            data += data_tmp
            if data_tmp == b'':
                self.callback_flag = False
                raise RuntimeError('socket connection broken')
        return data
    
    def _msg_length(self):
        d = self._read(4)
        s = struct.unpack('!I', d)
        return s[0]
    
    def read_msg(self):
        size = self._msg_length()
        data = self._read(size)
        frmt = "=%ds" % size
        msg = struct.unpack(frmt, data)
        return json.loads(str(msg[0]), 'ascill')
        
    def start_callback(self):
        if self.connect_flag == False:
            print('still not connect!')
        else:
            self.callback_flag = True
            self.socket.settimeout(3)
            while(self.callback_flag):
                try:
                    data = self.read_msg()
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
                except Exception as e:
                    print('except error:', e)
                    continue 
            self.disconnect()
        return
    
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

    def send_msg(self, msg):
        jmsg = msg  #the msg has been json
        if self.socket:
            frmt = "=%ds" % len(msg)
            packed_msg = struct.pack(frmt, bytes(jmsg, 'ascii'))
            packed_hdr = struct.pack('!I', len(packed_msg))
            self._send(packed_hdr)
            self._send(packed_msg)
    
    def _send(self, msg):
        sent = 0
        while sent < len(msg):
            sent += self.socket.send(msg[sent:])
    
    def _read(self, size):
        data = b''
        while len(data) < size:
            data_tmp = self.socket.recv(size-len(data))
            data += data_tmp
            if data_tmp == b'':
                self.callback_flag = False
                raise RuntimeError('socket connection broken')
        return data
    
    def _msg_length(self):
        d = self._read(4)
        s = struct.unpack('!I', d)
        return s[0]
    
    def read_msg(self):
        size = self._msg_length()
        data = self._read(size)
        frmt = "=%ds" % size
        msg = struct.unpack(frmt, data)
        return json.loads(str(msg[0]), 'ascill')
    
    def publish_msg(self, msg): #Keep the interface for small code modify
        self.send_msg(msg)
        
    def receive_msg(self):
        while True:
            try:
                self.socket.settimeout(3)
                data = self.read_msg()
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
                print('Pub recv except error:', e)
                continue                
        

        
