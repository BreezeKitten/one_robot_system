# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 15:17:56 2020

@author: BreezeCat
"""

import sys
import json
import random
import numpy as np
import math
import datetime
import copy
import os
import Agent
import numpy_Network as Network
import Combination
import Communication_func as Comm
import time
import multiprocessing as mp

color_list = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

####
#Common parameter
####
PI = math.pi
resX = 0.1 # resolution of X
resY = 0.1 # resolution of Y
resTH = PI/15
LOG_DIR = 'logs/Multi_test'
SOME_TAG = '_test4'

####
#Reward
####
Arrived_reward = 1
Time_out_penalty = -0.25
Collision_high_penalty = -0.5
Collision_low_penalty = -1
Collision_equ_penalty = -0.75


'''
Motion Parameter
'''
deltaT = 0.1            #unit:s
V_max = 3               #m/s
W_max = 1#2               #rad/s
linear_acc_max = 10     #m/s^2
angular_acc_max = 7     #rad/s^2
size_min = 0.1          #unit:m
x_upper_bound = 5       #unit:m
x_lower_bound = -5      #unit:m
y_upper_bound = 5       #unit:m
y_lower_bound = -5      #unit:m
TIME_OUT_FACTOR = 4



Network_Path_Dict = {'2':'Network/2_robot_network/gamma09_95_0429/two.json', 
                     '3':'Network/3_robot_network/0826_933/three.json'}



    
def Build_network(robot_num, base_network_path):
    N = Network.Network_Dict[str(robot_num)]()
    N.load_parameter(base_network_path)  
    return N

def Build_all_Network(path_dict):
    global Network_Dict
    for item in path_dict:
        Network_Dict[item] = Build_network(int(item), path_dict[item])

def Calculate_distance(x1, y1, x2, y2):
    return np.sqrt(math.pow( (x1-x2) , 2) + math.pow( (y1-y2) , 2))

def Check_Collision(agent1, agent2):
    distance = Calculate_distance(agent1.state.Px, agent1.state.Py, agent2.state.Px, agent2.state.Py)
    if (distance <= (agent1.state.r + agent2.state.r)):
        return True
    else:
        return False

def Check_Goal(agent, position_tolerance, orientation_tolerance):    
    position_error = Calculate_distance(agent.state.Px, agent.state.Py, agent.gx, agent.gy)
    orientation_error = abs(agent.state.Pth - agent.gth)
    if (position_error < position_tolerance) and (orientation_error < orientation_tolerance):
        return True
    else:
        return False

def Predict_action_value(main_agent, Agent_Set, V_pred, W_pred, base_network, Network_Dict):
    Other_Set, Value_list = [], []
    network = Network_Dict[str(base_network)]
    VO_flag = False
    
    for agent in Agent_Set:
        if main_agent.name != agent.name:
            Other_Set.append(agent)
    Comb_Set = Combination.Combination_list(Other_Set, base_network-1)
    
    pred_state = main_agent.Predit_state(V_pred, W_pred, dt = deltaT)
    obs_gx, obs_gy, obs_gth = main_agent.Relative_observed_goal(pred_state.Px, pred_state.Py, pred_state.Pth)
    
    for Comb_item in Comb_Set:
        other_state = [V_pred, W_pred, main_agent.state.r, obs_gx, obs_gy, obs_gth, V_max] 
        for agent in Comb_item:
            obs_state = agent.Relative_observed_state(pred_state.Px, pred_state.Py, pred_state.Pth)            
            m11, m12, m13 = 0, 0, 0
            if main_agent.rank > agent.rank:   
                m11 = 1
            elif main_agent.rank < agent.rank:   
                m13 = 1
            else:   
                m12 = 1
            VO_flag = VO_flag or Agent.If_in_VO(pred_state, obs_state, time_factor='INF')
            other_state += [m11, m12, m13, obs_state.x, obs_state.y, obs_state.Vx, obs_state.Vy, obs_state.r]
        value_matrix = network.get_value(np.array(other_state))
        Value_list.append(value_matrix[0][0])
    Value = min(Value_list)    
    
    VO_R = 0

    if not VO_flag:
        VO_R = 0.5
    else:
        VO_R = 0
        #print('in VO')

    
    R = 0
    
    main_agent_pred = Agent.Agent('Pred', pred_state.Px, pred_state.Py, pred_state.Pth, pred_state.V, pred_state.W, pred_state.r, main_agent.gx, main_agent.gy, main_agent.gth, main_agent.rank)
    if Check_Goal(main_agent_pred, Calculate_distance(resX, resY, 0, 0), resTH):
        R = Arrived_reward
    for item in Agent_Set:
        if main_agent.name != item.name:
            if Check_Collision(main_agent, item):
                if main_agent.rank > item.rank:
                    R = Collision_high_penalty
                elif main_agent.rank < item.rank:   
                    R = Collision_low_penalty
                else:   
                    R = Collision_equ_penalty
                break
    action_value = R + Value + VO_R
                
    return action_value

def change_V_W_action(V, W, action_value, V_com, W_com, global_action_value):
    V_com.value, W_com.value, global_action_value.value = V, W, action_value
    
lock = mp.Lock()

def Choose_action_from_Network(main_agent, Agent_Set, base_network, linear_acc_set, angular_acc_set, Network_Dict, V_com, W_com, global_action_value):
    action_value_max = -999999   
    for linear_acc in linear_acc_set:
        V_pred = np.clip(main_agent.state.V + linear_acc * deltaT, -V_max, V_max)
        for angular_acc in angular_acc_set:
            W_pred = np.clip(main_agent.state.W + angular_acc * deltaT, -W_max, W_max)            
            action_value = Predict_action_value(main_agent, Agent_Set, V_pred, W_pred, base_network, Network_Dict)            
            if action_value > action_value_max:
                action_value_max = action_value
                action_pair = [V_pred, W_pred]                    
    V_pred = action_pair[0]
    W_pred = action_pair[1]
    #print(action_value_max)
    if action_value_max > global_action_value.value:
        #print(action_value_max)
        lock.acquire()
        try:
            change_V_W_action(V_pred, W_pred, action_value_max, V_com, W_com, global_action_value)
        finally:
            lock.release()


    return V_pred, W_pred

def Choose_action(main_agent, Agent_Set, base_network):
    if main_agent.mode == 'Static':
        V_next, W_next = 0, 0
    if main_agent.mode == 'Random':
        V_next = main_agent.state.V + random.random() - 0.5
        W_next = main_agent.state.W + random.random() - 0.5
    if main_agent.mode == 'Greedy':
        change_V_W_action(0,0,-99999, V_com, W_com, global_action_value)
        t_list = []
        linear_acc_set = np.arange(-linear_acc_max, linear_acc_max, 1)
        angular_acc_set = np.arange(-angular_acc_max, angular_acc_max, 1)
        s_angular_acc_set = np.array_split(angular_acc_set, 6)
        for W in s_angular_acc_set:
            t = mp.Process(target=Choose_action_from_Network, args=(main_agent, Agent_Set, base_network, linear_acc_set, W, Network_Dict, V_com, W_com, global_action_value))
            t.start()
            t_list.append(t)
        for t in t_list:
            t.join()
        V_next, W_next = V_com, W_com
        
    return V_next, W_next

def Agent_Set_Callback(data):
    global Main_Agent, Agent_List
    agent_num = data['agent_num']
    main_agent_name = data['main_agent_name']
    Agent_List = []
    Agent_data = data['Agent_data']
    for agent_dict in Agent_data:
        agent = Agent.DicttoAgent(agent_dict)
        Agent_List.append(agent)
        if agent.name == main_agent_name:
            Main_Agent = copy.deepcopy(agent)
    if agent_num != len(Agent_List):
        print('robot num error!')
    else:
        Navigation_func()
        
def Navigation_func():
    if len(Agent_List) == 2:
        V_cmd, W_cmd = Choose_action(Main_Agent, Agent_List, 2)
    else:
        V_cmd, W_cmd = Choose_action(Main_Agent, Agent_List, 3)
    if Check_Goal(Main_Agent, Calculate_distance(resX, resY, 0, 0), resTH):
        print('Arrived!')
        V_cmd, W_cmd = 0, 0
    msg = {'header':'Message', 'main_agent_name':Main_Agent.name, 'V':V_cmd.value, 'W':W_cmd.value}
    pub.publish_msg(json.dumps(msg))
    
    

if __name__ == '__main__':
    NOW =  datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    Network_Dict = {}
    Main_Agent, Agent_List = [], []
    V_com, W_com, global_action_value = mp.Value('d', 0.0), mp.Value('d', 0.0), mp.Value('d', -999)
    Build_all_Network(Network_Path_Dict)
    pub = Comm.Publisher('127.0.0.1',12346)
    pub.set_pub()
    pub.wait_connect()
    OP = input('Command: ')
    while(OP != 'Stop'):
        if OP == 'Connect':
            sub = Comm.Subscriber('127.0.0.1',12345, cb_func=Agent_Set_Callback)
            sub.connect()
            t = sub.background_callback()
        if OP == 'Nav':
            Navigation_func()
        if OP == 'contin':
            for i in range(100):
                Navigation_func()
        if OP == 'Pub':
            pub.publish_msg(json.dumps({'header':'Message'}))
        OP = input('Command: ')
    sub.socket.close()
    pub.socket.close()
    
