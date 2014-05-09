'''
Created on May 8, 2014

@author: Matt

Contains functions to generate shapes of midi objects

Inputs: MIDIVisualObject
        'height' - string
        'width' - string
Outputs: none
'''

import math

def rectangle(midi_obj, h, w):
    v1 = (-w/2,-h/2)
    v2 = (-w/2, h/2)
    v3 = (w/2,-h/2)
    v4 = (w/2, h/2)
    
    midi_obj.vertices = v1+v2+v3+v4
    midi_obj.v_count = 4
    midi_obj.v_colors = [255,0,0,255]*midi_obj.v_count #placeholder color        
    midi_obj.v_index = [0,1,2,1,2,3]    

def ellipse(midi_obj, h, w):
    b = h/2
    a = w/2
    n = 30 # number of outer points
    midi_obj.v_count = n+1
    midi_obj.v_colors = [255,0,0,255]*midi_obj.v_count        
    midi_obj.vertices = [a,0]
    for i in range(n):
        x = a*math.cos(2*math.pi/n*i)
        y = b*math.sin(2*math.pi/n*i)
        midi_obj.vertices.extend([x,y])
    midi_obj.v_index = []
    for i in range(1,n):
        midi_obj.v_index.extend([0,i,i+1])
    midi_obj.v_index.extend([0,n,1])
    
def diamond(midi_obj, h, w):
    v1 = (-w/2,0)
    v2 = (0,h/2)
    v3 = (0,-h/2)
    v4 = (w/2,0)
    
    midi_obj.vertices = v1+v2+v3+v4
    midi_obj.v_count = 4
    midi_obj.v_colors = [255,0,0,255]*midi_obj.v_count #default color        
    midi_obj.v_index = [0,1,2,1,2,3]