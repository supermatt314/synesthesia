'''
Created on May 8, 2014

@author: Matt

Creates the following attributes for the provided MIDI Visual Object:
vertices - list of (x,y) vertex coordinates
           size 2n where n=number of vertices
v_count  - number of vertices, used by pyglet
v_colors - list of RGBA colors for each vertex
           size 4n where n=number of vertices
v_index  - list where entries are indices to vertices
           used by pyglet making indexed vertex lists
           size 3m where m=number of triangles of the object

Inputs: MIDIVisualObject
        'height' - float
        'width' - float
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
    midi_obj.vertices = [0,0]
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
    
def star(midi_obj, h, w):
    b = h/2
    a = w/2
    n = 30 # number of outer points
    midi_obj.v_count = n+1
    midi_obj.v_colors = [255,0,0,255]*midi_obj.v_count        
    midi_obj.vertices = [0,0]
    for i in range(n):
        x = a*math.cos(2*math.pi/n*i)**3
        y = b*math.sin(2*math.pi/n*i)**3
        midi_obj.vertices.extend([x,y])
    midi_obj.v_index = []
    for i in range(1,n):
        midi_obj.v_index.extend([0,i,i+1])
    midi_obj.v_index.extend([0,n,1])
    
def hexagon(midi_obj, h, w):
    if h == w: # hexagon degenerates to diamond if h = w
        diamond(midi_obj, h, w)
    elif h < w:
        v1 = (-w/2,0)
        v2 = (-w/2+h/2,h/2)
        v3 = (w/2-h/2,h/2)
        v4 = (w/2,0)
        v5 = (w/2-h/2,-h/2)
        v6 = (-w/2+h/2,-h/2)
    else: # h > w
        v1 = (0,h/2)
        v2 = (w/2,h/2-w/2)
        v3 = (w/2,-h/2+w/2)
        v4 = (0,-h/2)
        v5 = (-w/2,-h/2+w/2)
        v6 = (-w/2,h/2-w/2)
    midi_obj.v_count = 6
    midi_obj.v_colors = [255,0,0,255]*midi_obj.v_count
    midi_obj.vertices = v1+v2+v3+v4+v5+v6
    midi_obj.v_index = [0,1,2,0,2,3,0,3,4,0,4,5]
        