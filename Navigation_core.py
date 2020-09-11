# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 15:17:56 2020

@author: BreezeCat
"""

import sys
import tensorflow.compat.v1 as tf
import json
import random
import numpy as np
import math
import datetime
import copy
import os
import Agent
import Network
import Combination

tf.reset_default_graph()
gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.20) 
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
W_max = 2               #rad/s
linear_acc_max = 10     #m/s^2
angular_acc_max = 7     #rad/s^2
size_min = 0.1          #unit:m
x_upper_bound = 5       #unit:m
x_lower_bound = -5      #unit:m
y_upper_bound = 5       #unit:m
y_lower_bound = -5      #unit:m
TIME_OUT_FACTOR = 4



Network_Path_Dict = {'2':'2_robot_network/gamma09_95_0429/test.ckpt', 
                     '3-1':'multi_robot_network/3_robot_network/0824_925/3_robot.ckpt',
                     '3-2':'multi_robot_network/3_robot_network/0826_933/3_robot.ckpt'
                     
        }


    
def Build_network(session, robot_num, base_network_path):
    N = Network.Network_Dict[str(robot_num)](str(robot_num))
    N.restore_parameter(session, base_network_path)        
    return N



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

def Predict_action_value(session, network, main_agent, Agent_Set, V_pred, W_pred, base_network):
    Other_Set, Value_list = [], []
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
            other_state += [m11, m12, m13, obs_state.x, obs_state.y, obs_state.Vx, obs_state.Vy, obs_state.r]
        state_dict = {}
        state_dict[network.state] = other_state
        value_matrix = session.run(network.value, feed_dict = state_dict)
        Value_list.append(value_matrix[0][0])
    Value = min(Value_list)    
    
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
    action_value = R + Value
                
    return action_value


def Choose_action_from_Network(session, main_agent, Agent_Set, epsilon, base_network):
    dice = random.random()
    action_value_max = -999999   
    if dice < epsilon:
        linear_acc = -linear_acc_max + random.random() * 2 * linear_acc_max
        angular_acc = -angular_acc_max + random.random() * 2 * angular_acc_max
        V_pred = np.clip(main_agent.state.V + linear_acc * deltaT, -V_max, V_max)
        W_pred = np.clip(main_agent.state.W + angular_acc * deltaT, -W_max, W_max)
    else:
        linear_acc_set = np.arange(-linear_acc_max, linear_acc_max, 1)
        angular_acc_set = np.arange(-angular_acc_max, angular_acc_max, 1)
        for linear_acc in linear_acc_set:
            V_pred = np.clip(main_agent.state.V + linear_acc * deltaT, -V_max, V_max)
            for angular_acc in angular_acc_set:
                W_pred = np.clip(main_agent.state.W + angular_acc * deltaT, -W_max, W_max)
                action_value = Predict_action_value(main_agent, Agent_Set, V_pred, W_pred, base_network)
                if action_value > action_value_max:
                    action_value_max = action_value
                    action_pair = [V_pred, W_pred]                    
        V_pred = action_pair[0]
        W_pred = action_pair[1]
        #print(action_value_max)
    return V_pred, W_pred


def Choose_action(session, main_agent, Agent_Set, base_network):
    if main_agent.mode == 'Static':
        V_next, W_next = 0, 0
    if main_agent.mode == 'Random':
        V_next = main_agent.state.V + random.random() - 0.5
        W_next = main_agent.state.W + random.random() - 0.5
    if main_agent.mode == 'Greedy':
        V_next, W_next = Choose_action_from_Network(session, main_agent, Agent_Set, 0, base_network)
        
    return V_next, W_next




if __name__ == '__main__':
    NOW =  datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    print('Test!')
    print(Network_Path_Dict)    
    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
    
    Robot_num = int(input('How many robots: '))
    Base_Network_path = input('Base network path: ')
    Base_Network_num = int(input('Base network num: '))
    
    print('Build Network for ', Robot_num, ' robots with ', Base_Network_num, ' robot network at ', Base_Network_path)
        
    Value, Network_list, Train = Build_network(sess, Robot_num, Base_Network_num, Base_Network_path)
    
    SAVE_PATH = input('Save Path: ')


    
