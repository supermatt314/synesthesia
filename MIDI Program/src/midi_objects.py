'''
Created on Jul 6, 2013

@author: matt
'''


from math import sqrt

import pyglet


class Animator(object):
    def __init__(self,**data):
        self.fps = 20 # frames of animation per midi tick
        self.a_data = data['animation_data']
        self.n_data = data['note_data']
        self.s_data = data['song_data']
        self.t_data = data['track_data']        
    def start_animation(self,vertex_list):
        pass
    def animate(self,dt):
        pass
    def stop_animation(self):
        pass

class Highlighter(Animator):
    # Highlights object at specified times    
    def __init__(self,midi_clock,**data):
        Animator.__init__(self,**data)
        self.midi_clock = midi_clock
        # Times relative to note creation
        self.highlight_on =  self.t_data['scroll_on_time']
        self.highlight_off = self.n_data['time_off'] - self.n_data['time_on'] + self.t_data['scroll_on_time']

    def start_animation(self,vertex_list):
        self.midi_clock.schedule_once(self.animate, self.highlight_on, vertex_list, self.a_data['highlight_on_color'])
        self.midi_clock.schedule_once(self.animate, self.highlight_off, vertex_list, self.a_data['highlight_off_color'])
        
    def animate(self,dt,vertex_list,highlight_color):
        # Assumes alpha channel present, new color must be list/tuple of 4 ints
        size = vertex_list.get_size()
        for i in range(size):
            vertex_list.colors[4*i]   = highlight_color[0]
            vertex_list.colors[4*i+1] = highlight_color[1]
            vertex_list.colors[4*i+2] = highlight_color[2]            
            vertex_list.colors[4*i+3] = highlight_color[3]
      
class Scroller(Animator):
    # Scrolls a vertex list by scroll speed
    def __init__(self,midi_clock,**data):
        Animator.__init__(self,**data)
        self.midi_clock = midi_clock
        
    def start_animation(self,vertex_list):
        self.midi_clock.schedule_interval(self.animate, 1/self.fps, vertex_list, -self.t_data['speed'])
        
    def animate(self,dt,vertex_list,scroll_speed):
        scroll_amount = scroll_speed * dt
        for i in range(0,len(vertex_list.vertices),2):
            vertex_list.vertices[i] += scroll_amount

'''------------------------------------------------------'''
            
class DrawablePrimitiveObject(object):
    def __init__(self, batch, group, midi_clock):
        self.batch = batch
        self.group = group
        self.midi_clock = midi_clock
        self.animation_list = []
        self.vertex_format = 'v2f'
        self.color_format = 'c4B'
        self.v_count = 0
        self.vertices = []
        self.v_colors = []
        self.vertex_list = None
        self.mode = pyglet.gl.GL_TRIANGLES #default mode
        self.on_time = 0
        self.off_time = 0
        self.is_drawn = False
        
    def draw_object(self,dt):
        # Actually make the vertices of the object and set animations
        self.is_drawn = True
        self.vertex_list = self.batch.add( self.v_count, self.mode, self.group,
                                          (self.vertex_format, self.vertices),
                                          (self.color_format , self.v_colors)  )
        
    def delete_object(self,dt):
        # Turn off updating and delete object
        self.stop_object_animations()
        self.midi_clock.unschedule(self.draw_object)
        self.midi_clock.unschedule(self.delete_object)
        
        if self.is_drawn == True:
            self.is_drawn = False
            self.vertex_list.delete()

    def reset_object(self,new_clock):
        # Delete the current object and reschedule its draw and animation times
        self.delete_object(None)
        self.midi_clock = new_clock
        self.set_object_animations()
        self.set_draw_schedule(self.on_time, self.off_time)
        
    def set_draw_schedule(self,on_time,off_time):
        # Set times to draw and delete object
        self.on_time = on_time
        self.off_time = off_time
        self.midi_clock.schedule_once(self.draw_object, self.on_time-5)
        self.midi_clock.schedule_once(self.start_object_animations, self.on_time)
        self.midi_clock.schedule_once(self.delete_object, self.off_time)
        
    def set_object_animations(self):
        pass
    
    def start_object_animations(self,dt):
        for animator in self.animation_list:
            animator.start_animation(self.vertex_list)
                    
    def stop_object_animations(self):
        for animator in self.animation_list:
            self.midi_clock.unschedule(animator.start_animation)
            self.midi_clock.unschedule(animator.animate)
            self.midi_clock.unschedule(animator.stop_animation)

class Background(DrawablePrimitiveObject):
    def __init__(self, batch, group, clock, **data):
        DrawablePrimitiveObject.__init__(self, batch, group, clock)
        self.vertex_format = 'v2f/static'
        self.data = data
        v1 = (0,0)
        v2 = (0,self.data['window_height'])
        v3 = (self.data['window_width'],0)
        v4 = (self.data['window_width'],self.data['window_height'])
        self.vertices = v1+v2+v3+v2+v3+v4
        self.v_count = 6
        self.v_colors = self.data['color']*6
        self.set_draw_schedule(0, 1000000)
        
class PianoRollObject(DrawablePrimitiveObject):
    def __init__(self, batch, group, clock, **data):
        DrawablePrimitiveObject.__init__(self, batch, group, clock)
        self.vertex_format = 'v2f/stream'
        self.data = data        
            
        if self.data['track_data']['shape'] == 'rectangle':
            self.shape_class = Rectangle(**self.data)
        else:
            self.shape_class = Rectangle(**self.data)
        
        self.v_count = self.shape_class.v_count
        self.vertices = self.shape_class.vertices
        self.v_colors = self.shape_class.v_colors
        
        self.on_time = self.data['note_data']['time_on'] - self.data['track_data']['scroll_on_time'] + self.data['song_data']['offset']
        self.off_time = self.data['note_data']['time_off'] + self.data['track_data']['scroll_off_time'] + self.data['song_data']['offset']
        self.set_draw_schedule(self.on_time, self.off_time)
        self.set_object_animations()

    def set_object_animations(self):
        self.scroller = Scroller(self.midi_clock, **self.data)
        self.animation_list.append(self.scroller)
        
        if 'highlight' in self.data['animation_data']['hit_animations']:
            self.highlighter = Highlighter(self.midi_clock, **self.data)
            self.animation_list.append(self.highlighter)
            
class Rectangle(object):
    def __init__(self,**data): # note data, track data, screen data
        n_data = data['note_data']
        s_data = data['song_data']
        t_data = data['track_data']
        # Set default color
        height = n_data['velocity']/100 * t_data['size']
        width = (n_data['time_off']-n_data['time_on']) * t_data['speed']
        center_line = (n_data['pitch']-s_data['min_note'])/(s_data['max_note']-s_data['min_note']) \
                      *(s_data['window_height']-2*s_data['screen_buffer'])+s_data['screen_buffer']        
        corner1 = (s_data['window_width']        , center_line - height/2)
        corner2 = (s_data['window_width'] + width, center_line + height/2)
        v1 = (corner1[0], corner1[1])
        v2 = (corner1[0], corner2[1])
        v3 = (corner2[0], corner1[1])
        v4 = (corner2[0], corner2[1])
        self.vertices = v1+v2+v3+v2+v3+v4
        self.v_colors = t_data['color']*6
        self.v_count = 6


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
            