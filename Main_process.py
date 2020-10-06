# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 10:52:14 2020

@author: BreezeCat
"""

IS_SIMULATION = True
deltaT = 0.1

import Agent
import Navigation_core
import geo_virtual_robot
import matplotlib.pyplot as plt
import datetime

Map = geo_virtual_robot.TEST_Map
real_Map = geo_virtual_robot.TEST_Map_real
TEST_Agent = Agent.Agent('TEST', -3, 0, 0, 0, 0, 0.2, 2, -3, 6.28-1.57, 1, mode = 'Greedy')
color_list = ['b', 'g', 'r', 'c', 'm', 'y', 'k']



def Show_Path(Agent_Set, result, Map, FV, VVO, save_path):
    plt.close('all')
    plt.figure(figsize=(12,12))
    ax = plt.subplot(111)
    ax.cla()    
    ax = VVO.plot(color='yellow',ax = FV.plot(color='red', ax = real_Map.plot(color='black', ax = Map.plot(color='gray', ax = ax))))
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

def Saturation(V, W, Vmax, Wmax):
    Vsat, Wsat = V, W
    if abs(V) > Vmax:
        Vsat = Vmax * abs(V)/V
        Wsat = W * Vmax/abs(V)
        if abs(Wsat) > Wmax:
           Vsat = Vsat * Wmax/abs(Wsat)
           Wsat = Wmax * abs(Wsat)/Wsat
    elif abs(W) > Wmax:
        Wsat = Wmax * abs(W)/W
        Vsat = V * Wmax/abs(W)
        if abs(Vsat) > Vmax:
            Wsat = Wsat * Vmax/abs(Vsat)
            Vsat = Vmax * abs(Vsat)/Vsat
    return Vsat, Wsat
    

def Sim_Process(main_agent: Agent.Agent, save_path):
    time = 0
    while not Navigation_core.Check_Goal(main_agent, 0.2, 3.14/15):
        Virtual_Agent, FV, VVO = geo_virtual_robot.Virtual_Agent_func(main_agent, 1, 1, Map)
        while len(Virtual_Agent) < 1:
            print('empty')
            Virtual_Agent.append(Agent.Agent('empty',-5,-5,0,0,0,0.2,-5,-5,0,3,mode='Static'))
            
        All_Agent_list = [main_agent] + Virtual_Agent
        #print(len(All_Agent_list))
        Show_Path(All_Agent_list, str(round(time,1)), Map, FV, VVO, save_path)
        V_net, W_net = Navigation_core.Choose_action(main_agent, All_Agent_list, min(len(All_Agent_list),3))
        #print(V_net, W_net)
        V_next, W_next = Saturation(V_net, W_net, 0.5, 1)
        print('sat:', V_next, W_next)
        main_agent.Set_V_W(V_next, W_next)
        main_agent.Update_state(dt=deltaT)
        main_agent.Check_oscillation(5)
        '''
        for VR in geo_virtual_robot.Virtual_Agent_List:
            VR.Set_V_W(V_next/3, 0)
            VR.Update_state(dt=deltaT)
        '''
        time += deltaT      
    V_next, W_next = 0, 0
    main_agent.Set_V_W(V_next, W_next)
    return

def Process():
    
    return


        