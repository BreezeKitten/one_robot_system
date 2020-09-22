# -*- coding: utf-8 -*-
"""
Created on Mon Sep 21 10:23:32 2020

@author: BreezeCat
"""

import geopandas
from shapely.geometry import Polygon
from shapely.geometry.multipolygon import MultiPolygon

import math as m
import Agent

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def List(self):
        return (self.x, self.y)

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.length = self.get_length()
        
    def get_length(self):
        return m.sqrt(self.x*self.x + self.y*self.y)
    
    def print_vector(self):
        print([self.x, self.y])
        
def Dot(vector1, vector2):
    return vector1.x*vector2.x + vector1.y*vector2.y

def Norm2(vector):
    return m.sqrt(Dot(vector,vector))

def Rotate_vector(vector, theta):
    c = m.cos(theta)
    s = m.sin(theta)
    vx = c * vector.x - s * vector.y
    vy = s * vector.x + c * vector.y
    return Vector(vx, vy)

def Set_union(set1, set2):
    return  geopandas.overlay(set1, set2, how='union')

def Set_intersection(set1, set2):
    return  geopandas.overlay(set1, set2, how='intersection')

def Set_difference(set1, set2): #set1 - set2
    return  geopandas.overlay(set1, set2, how='difference')

def Generate_GeoDataFrame(polys_list):
    num = len(polys_list)
    df_list = [i+1 for i in range(num)]
    polys_series = geopandas.GeoSeries(polys_list)
    df = geopandas.GeoDataFrame({'geometry': polys_series, 'df': df_list})
    return df

def New_robot_polygon(Main_State: Agent.State, Virtual_State: Agent.Observed_State, VO_range):
    PA, rA = Point(Main_State.Px, Main_State.Py), Main_State.r 
    PB, rB, Vx, Vy = Point(Virtual_State.x, Virtual_State.y), Virtual_State.r, Virtual_State.Vx, Virtual_State.Vy
    
    u = Vector(PB.x - PA.x, PB.y - PA.y)
    u_unit = Vector((PB.x - PA.x)/u.length, (PB.y - PA.y)/u.length)
    d = u.length
    if (rA + rB) > d:
        theta = 0
    else:
        theta = m.asin((rA + rB)/d)
    u_L = Rotate_vector(u_unit, theta)
    u_R = Rotate_vector(u_unit, -theta)

    if VO_range == 'inf':
        LS = 0
    else:
        LS = d/VO_range/m.cos(theta)
    LL = max(5,5*LS)
    
    A = Point(PA.x + LS* u_L.x + Vx, PA.y + LS* u_L.y + Vy)
    B = Point(PA.x + LS* u_R.x + Vx, PA.y + LS* u_R.y + Vy)
    C = Point(PA.x + LL* u_R.x + Vx, PA.y + LL* u_R.y + Vy)
    D = Point(PA.x + LL* u_L.x + Vx, PA.y + LL* u_L.y + Vy)
    
    polys = Polygon([A.List(), B.List(), C.List(), D.List()])
    
    return polys

def Build_velocity_poly(Robot: Agent.State, dV, Wmax, approximation_method = 'Tri'):
    P = Point(Robot.Px, Robot.Py)
    theta = Robot.Pth
    V = Robot.V    
    Vc = Point(P.x+V*m.cos(theta), P.y+V*m.sin(theta))
    if V == 0:
        Vv = Vector((V+dV)*m.cos(theta), (V+dV)*m.sin(theta))
    else:
        Vv = Vector(V*m.cos(theta), V*m.sin(theta))
    Vo = Rotate_vector(Vv, m.pi/2)    
    # Square approximaion   
    if approximation_method == 'Squ':      
        A = Point(Vc.x+dV, Vc.y+dV)
        B = Point(Vc.x-dV, Vc.y+dV)
        C = Point(Vc.x-dV, Vc.y-dV)
        D = Point(Vc.x+dV, Vc.y-dV)
        poly_list = [Polygon([A.List(), B.List(), C.List(), D.List()])]    
    # triangle approximation
    if approximation_method == 'Tri':
        A = Point(Vv.x*(V+dV)/Vv.length + Vo.x*(V+dV)*Wmax/Vo.length + P.x, Vv.y*(V+dV)/Vv.length + Vo.y*(V+dV)*Wmax/Vo.length + P.y)
        B = Point(Vv.x*(V-dV)/Vv.length + Vo.x*(V-dV)*Wmax/Vo.length + P.x, Vv.y*(V-dV)/Vv.length + Vo.y*(V-dV)*Wmax/Vo.length + P.y)
        C = Point(Vv.x*(V-dV)/Vv.length - Vo.x*(V-dV)*Wmax/Vo.length + P.x, Vv.y*(V-dV)/Vv.length - Vo.y*(V-dV)*Wmax/Vo.length + P.y)
        D = Point(Vv.x*(V+dV)/Vv.length - Vo.x*(V+dV)*Wmax/Vo.length + P.x, Vv.y*(V+dV)/Vv.length - Vo.y*(V+dV)*Wmax/Vo.length + P.y)    
        if V*(V-dV) > 0 :#or V*(V+dV) < 0:
            poly_list = [Polygon([A.List(), B.List(), C.List(), D.List()])]
        else:
            poly_list = [Polygon([A.List(), P.List(), D.List()]), Polygon([P.List(), B.List(), C.List()])]    
    Vel_df = Generate_GeoDataFrame(poly_list)
    return Vel_df

def Build_test_map(map_num):
    obs_list = []
    if map_num == 1:
        obs_list.append(Polygon([(-5,-5), (5,-5), (5,-1), (-5,-1)]))
        obs_list.append(Polygon([(-5,1), (5,1), (5,5), (-5,5)]))
        test_map = Generate_GeoDataFrame(obs_list)
        return test_map
    elif map_num == 2:
        obs_list.append(Polygon([(-5,-5), (0,-5), (0,-1), (-5,-1)]))
        obs_list.append(Polygon([(-5,1), (5,1), (5,5), (-5,5)]))
        test_map = Generate_GeoDataFrame(obs_list)    
        return test_map
    elif map_num == 3:
        obs_list.append(Polygon([(-5,-5), (1,-5), (1,-1), (-5,-1)]))
        obs_list.append(Polygon([(-5,1), (5,1), (5,5), (-5,5)]))
        obs_list.append(Polygon([(3,-5), (3,5), (5,5), (5,-5)]))
        test_map = Generate_GeoDataFrame(obs_list)
        return test_map
    else:
        print('map_num error')
        return
    
def explode(indf):
    outdf = geopandas.GeoDataFrame(columns=indf.columns)
    for idx, row in indf.iterrows():
        if type(row.geometry) == Polygon:
            outdf = outdf.append(row,ignore_index=True)
        if type(row.geometry) == MultiPolygon:
            multdf = geopandas.GeoDataFrame(columns=indf.columns)
            recs = len(row.geometry)
            multdf = multdf.append([row]*recs,ignore_index=True)
            for geom in range(recs):
                multdf.loc[geom,'geometry'] = row.geometry[geom]
            outdf = outdf.append(multdf,ignore_index=True)
    return outdf