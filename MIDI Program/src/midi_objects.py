'''
Created on Jul 6, 2013

@author: matt
'''


#from math import sqrt
import pyglet

class Animator(object):
    def __init__(self,midi_clock,vertex_list,data):
        self.midi_clock = midi_clock
        self.vertex_list = vertex_list
        self.vertex_list_size = self.vertex_list.get_size()        
        self.fps = 60 # frames of animation per midi tick
        self.a_data = data['animation']
        self.m_data = data['morph']
        self.t_data = data['timing']
    def start_animation(self,dt): # Used to start ticking animations
        pass
    def animate(self,dt):
        pass
    def stop_animation(self,dt): # Used to stop ticking animations
        pass

class Highlighter(Animator):
    # Highlights object at specified times    
    def __init__(self,midi_clock,vertex_list,data):
        Animator.__init__(self,midi_clock,vertex_list,data)
        self.midi_clock.schedule_once(self.animate, self.t_data['time_on'], self.a_data['highlight_on_color'])
        self.midi_clock.schedule_once(self.animate, self.t_data['time_off'], self.a_data['highlight_off_color'])
        
    def animate(self,dt,new_color):
        # Assumes alpha channel present, new color must be list/tuple of 4 ints
        for i in range(self.vertex_list_size):
            self.vertex_list.colors[4*i]   = new_color[0]
            self.vertex_list.colors[4*i+1] = new_color[1]
            self.vertex_list.colors[4*i+2] = new_color[2]            
            self.vertex_list.colors[4*i+3] = new_color[3]
      
class Scroller(Animator):
    # Scrolls a vertex list by scroll speed
    def __init__(self,midi_clock,vertex_list,data):
        Animator.__init__(self,midi_clock,vertex_list,data)
        self.midi_clock.schedule_once(self.start_animation, self.t_data['scroll_on_time'])
        self.midi_clock.schedule_once(self.stop_animation, self.t_data['scroll_off_time']+50)
        
    def start_animation(self,dt):
        self.midi_clock.schedule_interval(self.animate, 1/self.fps, self.a_data['scroll_speed'])
        
    def animate(self,dt,scroll_speed):
        for i in range(self.vertex_list_size):
            self.vertex_list.vertices[2*i] += scroll_speed * dt
            
    def stop_animation(self,dt):
        self.midi_clock.unschedule(self.animate)

'''------------------------------------------------------'''
            
class DrawablePrimitiveObject(object):
    def __init__(self, batch, group, midi_clock, data):
        self.batch = batch
        self.group = group
        self.midi_clock = midi_clock
        self.data = data
        self.a_data = data['animation']
        self.m_data = data['morph']
        self.p_data = data['position']
        self.t_data = data['timing']
        self.vertex_format = 'v2f'
        self.color_format = 'c4B'
        self.v_count = 0
        self.v_index = []
        self.vertices = ()
        self.v_colors = ()
        self.vertex_list = None
        self.mode = pyglet.gl.GL_TRIANGLES #default mode
        self.on_time = 0
        self.off_time = 0


class Background(DrawablePrimitiveObject):
    def __init__(self, batch, group, clock, data):
        DrawablePrimitiveObject.__init__(self, batch, group, clock, data)
        self.vertex_format = 'v2f/static'
        make_rectangle(self)
        self.vertex_list = self.batch.add_indexed( self.v_count, self.mode, self.group, self.v_index, 
                                          (self.vertex_format, self.vertices),
                                          (self.color_format , self.v_colors)  )
        
class PianoRollObject(DrawablePrimitiveObject):
    def __init__(self, batch, group, clock, data):
        DrawablePrimitiveObject.__init__(self, batch, group, clock, data)
        self.vertex_format = 'v2f/stream'      
            
        if self.m_data['shape'] == 'rectangle':
            make_rectangle(self)
        else:
            make_rectangle(self)
        
        self.vertex_list = self.batch.add_indexed( self.v_count, self.mode, self.group, self.v_index, 
                                          (self.vertex_format, self.vertices),
                                          (self.color_format , self.v_colors)  )
        self.scroller = Scroller(self.midi_clock, self.vertex_list, self.data)
        if 'highlight' in self.a_data['hit_animations']:
            self.highlighter = Highlighter(self.midi_clock, self.vertex_list, self.data)

def make_rectangle(n):
    x = n.p_data['x']
    y = n.p_data['y']
    h = n.m_data['height']
    w = n.m_data['width']
    v1 = (x,y)
    v2 = (x,y+h)
    v3 = (x+w,y)
    v4 = (x+w,y+h)
    
    n.vertices = v1+v2+v3+v4
    n.v_colors = n.m_data['color']*4
    n.v_count = 4
    n.v_index = [0,1,2,1,2,3]
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
            