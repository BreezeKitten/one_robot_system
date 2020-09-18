# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 17:08:18 2020

@author: BreezeCat
"""
import sys
import json
import random
import numpy as np
import math
import matplotlib.pyplot as plt
import datetime
import copy
import os
import Agent
import configparser
import Combination
import Communication_func as Comm
import time as TT

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
DL Parameter
'''
training_eposide_num = 5000 #100000 
training_num = 1500 #3000
test_num = 1
two_robot_Network_Path = '2_robot_network/gamma09_95_0429/test.ckpt'

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


RL_eposide_num = 100
RL_epsilon = 0
gamma = 0.9

Network_Path_Dict = {'2':'2_robot_network/gamma09_95_0429/test.ckpt', 
                     '3':'TEST/Network/3_robot.ckpt'
        }

Command_dict = {}


def Load_Config(file):
    print('Load config from ' + file)
    config = configparser.ConfigParser()
    config.read(file)
    configDict = {section: dict(config.items(section)) for section in config.sections()}
    print(configDict)
    return configDict

def Set_parameter(paraDict):
    global deltaT, V_max, W_max, linear_acc_max, angular_acc_max, size_min, TIME_OUT_FACTOR
    print('Set parameter\n', paraDict)
    deltaT = float(paraDict['deltat'])
    V_max, W_max, linear_acc_max, angular_acc_max = float(paraDict['v_max']), float(paraDict['w_max']), float(paraDict['linear_acc_max']), float(paraDict['angular_acc_max'])
    size_min = float(paraDict['size_min'])
    TIME_OUT_FACTOR = float(paraDict['time_out_factor'])
    


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

def Random_Agent(name):
    Px = random.random()*(x_upper_bound - x_lower_bound) + x_lower_bound
    Py = random.random()*(y_upper_bound - y_lower_bound) + y_lower_bound
    Pth = random.random()*2*PI 
    V = 0 #(random.random() - 0.5) * V_max
    W = 0 #(random.random() - 0.5) * W_max
    r = random.random() + size_min
    gx = random.random()*(x_upper_bound - x_lower_bound) + x_lower_bound
    gy = random.random()*(y_upper_bound - y_lower_bound) + y_lower_bound
    gth = random.random()*2*PI 
    rank = random.randint(1,3)
    return Agent.Agent(name, Px, Py, Pth, V, W, r, gx, gy, gth, rank, mode = 'Greedy')

def Set_Agent(name):
    Px = float(input('Px(-5~5m): '))
    Py = float(input('Py(-5~5m): '))
    Pth = float(input('Pth(0~6.28): '))
    V = 0 #(random.random() - 0.5) * V_max
    W = 0 #(random.random() - 0.5) * W_max
    r = float(input('r(0.1~1m): '))
    gx = float(input('gx(-5~5m): '))
    gy = float(input('gy(-5~5m): '))
    gth = float(input('gth(0~6.28): '))
    rank = int(input('rnak(1.2.3): '))
    return Agent.Agent(name, Px, Py, Pth, V, W, r, gx, gy, gth, rank, mode = 'Greedy')



def Show_Path(Agent_Set, result, save_path):
    plt.close('all')
    plt.figure(figsize=(12,12))
    ax = plt.gca()
    ax.cla()    
    ax.set_xlim((x_lower_bound,x_upper_bound))     #上下限
    ax.set_ylim((x_lower_bound,x_upper_bound))
    plt.xlabel('X(m)')
    plt.ylabel('Y(m)')
    color_count = 0
    for agent in Agent_Set:
        agent.Plot_Path(ax = ax, color = color_list[color_count%len(color_list)])
        agent.Plot_goal(ax = ax, color = color_list[color_count%len(color_list)])
        color_count += 1
    NOW = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    plt.savefig(save_path +'/'+ NOW + result +'.png')
    return


def RL_process_all_Goal(robot_num, eposide_num, epsilon, RL_SAVE_PATH):    
    for eposide in range(eposide_num):
        global Command_dict
        Command_dict = {}
        if eposide%20 == 0:
            print(eposide)
        Main_Agent = Random_Agent('Main')
        Agent_Set = [Main_Agent]
        for i in range(robot_num-1):
            Agent_Set.append(Random_Agent(str(i+2)))      
        
        time = 0
        
        Collision_Flag = False
        Goal_dist_Flag = False
        for item in Agent_Set:
            for item2 in Agent_Set:
                if item.name != item2.name:
                    Collision_Flag = Collision_Flag or Check_Collision(item, item2)
                    Goal_dist_Flag = Goal_dist_Flag or Calculate_distance(item.gx, item.gy, item2.gx, item2.gy) < (item.state.r + item2.state.r)
                if Collision_Flag or Goal_dist_Flag:
                    break
            if Collision_Flag or Goal_dist_Flag:
                break
        if Collision_Flag or Goal_dist_Flag:
            continue

        if Check_Goal(Main_Agent, Calculate_distance(resX, resY, 0, 0), resTH):
            continue
        
        TIME_OUT = 0
        for agent in Agent_Set:
            TIME_OUT = max(TIME_OUT, Calculate_distance(agent.state.Px, agent.state.Py, agent.gx, agent.gy) * TIME_OUT_FACTOR)
   
       
        terminal_flag = True
        for agent in Agent_Set:
            small_goal_flag = Check_Goal(agent, Calculate_distance(resX, resY, 0, 0), resTH)
            if small_goal_flag:
                agent.Goal_state = 'Finish'
            terminal_flag = terminal_flag and small_goal_flag
            
        data = {}
        data['header'] = 'Message'
        data['agent_num'] = len(Agent_Set)
        data['Agent_data'] = []
        for agent in Agent_Set:
            data['Agent_data'].append(agent.Transform_to_Dict())
            Command_dict[agent.name] = {'V':0, 'W':0}          
            
            
        NOW = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        save_path = RL_SAVE_PATH + '/' + NOW
        os.makedirs(save_path)
        while(not terminal_flag):       
            for agent1 in Agent_Set:               
                for agent2 in Agent_Set:
                    if agent1.name != agent2.name:
                        if Check_Collision(agent1, agent2):
                            if agent1.rank > agent2.rank:
                                if agent1.Goal_state == 'Not':
                                    agent1.Goal_state = 'Collision_high'
                                if agent2.Goal_state == 'Not':
                                    agent2.Goal_state = 'Collision_low'
                            elif agent1.rank < agent2.rank:
                                if agent1.Goal_state == 'Not':
                                    agent1.Goal_state = 'Collision_low'
                                if agent2.Goal_state == 'Not':
                                    agent2.Goal_state = 'Collision_high'
                            else:
                                if agent1.Goal_state == 'Not':
                                    agent1.Goal_state = 'Collision_equal'
                                if agent2.Goal_state == 'Not':
                                    agent2.Goal_state = 'Collision_equal'
                if Check_Goal(agent1, Calculate_distance(resX, resY, 0, 0), resTH) and agent1.Goal_state == 'Not':
                    agent1.Goal_state = 'Finish'

            
            for agent in Agent_Set:
                data['main_agent_name'] = agent.name
                pub.publish_msg(json.dumps(data).encode())
                TT.sleep(0.1)
            
            terminal_flag = True
            for agent in Agent_Set:
                if agent.Goal_state == 'Not':
                    V_next, W_next = Command_dict[agent.name]['V'], Command_dict[agent.name]['W']
                else:
                    V_next, W_next = 0, 0  
                agent.Set_V_W(V_next, W_next)
                terminal_flag = terminal_flag and agent.Goal_state != 'Not'
                       
            if time > TIME_OUT:
                for agent in Agent_Set:
                    if agent.Goal_state == 'Not':
                        agent.Goal_state = 'TIME_OUT'
                break


            for agent in Agent_Set:
                agent.Update_state(dt = deltaT)
                    
            time = time + deltaT


            
            
        result = ''
        for agent in Agent_Set:
            result = result + agent.Goal_state[0]
            agent.Record_data(save_path)
        Show_Path(Agent_Set, result, save_path)
    return


def callback(data):
    global Command_dict
    Command_dict[data['main_agent_name']]['V'], Command_dict[data['main_agent_name']]['W'] = data['V'], data['W']

if __name__ == '__main__':
    NOW =  datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    if len(sys.argv) < 2:
        Configfile = input('Config file at:')
    else:
        Configfile = sys.argv[1]
    Config_dict = Load_Config(Configfile) 
   
    
    if int(Config_dict['main']['custom_parameter']):
        Set_parameter(Config_dict['parameter'])
        
    pub = Comm.Publisher('127.0.0.1',12345)
    pub.set_pub()
    pub.wait_connect()
    
    OP = input('Command: ')
    while(OP != 'Stop'):
        if OP == 'Connect':
            sub = Comm.Subscriber('127.0.0.1',12346, cb_func=callback)
            sub.connect()
            t = sub.background_callback()
        OP = input('Command: ')
          
        
    
    if int(Config_dict['main']['all_goal']):
        print('All goal process')
        save_path = Config_dict['main']['save_path'] + '/' + NOW +'_all_goal'
        os.makedirs(save_path)
        RL_process_all_Goal(int(Config_dict['main']['robot_num']), int(Config_dict['main']['eposide_num']), epsilon = 1, RL_SAVE_PATH = save_path)
        
    pub.socket.close()
    sub.socket.close()  
