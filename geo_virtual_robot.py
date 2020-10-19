# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 10:10:26 2020

@author: BreezeCat
"""

import geo_func as gef
import Agent
import random
import copy
import math 

VO_range = 2
TEST_Map = gef.Build_test_map(4)
TEST_Map_real = gef.Build_test_map(3)
TEST_Agent = Agent.Agent('TEST', 0, 0, 0, 0, 0, 0.5, 0, 0, 0, 3, mode = 'Greedy')
Virtual_Agent_List = []

def Build_FV(main_agent: Agent.Agent, dV, Wmax, env_map):
    V_set = gef.Build_velocity_poly(main_agent.state, dV, Wmax, safety_factor=1.5)
    FV = gef.Set_intersection(V_set, env_map)
    Del_small_area(FV)
    return FV

def Find_bound(main_Px, main_Py, bound):
    b_minx, b_miny, b_maxx, b_maxy = bound[0], bound[1], bound[2], bound[3]
    mid_x, mid_y = (b_maxx + b_minx)/2, (b_maxy + b_miny)/2
    v = gef.Vector(main_Px - mid_x, main_Py - mid_y)
    new_mid_x, new_mid_y = mid_x , mid_y + v.y*0.5/v.length
    x_bound = [new_mid_x - 0.1, new_mid_x + 0.1]
    y_bound = [new_mid_y - 0.02, new_mid_y + 0.02]
    return x_bound, y_bound

def General_virtual_agent(name, x_bound, y_bound):
    x, y, r = random.uniform(x_bound[0], x_bound[1]), random.uniform(y_bound[0], y_bound[1]), 0.2
    return Agent.Agent(name, x, y, 0, 0, 0, r, x, y, 0, 3, mode = 'Greedy', nonholonomic=False)

def Modify_Virtual_List(main_agent: Agent.Agent, diff, FV):
    for i in diff.index:
        bound = diff.geometry[i].bounds
        x_bound, y_bound = Find_bound(main_agent.state.Px, main_agent.state.Py, bound)
        sFV = gef.Generate_GeoDataFrame([diff.geometry[i]])
        sV = General_virtual_agent('diff'+str(i), x_bound, y_bound)
        sVVO_df = gef.Generate_GeoDataFrame([gef.New_robot_polygon(main_agent.state, sV.Relative_observed_state(0,0,0), VO_range)])
        sdiff = gef.Set_difference(sFV, sVVO_df)  
        Del_small_area(sdiff)
        time = 0
        while(len(sdiff.is_empty) != 0 and time < 3):
            sV = General_virtual_agent('diff'+str(i), x_bound, y_bound)
            sVVO_df = gef.Generate_GeoDataFrame([gef.New_robot_polygon(main_agent.state, sV.Relative_observed_state(0,0,0), VO_range)])
            sdiff = gef.Set_difference(sFV, sVVO_df)  
            Del_small_area(sdiff)
            time = time + 1
        #print(time)                 
        Virtual_Agent_List.append(sV)            
    return

def Del_small_area(gpdf):
    for i in gpdf.index:
        if gpdf.geometry[i].area < 0.2:
            gpdf.drop(i, inplace=True)

def Calculate_distance(x1, y1, x2, y2):
    return math.sqrt(math.pow( (x1-x2) , 2) + math.pow( (y1-y2) , 2))
            
def Adjust_Old_New_VA(main_agent: Agent.Agent, Old_List: [Agent.Agent]):
    global Virtual_Agent_List
    if Virtual_Agent_List == []:
        print('empty VAl, copy old')
        for old_agent in Old_List:
            if Calculate_distance(old_agent.state.Px, old_agent.state.Py, main_agent.state.Px, main_agent.state.Py) > 3.5 and len(Old_List) > 1:
                Old_List.remove(old_agent)
        Virtual_Agent_List = copy.deepcopy(Old_List)
        return
    
    if len(Virtual_Agent_List) <= len(Old_List):
        for new_agent in Virtual_Agent_List:
            for old_agent in Old_List:
                if Calculate_distance(old_agent.state.Px, old_agent.state.Py, new_agent.state.Px, new_agent.state.Py) < 0.3:
                    if Calculate_distance(old_agent.state.Px, old_agent.state.Py, new_agent.state.Px, new_agent.state.Py) < 0.15:
                        new_agent = old_agent
                    Old_List.remove(old_agent)
                    
        for old_agent in Old_List:
            if Calculate_distance(old_agent.state.Px, old_agent.state.Py, main_agent.state.Px, main_agent.state.Py) > 4:
                Old_List.remove(old_agent)
                
        Virtual_Agent_List = Virtual_Agent_List + Old_List
        return        
            

def Find_Virtual_Agent(main_agent: Agent.Agent, FV):
    global Virtual_Agent_List
    Old_VA_List = copy.deepcopy(Virtual_Agent_List)
    Virtual_Agent_List = []
    

    if Virtual_Agent_List == []:
        for i in FV.index:
            bound = FV.geometry[i].bounds
            x_bound, y_bound = Find_bound(main_agent.state.Px, main_agent.state.Py, bound)
            sFV = gef.Generate_GeoDataFrame([FV.geometry[i]])
            sV = General_virtual_agent('FV'+str(i), x_bound, y_bound)
            sVVO_df = gef.Generate_GeoDataFrame([gef.New_robot_polygon(main_agent.state, sV.Relative_observed_state(0,0,0), VO_range)])
            sdiff = gef.Set_difference(sFV, sVVO_df)  
            Del_small_area(sdiff)
            time = 0
            while(len(sdiff.is_empty) != 0 and time < 3):
                sV = General_virtual_agent('FV'+str(i), x_bound, y_bound)
                sVVO_df = gef.Generate_GeoDataFrame([gef.New_robot_polygon(main_agent.state, sV.Relative_observed_state(0,0,0), VO_range)])
                sdiff = gef.Set_difference(sFV, sVVO_df)  
                Del_small_area(sdiff)
                time = time + 1
            #print(time)                 
            Virtual_Agent_List.append(sV)
     
    VVO_poly_list = [gef.New_robot_polygon(main_agent.state, virtual_agent.Relative_observed_state(0,0,0), VO_range) for virtual_agent in Virtual_Agent_List]
    VVO_df = gef.Generate_GeoDataFrame(VVO_poly_list)
    diff = gef.Set_difference(FV, VVO_df)
    diff = gef.explode(diff)
    Del_small_area(diff)
    while(len(diff.is_empty) != 0 and sum(diff.area) > 0.2):
        #print(sum(diff.area))
        Modify_Virtual_List(main_agent, diff, FV)
        VVO_poly_list = [gef.New_robot_polygon(main_agent.state, virtual_agent.Relative_observed_state(0,0,0), VO_range) for virtual_agent in Virtual_Agent_List]
        VVO_df = gef.Generate_GeoDataFrame(VVO_poly_list)
        diff = gef.Set_difference(FV, VVO_df)
        diff = gef.explode(diff)
        Del_small_area(diff)
    #VVO_df.plot(ax = FV.plot(ax=TEST_Map.plot(color='black'), color='red'))
    Adjust_Old_New_VA(main_agent, Old_VA_List)
        
    return VVO_df

  
def Virtual_Agent_func(main_agent: Agent.Agent, dV, Wmax, Map):
    global Virtual_Agent_List
    if main_agent.mode == 'Oscillation' and main_agent.oscill_time > 5:
        print('Clear virtual agent')
        Virtual_Agent_List = []
        main_agent.oscill_time = 0
    try:
        FV = Build_FV(main_agent, dV, Wmax, Map)
        VVO = Find_Virtual_Agent(main_agent, FV)
        return copy.deepcopy(Virtual_Agent_List), FV, VVO
    except:
        print('VAf_error')
        return copy.deepcopy(Virtual_Agent_List), gef.Generate_GeoDataFrame([]), gef.Generate_GeoDataFrame([])
    
    

            