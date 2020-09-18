# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 11:57:10 2020

@author: BreezeCat
"""

import numpy as np
import json

def relu(X):
    return np.maximum(0,X)

def sigmoid(X):
    return 1/(1+np.exp(-X))

def tanh(X):
    return (np.exp(X) - np.exp(-X))/(np.exp(X) + np.exp(-X))


class Two_robot_network():
    def __init__(self):
        self.W1, self.W2, self.W3, self.W4, self.Wf = 0, 0, 0, 0, 0
        self.B1, self.B2, self.B3, self.B4, self.Bf = 0, 0, 0, 0, 0
        self.act_f1, self.act_f2, self.act_f3, self.act_f4, self.act_ff = relu, relu, relu, sigmoid, tanh
        
    def load_parameter(self, parameter_file):
        with open(parameter_file) as f:
            para_dict = json.load(f)
        self.W1, self.W2, self.W3, self.W4, self.Wf = np.array(para_dict['W1']), np.array(para_dict['W2']), np.array(para_dict['W3']), np.array(para_dict['W4']), np.array(para_dict['Wf'])
        self.B1, self.B2, self.B3, self.B4, self.Bf = np.array(para_dict['B1']), np.array(para_dict['B2']), np.array(para_dict['B3']), np.array(para_dict['B4']), np.array(para_dict['Bf'])
        
    def get_value(self, state):
        H1 = self.act_f1(state.dot(self.W1)+self.B1)
        H2 = self.act_f2(H1.dot(self.W2)+self.B2)
        H3 = self.act_f3(H2.dot(self.W3)+self.B3)
        H4 = self.act_f4(H3.dot(self.W4)+self.B4)
        value = self.act_ff(H4.dot(self.Wf)+self.Bf)
        return value
        
    
    
class Three_robot_network():
    def __init__(self):
        self.W1, self.W2, self.W3, self.W4, self.Wf = 0, 0, 0, 0, 0
        self.B1, self.B2, self.B3, self.B4, self.Bf = 0, 0, 0, 0, 0
        self.act_f1, self.act_f2, self.act_f3, self.act_f4, self.act_ff = relu, relu, relu, sigmoid, tanh
        
    def load_parameter(self, parameter_file):
        with open(parameter_file) as f:
            para_dict = json.load(f)
        self.W1, self.W2, self.W3, self.W4, self.Wf = np.array(para_dict['W1']), np.array(para_dict['W2']), np.array(para_dict['W3']), np.array(para_dict['W4']), np.array(para_dict['Wf'])
        self.B1, self.B2, self.B3, self.B4, self.Bf = np.array(para_dict['B1']), np.array(para_dict['B2']), np.array(para_dict['B3']), np.array(para_dict['B4']), np.array(para_dict['Bf'])
        
    def get_value(self, state):
        H1 = self.act_f1(state.dot(self.W1)+self.B1)
        H2 = self.act_f2(H1.dot(self.W2)+self.B2)
        H3 = self.act_f3(H2.dot(self.W3)+self.B3)
        H4 = self.act_f4(H3.dot(self.W4)+self.B4)
        value = self.act_ff(H4.dot(self.Wf)+self.Bf)
        return value
    
class Four_robot_network():
    def __init__(self):
        self.W1, self.W2, self.W3, self.W4, self.Wf = 0, 0, 0, 0, 0
        self.B1, self.B2, self.B3, self.B4, self.Bf = 0, 0, 0, 0, 0
        self.act_f1, self.act_f2, self.act_f3, self.act_f4, self.act_ff = relu, relu, relu, sigmoid, tanh
        
    def load_parameter(self, parameter_file):
        with open(parameter_file) as f:
            para_dict = json.load(f)
        self.W1, self.W2, self.W3, self.W4, self.Wf = np.array(para_dict['W1']), np.array(para_dict['W2']), np.array(para_dict['W3']), np.array(para_dict['W4']), np.array(para_dict['Wf'])
        self.B1, self.B2, self.B3, self.B4, self.Bf = np.array(para_dict['B1']), np.array(para_dict['B2']), np.array(para_dict['B3']), np.array(para_dict['B4']), np.array(para_dict['Bf'])
        
    def get_value(self, state):
        H1 = self.act_f1(state.dot(self.W1)+self.B1)
        H2 = self.act_f2(H1.dot(self.W2)+self.B2)
        H3 = self.act_f3(H2.dot(self.W3)+self.B3)
        H4 = self.act_f4(H3.dot(self.W4)+self.B4)
        value = self.act_ff(H4.dot(self.Wf)+self.Bf)
        return value
    
    
    
    
    
        
Network_Dict = {'2': Two_robot_network, 
                '3': Three_robot_network,
                '4': Four_robot_network
        }
        