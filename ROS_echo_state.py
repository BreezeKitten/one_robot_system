# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 20:14:35 2020

@author: BreezeCat
"""

Main_name = input('name: ')    
    
import json
import copy
import rospy
import Agent
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
start_flag = False

Main_agent = Agent.Agent(Main_name, 0, 0, 0, 0, 0, 0.3, 0, 0, 0, 1)

def Pose_CB(data):
    global Main_agent
    Main_agent.state.Px, Main_agent.state.Py, Main_agent.state.Pth = data.linear.x, data.linear.y, data.angular.z       
    return        

def Vel_CB(data):
    global Main_agent
    Main_agent.state.V, Main_agent.state.W = data.linear.x, data.angular.z       
    return  
            
def Flag_CB(data):
    global start_flag 
    start_flag = data.data
    if start_flag:
        print('mission start!')
    else:
        print('mission pause!')


rospy.init_node('Echo_node_'+Main_name,anonymous=True)
rate = rospy.Rate(10)
pose_sub = rospy.Subscriber("/"+Main_name+"/robot_pose",Twist,Pose_CB)
flag_sub = rospy.Subscriber("/start_flag",Bool,Flag_CB)
vel_sub = rospy.Subscriber("/"+Main_name+"/FeedBack_Vel",Twist,Vel_CB)

while not rospy.is_shutdown():
    if start_flag:
        Main_agent.Path.append(copy.deepcopy(Main_agent.state))
    try:
        rate.sleep()
    except Exception as e:
        print('ROS rate error', e)
        break
Main_agent.Record_data('logs')