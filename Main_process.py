# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 10:52:14 2020

@author: BreezeCat
"""

IS_ROS = False
deltaT = 0.1
import math

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

def Calculate_distance(x1, y1, x2, y2):
    return math.sqrt(math.pow( (x1-x2) , 2) + math.pow( (y1-y2) , 2))

def Check_Goal(agent, position_tolerance, orientation_tolerance):    
    position_error = Calculate_distance(agent.state.Px, agent.state.Py, agent.gx, agent.gy)
    orientation_error = abs(agent.state.Pth - agent.gth)
    if (position_error < position_tolerance) and (orientation_error < orientation_tolerance):
        return True
    else:
        return False


if not IS_ROS:
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
   
      
    
    def Sim_Process(main_agent, save_path):
        time = 0
        while not Navigation_core.Check_Goal(main_agent, 0.2, 3.14/15):
            if main_agent.state.Px < 1:
                Virtual_Agent, FV, VVO = geo_virtual_robot.Virtual_Agent_func(main_agent, 1, 1, Map, mode='Vel')
                while len(Virtual_Agent) < 1:
                    print('empty')
                    Virtual_Agent.append(Agent.Agent('empty',-5,-5,0,0,0,0.2,-5,-5,0,3,mode='Static'))
                    
                All_Agent_list = [main_agent] + Virtual_Agent
                
            else:
                Virtual_Agent, FV, VVO = geo_virtual_robot.Virtual_Agent_func(main_agent, 1, 1, Map, mode='VelY')
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
        main_agent.Record_data(save_path)
        return


else:
    Main_name = input('name: ')    
    
    import Agent
    import Communication_func as Comm
    import copy
    import json
    import rospy
    from geometry_msgs.msg import Twist
    from std_msgs.msg import Bool
    start_flag = False
    robot_cmd_vel = rospy.Publisher("/"+Main_name+"/cmd_vel", Twist, queue_size=10)
    Cmd_Vel = Twist()
    Main_agent = Agent.Agent(Main_name, 0, 0, 0, 0, 0, 0.2, 0, 0, 0, 1)
    Other_agent_list = [Agent.Agent('test1', -3, 1, 0, 0, 0, 0.2, 0, 0, 0, 1), Agent.Agent('test2', -3, -1, 0, 0, 0, 0.2, 0, 0, 0, 1)]
    
    def Command_CB(data):
        V_cmd, W_cmd = Saturation(data['V'], data['W'], 0.5, 1)
        Cmd_Vel.linear.x = V_cmd
        Cmd_Vel.angular.z = W_cmd
        robot_cmd_vel.publish(Cmd_Vel)
        return
        
    def Pose_CB(data):
        global Main_agent
        Main_agent.state.Px, Main_agent.state.Py, Main_agent.state.Pth = data.linear.x, data.linear.y, data.angular.z
        Main_agent.Path.append(copy.deepcopy(Main_agent.state))        
        return        
    
    def Set_Main_Agent():
        global Main_agent
        Main_agent.state.Px = float(input('Px: '))
        Main_agent.state.Py = float(input('Py: '))
        Main_agent.state.Pth = float(input('Pth: '))
        Main_agent.gx = float(input('gx: '))
        Main_agent.gy = float(input('gy: '))
        Main_agent.gth = float(input('gth: '))
        Main_agent.rank = int(input('rank: '))

    def Navi_process(Nav_sub):
        data = {}
        data['header'] = 'Message'
        data['main_agent_name'] = Main_agent.name
        data['agent_num'] = len(Other_agent_list) + 1
        data['Agent_data'] = [Main_agent.Transform_to_Dict()]
        for agent in Other_agent_list:
            data['Agent_data'].append(agent.Transform_to_Dict())        
        jdata = json.dumps(data)
        Nav_sub.socket.settimeout(3)
        Nav_sub.socket.send(jdata.encode())
        Nav_sub.socket.settimeout(None)
        return
    
    def Other_Set_Callback(data):
        global Other_agent_list
        Other_agent_list = []
        Agent_data = data['Agent_data']
        for agent_dict in Agent_data:
            agent = Agent.DicttoAgent(agent_dict)
            if agent.name != Main_name:
                Other_agent_list.append(agent)
                
    def Flag_CB(data):
        global start_flag 
        start_flag = data
        if start_flag:
            print('mission start!')
        else:
            print('mission pause!')

    
    if __name__ == '__main__':
        rospy.init_node('navi_node_'+Main_name,anonymous=True)
        rate = rospy.Rate(10)
        pose_sub = rospy.Subscriber("/"+Main_name+"/robot_pose",Twist,Pose_CB)
        flag_sub = rospy.Subscriber("/start_flag",Bool,Flag_CB)
                
        Set_Main_Agent()

        OP = input('Command: ')
        while(OP != 'Continue'):
            if OP == 'Connect':
                sub = Comm.Subscriber('127.0.0.1',12346, cb_func=Command_CB)
                sub.connect()
                t = sub.background_callback()
            if OP == 'Connect2':
                sub2 = Comm.Subscriber('192.168.0.134',12340+int(Main_name[-1]), cb_func=Other_Set_Callback)
                sub2.connect()
                t2 = sub2.background_callback()
            OP = input('Command: ')
        
        while not rospy.is_shutdown():
            if start_flag:
                if Check_Goal(Main_agent, Calculate_distance(0.1, 0.1, 0, 0), math.pi/15):
                    print('Arrived!')
                    Command_CB({'V':0, 'W':0})
                else:
                    Navi_process(sub)
            rate.sleep()
        
        
        sub.socket.close()




        
