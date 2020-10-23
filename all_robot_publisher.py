# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 15:38:04 2020

@author: BreezeCat
"""

import rospy
import Agent
import Communication_func as Comm
from geometry_msgs.msg import Twist
import threading
import sys

IP = '192.168.0.134'
name_list = ['robot'+str(i+1) for i in range(int(sys.argv[1]))]
Agent_list = []
message_list = []
Pub_List = []
STOP_Flag = False

for name in name_list:
    Agent_list.append(Agent.Agent(name, -5, 5, 0, 0, 0, 0.2, 0, 0, 0, 1))
    

class Robot_message():
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.pub = self.Build_pub()
        self.ros_pose_sub = rospy.Subscriber("/"+name+"/robot_pose",Twist,self.Pose_CB)
        self.ros_vel_sub = rospy.Subscriber("/"+name+"/cmd_vel",Twist,self.vel_CB)
    
    def Build_pub(self):
        pub = Comm.Publisher(self.ip, 12340+int(self.name[-1]))
        pub.set_pub()
        pub.wait_connect()
        return pub
        
    def Pose_CB(self, data):
        for agent in Agent_list:
            if agent.name == self.name:
                agent.state.Px, agent.state.Py, agent.state.Pth = data.linear.x, data.linear.y, data.angular.z
    
    def vel_CB(self, data):
        for agent in Agent_list:
            if agent.name == self.name:
                agent.state.V, agent.state.W = data.linear.x, data.angular.z                
        
            
def Pub_process(pub_list):
        data = {}
        data['header'] = 'Message'
        data['Agent_data'] = []
        for agent in Agent_list:
            data['Agent_data'].append(agent.Transform_to_Dict())        
        for pub in pub_list:
            pub.send_msg(data)
        return
            
def tread_Pub_Process(pub_list):
    global STOP_Flag
    while not (rospy.is_shutdown() or STOP_Flag):
        Pub_process(Pub_List)
        rate.sleep()
    print('Stop!')
    return

def Build_Pub():
    global message_list, Pub_List
    for name in name_list:
        message_list.append(Robot_message(name, IP))
        Pub_List.append(message_list[-1].pub)
    return
        
def Close_Pub():
    global message_list, Pub_List
    for pub in Pub_List:
        pub.socket.shutdown(2)
        pub.socket.close()
    message_list, Pub_List = [], []
    return

rospy.init_node('global_pose_node',anonymous=True)
rate = rospy.Rate(10)


Build_Pub()
OP = input('command:')
while(OP != 'Stop'):
    if OP == 'Start':
        STOP_Flag = False
        t = threading.Thread(target=tread_Pub_Process, args=(Pub_List,))
        t.start()
    if OP == 'Stop_Pub':
        STOP_Flag = True
        t.join()
    if OP == 'Rebuild':
        Close_Pub()
        Build_Pub()
    OP = input('command:')
    
STOP_Flag = True
Close_Pub()
t.join()
