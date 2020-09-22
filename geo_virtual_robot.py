# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 10:10:26 2020

@author: BreezeCat
"""

import geo_func as gef
import Agent
import random

VO_range = 2
TEST_Map = gef.Build_test_map(3)
TEST_Agent = Agent.Agent('TEST', 0, 0, 0, 0, 0, 0.2, 0, 0, 0, 1, mode = 'Greedy')
Virtual_Agent_List = []

def Build_FV(main_agent: Agent.Agent, dV, Wmax, env_map):
    V_set = gef.Build_velocity_poly(main_agent.state, dV, Wmax)
    FV = gef.Set_intersection(V_set, env_map)
    Del_small_area(FV)
    return FV

def Find_bound(main_Px, main_Py, bound):
    b_minx, b_miny, b_maxx, b_maxy = bound[0], bound[1], bound[2], bound[3]
    mid_x, mid_y = (b_maxx + b_minx)/2, (b_maxy + b_miny)/2
    v = gef.Vector(main_Px - mid_x, main_Py - mid_y)
    new_mid_x, new_mid_y = mid_x , mid_y + v.y*0.5/v.length
    x_bound = [new_mid_x - 0.3, new_mid_x + 0.3]
    y_bound = [new_mid_y - 0.3, new_mid_y + 0.3]
    return x_bound, y_bound

def General_virtual_agent(name, x_bound, y_bound):
    x, y, r = random.uniform(x_bound[0], x_bound[1]), random.uniform(y_bound[0], y_bound[1]), 0.2
    return Agent.Agent(name, x, y, 0, 0, 0, r, 0, 0, 0, 1, mode = 'Greedy')

def Modify_Virtual_List(main_agent: Agent.Agent, diff, FV):
    for i in diff.index:
        bound = diff.geometry[i].bounds
        x_bound, y_bound = Find_bound(main_agent.state.Px, main_agent.state.Py, bound)            
        Virtual_Agent_List.append(General_virtual_agent('diff'+str(i), x_bound, y_bound))
    return

def Del_small_area(gpdf):
    for i in gpdf.index:
        if gpdf.geometry[i].area < 0.2:
            gpdf.drop(i, inplace=True)

def Find_Virtual_Agent(main_agent: Agent.Agent, FV):
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
            print(time)                 
            Virtual_Agent_List.append(sV)
            
    VVO_poly_list = [gef.New_robot_polygon(main_agent.state, virtual_agent.Relative_observed_state(0,0,0), VO_range) for virtual_agent in Virtual_Agent_List]
    VVO_df = gef.Generate_GeoDataFrame(VVO_poly_list)
    diff = gef.Set_difference(FV, VVO_df)
    diff = gef.explode(diff)
    Del_small_area(diff)
    while(len(diff.is_empty) != 0 and sum(diff.area) > 1):
        print(sum(diff.area))
        Modify_Virtual_List(main_agent, diff, FV)
        VVO_poly_list = [gef.New_robot_polygon(main_agent.state, virtual_agent.Relative_observed_state(0,0,0), VO_range) for virtual_agent in Virtual_Agent_List]
        VVO_df = gef.Generate_GeoDataFrame(VVO_poly_list)
        diff = gef.Set_difference(FV, VVO_df)
        diff = gef.explode(diff)
        Del_small_area(diff)
    #VVO_df.plot(ax = FV.plot(ax=TEST_Map.plot(color='black'), color='red'))        
    return VVO_df

    


            