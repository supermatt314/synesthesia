'''
Created on Jul 6, 2013

@author: matt
'''

import math
import pyglet

class MIDIObjectException(Exception):
    pass

class Animator(object):
    def __init__(self,midi_object,data):
        self.midi_clock = midi_object.midi_clock
        self.vertex_list = midi_object.vertex_list
        self.vertex_list_size = self.vertex_list.get_size()        
        self.fps = 30
        self.data = data
    def start_animation(self,dt): # Used to start ticking animations
        pass
    def animate(self,dt):
        pass
    def stop_animation(self,dt): # Used to stop ticking animations
        pass

class Highlighter(Animator):
    # Highlights object at specified times    
    def __init__(self,midi_object,data):
        Animator.__init__(self,midi_object,data)
        self.midi_clock.schedule_once(self.animate, midi_object.on_time, self.data['highlight_on_color'])
        self.midi_clock.schedule_once(self.animate, midi_object.off_time, self.data['highlight_off_color'])
        
    def animate(self,dt,new_color):
        # Assumes alpha channel present, new color must be list/tuple of 4 ints
        for i in range(self.vertex_list_size):
            self.vertex_list.colors[4*i]   = new_color[0]
            self.vertex_list.colors[4*i+1] = new_color[1]
            self.vertex_list.colors[4*i+2] = new_color[2]            
            self.vertex_list.colors[4*i+3] = new_color[3]
      
class Scroller(Animator):
    # Scrolls a vertex list by scroll speed
    def __init__(self,midi_object,data):
        Animator.__init__(self,midi_object,data)
        self.midi_clock.schedule_once(self.start_animation, self.data['scroll_on_time'])
        self.midi_clock.schedule_once(self.stop_animation, self.data['scroll_off_time']+50)
        
    def start_animation(self,dt):
        self.midi_clock.schedule_interval(self.animate, 1/self.fps, self.data['scroll_speed'])
        
    def animate(self,dt,scroll_speed):
        for i in range(self.vertex_list_size):
            self.vertex_list.vertices[2*i] += scroll_speed * dt
            
    def stop_animation(self,dt):
        self.midi_clock.unschedule(self.animate)

'''------------------------------------------------------'''
            
class MIDIObject(object):
    def __init__(self, batch, group, midi_clock, data):
        self.batch = batch
        self.group = group
        self.midi_clock = midi_clock
        self.shape = data['shape']
        self.height = data['height']
        self.width = data['width']
        self.vertex_format = 'v2f'
        self.color_format = 'c4B'
        self.mode = pyglet.gl.GL_TRIANGLES #default mode
        if self.shape == 'rectangle':
            self._make_rectangle()
        elif self.shape == 'ellipse':
            self._make_ellipse()
        else:
            raise MIDIObjectException('Unknown MIDI shape:',self.shape)
        #=======================================================================
        # self.v_count = 0
        # self.v_index = []
        # self.vertices = ()
        # self.v_colors = ()
        #=======================================================================
        self.vertex_list = self.batch.add_indexed( self.v_count, self.mode, self.group, self.v_index, 
                                          (self.vertex_format, self.vertices),
                                          (self.color_format , self.v_colors)  )
        self.on_time = 0
        self.off_time = 0
        self.x = 0
        self.y = 0        

    def set_position(self, x, y):
        '''
        Sets position of MIDI object at coordinates (x,y)
        Position is relative to center of left edge of bounding box
        of object
        '''
        self.x = x
        self.y = y
        for i in range(self.vertex_list.get_size()):
            self.vertex_list.vertices[2*i]   = x + self.vertices[2*i]
            self.vertex_list.vertices[2*i+1] = y + self.vertices[2*i+1]
    
    def set_color(self, color_list):
        '''
        color_list: 3 (RGB) or 4 (RGBA) length list
        If Alpha is not given, default to max opacity 255
        '''
        if len(color_list) == 3:
            color_list[3] = 255
        for i in range(self.vertex_list.get_size()):
            self.vertex_list.colors[4*i]   = color_list[0]
            self.vertex_list.colors[4*i+1] = color_list[1]
            self.vertex_list.colors[4*i+2] = color_list[2]            
            self.vertex_list.colors[4*i+3] = color_list[3]
            
    def set_timing(self, on_time, off_time):
        self.on_time = on_time
        self.off_time = off_time
            
    def set_animations(self, animation_list):
        for animation in animation_list:
            if animation['type'] == 'scroll':
                self.scroller = Scroller(self, animation)
            elif animation['type'] == 'highlight':
                self.highlighter = Highlighter(self, animation)
            elif animation['type'] == 'fade':
                #fade
                pass
            else:
                raise MIDIObjectException('Unknown animation type',animation['type'])
        
        
    def _make_rectangle(self):
        h = self.height
        w = self.width
        v1 = (0,-h/2)
        v2 = (0, h/2)
        v3 = (w,-h/2)
        v4 = (w, h/2)
        
        self.vertices = v1+v2+v3+v4
        self.v_count = 4
        self.v_colors = [255,0,0,255]*self.v_count #default color        
        self.v_index = [0,1,2,1,2,3]    

    def _make_ellipse(self):
        b = self.height/2
        a = self.width/2
        n = 20 # number of outer points
        self.v_count = n+1
        self.v_colors = [255,0,0,255]*self.v_count        
        self.vertices = [a,0]
        for i in range(n): # top half of ellipse
            x = a*math.cos(2*math.pi/n*i)
            y = b*math.sin(2*math.pi/n*i)
            self.vertices.extend([x+a,y])
        self.v_index = []
        for i in range(1,n):
            self.v_index.extend([0,i,i+1])
        self.v_index.extend([0,n,1])
#===============================================================================
# class Background(DrawablePrimitiveObject):
#     def __init__(self, batch, group, clock, data):
#         DrawablePrimitiveObject.__init__(self, batch, group, clock, data)
#         self.vertex_format = 'v2f/static'
#         make_rectangle(self)
#         self.vertex_list = self.batch.add_indexed( self.v_count, self.mode, self.group, self.v_index, 
#                                           (self.vertex_format, self.vertices),
#                                           (self.color_format , self.v_colors)  )
#         
# class PianoRollObject(DrawablePrimitiveObject):
#     def __init__(self, batch, group, clock, data):
#         DrawablePrimitiveObject.__init__(self, batch, group, clock, data)
#         self.vertex_format = 'v2f/stream'      
#             
#         if self.m_data['shape'] == 'rectangle':
#             make_rectangle(self)
#         else:
#             make_rectangle(self)
#         
#         self.vertex_list = self.batch.add_indexed( self.v_count, self.mode, self.group, self.v_index, 
#                                           (self.vertex_format, self.vertices),
#                                           (self.color_format , self.v_colors)  )
#         self.scroller = Scroller(self.midi_clock, self.vertex_list, self.data)
#         if 'highlight' in self.a_data['hit_animations']:
#             self.highlighter = Highlighter(self.midi_clock, self.vertex_list, self.data)
#===============================================================================


# class ThickBezier(DrawablePrimitiveObject):
#     '''
#     Create Bezier Curve with flat slope at each node
#     '''
#     def __init__(self,group,batch,midi_clock,point_list,width=5,color=(255,0,0,255)):
#         DrawablePrimitiveObject.__init__(self,group,batch,midi_clock)
#         self.mode = pyglet.gl.GL_TRIANGLE_STRIP
#         for i in range(len(point_list)-1):
#             P0 = point_list[i]
#             P3 = point_list[i+1]
#             P1 = ((P3[0]+P0[0])/2, P0[1])
#             P2 = ((P3[0]+P0[0])/2, P3[1])
#             C0x, C0y =  1*P0[0]                               ,  1*P0[1]
#             C1x, C1y = -3*P0[0] + 3*P1[0]                     , -3*P0[1] + 3*P1[1]
#             C2x, C2y =  3*P0[0] - 6*P1[0] + 3*P2[0]           ,  3*P0[1] - 6*P1[1] + 3*P2[1]
#             C3x, C3y = -1*P0[0] + 3*P1[0] - 3*P2[0] + 1*P3[0] , -1*P0[1] + 3*P1[1] - 3*P2[1] + 1*P3[1]
#             
#             Cp0x, Cp0y = -3*P0[0] +  3*P1[0]                     , -3*P0[1] +  3*P1[1]
#             Cp1x, Cp1y =  6*P0[0] - 12*P1[0] + 6*P2[0]           ,  6*P0[1] - 12*P1[1] + 6*P2[1]
#             Cp2x, Cp2y = -3*P0[0] +  9*P1[0] - 9*P2[0] + 3*P3[0] , -3*P0[1] +  9*P1[1] - 9*P2[1] + 3*P3[1]
#             
#             t = 0
#             while t <= 1.0:
#                 Bx  = C0x  + C1x *t + C2x *t**2 + C3x*t**3
#                 By  = C0y  + C1y *t + C2y *t**2 + C3y*t**3
#                 Bpx = Cp0x + Cp1x*t + Cp2x*t**2
#                 Bpy = Cp0y + Cp1y*t + Cp2y*t**2
#                 
#                 Bnorm = sqrt(Bpx**2 + Bpy**2)
#                 Nx =  Bpy / Bnorm
#                 Ny = -Bpx / Bnorm
#                 
#                 vertex_1 = (Bx+width*Nx,By+width*Ny)
#                 vertex_2 = (Bx-width*Nx,By-width*Ny)
#                 self.vertices.extend(vertex_1+vertex_2)
#                 self.count += 2
#                 
#                 t += 0.01
#                 
#         self.v_colors.extend(color*self.count)
            