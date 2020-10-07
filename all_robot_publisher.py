# -*- coding: utf-8 -*-
"""
Created on Wed Oct  7 15:38:04 2020

@author: BreezeCat
"""

import rospy
import Agent
import Communication_func as Comm
import json
from geometry_msgs.msg import Twist

name_list = ['robot1','robot2','robot3']
Agent_list = []
for name in name_list:
    Agent_list.append(Agent.Agent(name, -5, 5, 0, 0, 0, 0.2, 0, 0, 0, 1))


def Pose1_CB(data):
    for agent in Agent_list:
        if agent.name == 'robot1':
            agent.state.Px, agent.state.Py, agent.state.Pth = data.linear.x, data.linear.y, data.angular.z

def Pose2_CB(data):
    for agent in Agent_list:
        if agent.name == 'robot2':
            agent.state.Px, agent.state.Py, agent.state.Pth = data.linear.x, data.linear.y, data.angular.z
            
def Pose3_CB(data):
    for agent in Agent_list:
        if agent.name == 'robot3':
            agent.state.Px, agent.state.Py, agent.state.Pth = data.linear.x, data.linear.y, data.angular.z
            
def Pub_process(pub_list):
        data = {}
        data['header'] = 'Message'
        data['Agent_data'] = []
        for agent in Agent_list:
            data['Agent_data'].append(agent.Transform_to_Dict())        
        jdata = json.dumps(data)
        for pub in pub_list:
            pub.publish_msg(jdata)
        return
            
rospy.init_node('global_pose_node',anonymous=True)
rate = rospy.Rate(10)
pose1_sub = rospy.Subscriber("/robot1/robot_pose",Twist,Pose1_CB)
pose2_sub = rospy.Subscriber("/robot2/robot_pose",Twist,Pose2_CB)
pose3_sub = rospy.Subscriber("/robot3/robot_pose",Twist,Pose3_CB)


agent1_pub = Comm.Publisher('192.168.0.134',12341)
agent1_pub.set_pub()
agent1_pub.wait_connect() 

agent2_pub = Comm.Publisher('192.168.0.134',12342)
agent2_pub.set_pub()
agent2_pub.wait_connect() 

agent3_pub = Comm.Publisher('192.168.0.134',12343)
agent3_pub.set_pub()
agent3_pub.wait_connect()

OP = input('command:')
while(OP != 'Start'):
    OP = input('command:')

while not rospy.is_shutdown():
    Pub_process([agent1_pub, agent2_pub, agent3_pub])
    rate.sleep()

agent1_pub.socket.close()
agent2_pub.socket.close()
agent3_pub.socket.close()