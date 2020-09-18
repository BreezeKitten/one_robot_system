# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 16:56:49 2020

@author: BreezeCat
"""

import json
import Agent
import Communication_func as Comm
import time


A = Agent.Agent('A', -3, 1, 0, 0, 0, 0.2, 3, -1, 0, 1, mode = 'Greedy')
B = Agent.Agent('B', -3, -1, 0, 0, 0, 0.2, 3, 1, 0, 1, mode = 'Greedy')
C = Agent.Agent('C', 3, 1, 3.14, 0, 0, 0.2, -3, -1, 3.14, 1, mode = 'Greedy')
D = Agent.Agent('D', 3, -1, 3.14, 0, 0, 0.2, -3, 1, 3.14, 1, mode = 'Greedy')
data = {}
data['main_agent_name'] = 'A'
data['agent_num'] = 4
data['Agent_data'] = []
data['Agent_data'].append(A.Transform_to_Dict())
data['Agent_data'].append(B.Transform_to_Dict())
data['Agent_data'].append(C.Transform_to_Dict())
data['Agent_data'].append(D.Transform_to_Dict())
data['header'] = 'Message'
jdata = json.dumps(data)


def PD(data):
    print(data, time.time())

pub = Comm.Publisher('127.0.0.1',12345)
pub.set_pub()
pub.wait_connect()

OP = input('Command: ')
while(OP != 'Stop'):
    if OP == 'Connect':
        sub = Comm.Subscriber('127.0.0.1',12346, cb_func=PD)
        sub.connect()
        t = sub.background_callback()
    if OP == 'Pub':
        pub.publish_msg(jdata)
    if OP == 'contin':
        for i in range(100):
            pub.publish_msg(jdata)
            time.sleep(0.1)
    OP = input('Command: ')