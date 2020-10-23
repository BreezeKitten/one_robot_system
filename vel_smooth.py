# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 17:21:06 2020

@author: BreezeCat
"""

import rospy
from geometry_msgs.msg import Twist
import sys

name = sys.argv[1]
rawV, rawW, smoothV, smoothW = 0,0,0,0
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

rospy.init_node('vel_smooth', anonymous=True)

goal_pub_dict = {}

robot_cmd_vel = rospy.Publisher("/"+name+"/cmd_vel", Twist, queue_size=10)



def Vel_pub(rV, rW, sV):
    Cmd_Vel = Twist()
    V_cmd, W_cmd = Saturation(rV, rW, sV, 1)
    Cmd_Vel.linear.x = V_cmd
    Cmd_Vel.angular.z = W_cmd
    robot_cmd_vel.publish(Cmd_Vel)

    return

def rVel_CB(data):
    global rawV, rawW
    rawV = data.linear.x 
    rawW = data.angular.z
    return

def sVel_CB(data):
    global smoothV, smoothW
    smoothV = data.linear.x 
    smoothW = data.angular.z
    return

raw_sub = rospy.Subscriber("/"+name+"/raw_cmd_vel",Twist,rVel_CB)
smooth_sub = rospy.Subscriber("/"+name+"/s_cmd_vel",Twist,sVel_CB)
rate = rospy.Rate(10)
while not rospy.is_shutdown():
    Vel_pub(rawV, rawW, abs(smoothV))
    rate.sleep()        


                    
    
