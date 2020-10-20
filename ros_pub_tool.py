# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 17:21:06 2020

@author: BreezeCat
"""

import rospy
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Bool


Command_list = ['Stop', 'Start', 'Manual']
name_list = ['robot1', 'robot2', 'robot3', 'robot4']

rospy.init_node('tool', anonymous=True)

goal_pub_dict = {}

#[x,y,z,w]
Angle_table = {'0':[0,0,0,1], '45':[0,0,0.383,0.924], '90':[0,0,0.707,0.707], '135':[0,0,0.924,0.383], '180':[0,0,1,0],
               '-135':[0,0,0.924,-0.383], '-90':[0,0,0.707,-0.707], '-45':[0,0,-0.383,0.924]}
               


for name in name_list:
    goal_pub_dict[name] = rospy.Publisher("/"+name+"/move_base_simple/goal", PoseStamped, queue_size=10)

start_flag_pub = rospy.Publisher("/start_flag",Bool, queue_size=10)

def Start_nav():
    data = Bool()
    data = True
    start_flag_pub.publish(data)
    return

def Goal_pub(robot_name, gx, gy, gth):
    goal = PoseStamped()
    goal.header.frame_id = 'map'
    goal.pose.position.x, goal.pose.position.y, goal.pose.position.z = gx, gy, 0
    [goal.pose.orientaiotn.x, goal.pose.orientaiotn.y, goal.pose.orientaiotn.z, goal.pose.orientaiotn.w] = Angle_table[gth]
    goal_pub_dict[robot_name].publish(goal)
    return

def Show_Command():
    print('Command List:')
    print('#################')
    for item in Command_list:
        print('## '+item)
    print('#################')
    return

OP = ''
while(OP != 'Stop'):
    try:
        Show_Command()
        OP = input('Command:')
    except Exception as e:
        print('input error:', e)
        pass
        
    if OP not in Command_list:
        print('not existed coommand!', OP)
    elif OP == 'Start':
        try:
            Start_nav()
        except Exception as e:
            print('Start error:', e)
    elif OP == 'Manual':
        try:
            robot_name = input('robot_name: ')
            gx = float(input('gx: '))
            gy = float(input('gy: '))
            gth = str(input('gth: '))
            Goal_pub(robot_name, gx, gy, gth)
        except Exception as e:
            print('Manial error:', e)


                    
    