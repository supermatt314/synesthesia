'''
Created on Jul 6, 2013

@author: matt
'''

import math
import pyglet
import style

class MIDIObjectException(Exception):
    pass

class Animator(object):
    def __init__(self,midi_object,data):
        self.midi_clock = midi_object.midi_clock
        self.vertex_list = midi_object.vertex_list
        self.vertex_list_size = self.vertex_list.get_size()        
        self.fps = 60
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
            
class MIDIVisualObject(object):
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
        elif self.shape == 'diamond':
            self._make_diamond()
        else:
            raise MIDIObjectException('Unknown MIDI shape:',self.shape)

        self.vertex_list = self.batch.add_indexed( self.v_count, self.mode, self.group, self.v_index, 
                                          (self.vertex_format, self.vertices),
                                          (self.color_format , self.v_colors)  )
        self.on_time = None
        self.off_time = None
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
        
    def _make_diamond(self):
        h = self.height
        w = self.width
        v1 = (0,0)
        v2 = (w/2,h/2)
        v3 = (w/2,-h/2)
        v4 = (w,0)
        
        self.vertices = v1+v2+v3+v4
        self.v_count = 4
        self.v_colors = [255,0,0,255]*self.v_count #default color        
        self.v_index = [0,1,2,1,2,3]

class Song(object):
    '''
    Data object for entire song
    '''
    def __init__(self):
        self.track_list = []
        self.tempo_list = []
        self.global_min_note = 128
        self.global_max_note = -1
        self.global_offset = 0
        self.midi_file = None
        self.mp3_file = None
        self.mp3_delay = 0
        self.window_width = 0
        self.window_height = 0
        self.unk_track_index = 0
        
    def register_track(self,track_data):
        new_track = Track(self,track_data)
        self.track_list.append(new_track)
        
    def register_tempo(self,time,data):
        new_tempo = Tempo(self,time,data)
        self.tempo_list.append(new_tempo)
        sorted(self.tempo_list, key=lambda k: k.midi_tick)
        for tempo in self.tempo_list:
            tempo.is_first = False
        self.tempo_list[0].is_first = True
        
    def set_background_color(self,bg_color):
        self.bg_color = bg_color
        
    def set_global_note_bounds(self):
        for track in self.track_list:
            self.global_max_note = max(track.max_note,self.global_max_note)
            self.global_min_note = min(track.min_note,self.global_min_note)
        
    def set_global_offset(self):
        for track in self.track_list:
            if track.style in style.style_list.keys():
                if style.style_list[track.style].is_scrolling:
                    self.global_offset = max(track.scroll_on_amount,self.global_offset)
            else:
                raise MIDIObjectException('Style {} not found'.format(track.style))
    
    def set_midi_file(self, midi_file):
        self.midi_file = midi_file
        
    def set_mp3_delay(self,delay):
        if delay < 0:
            raise MIDIObjectException('MP3 delay less than zero')
        else:
            self.mp3_delay = delay        
        
    def set_mp3_file(self, mp3_file):
        self.mp3_file = mp3_file

    def set_window_dimensions(self, window):
        self.window_height = window.height
        self.window_width = window.width
        
    def setup_visuals(self, batch, midi_clock):
        self.batch = batch
        self.midi_clock = midi_clock
        for track in self.track_list:
            if track.style in style.style_list.keys():
                style.style_list[track.style].draw_function(track)
            else:
                raise MIDIObjectException('Style {} not found'.format(track.style))
        
    def get_track_by_index(self, index):
        for track in self.track_list:
            if track.index == index:
                return track
        else:
            raise MIDIObjectException('No track found with index:', index)
        
class Track(object):
    '''
    Data object for track
    '''
    def __init__(self,parent,track_data):
        self.parent_song = parent
        self.index = track_data.index
        self.note_list = []
        self.volume_list = []
        self.min_note = 128
        self.max_note = -1
        for e in track_data.events:
            if e.type == 'SEQUENCE_TRACK_NAME':
                self.name = e.data.replace(b' ',b'_')
                break
        else:
            self.name = 'Unknown_Name_{}'.format(self.parent_song.unk_track_index)
            self.parent_song.unk_track_index += 1
            
        #=======================================================================
        # self.type = 'none'
        # self.shape = 'rectangle'
        # self.size = 12
        # self.color = [255,0,0,255]
        #=======================================================================
        self.z_order = 255
        self.style = 'none'
        self.style_parameters = {}
            
    def register_note(self,note_data):
        new_note = Note(self,note_data)
        self.note_list.append(new_note)
        self.min_note = min(new_note.pitch,self.min_note)
        self.max_note = max(new_note.pitch,self.max_note)
        
    #===========================================================================
    # def setup_visuals(self, batch, midi_clock):
    #     self.batch = batch
    #     self.midi_clock = midi_clock
    #     self.group = pyglet.graphics.OrderedGroup(self.z_order)
    #     if self.type == 'none':
    #         return
    #     elif self.type == 'piano_roll':
    #         self._visuals_piano_roll()
    #     elif self.type == 'static':
    #         self._visuals_static()
    #     else:
    #         raise MIDIObjectException('Unknown track type', self.type)
    #===========================================================================
        
    def set_user_data(self,u):
        '''
        Sets the user data for a track
        User data follows structure of default_config.ini
        '''
        self.z_order = u['z_order']
        self.style = u['style']
        self.style_parameters = u['style_parameters']
        if self.style in style.style_list.keys():
            style.style_list[self.style].validate(self)
        else:
            raise MIDIObjectException('Style {} not found'.format(self.style))
        ### validate style parameters, set up track offsets
        #=======================================================================
        # self.type = u['type']       
        # self.shape = u['shape']
        # self.size = u['size']
        # self.color = u['color']
        # self.z_order = u['z_order']
        # if self.type == 'piano_roll':
        #     if u['min_screen_region']:
        #         self.min_screen_region = u['min_screen_region']
        #     else:
        #         self.min_screen_region = 20
        #     if u['max_screen_region']:
        #         self.max_screen_region = u['max_screen_region']
        #     else:
        #         self.max_screen_region = self.parent_song.window_height - 20 
        #     if u['speed']:
        #         self.speed = u['speed']
        #     else:
        #         self.speed = 1
        #     if u['hit_line_percent']:
        #         self.hit_line_percent = u['hit_line_percent']
        #     else:
        #         self.hit_line_percent = 0.5
        #     if u['scale_by_note_length']:
        #         self.scale_note_length = u['scale_by_note_length']
        #     else:
        #         self.scale_note_length = True
        #         
        #     self.scroll_on_amount  = self.parent_song.window_width/self.speed * (1-self.hit_line_percent)
        #     self.scroll_off_amount = self.parent_song.window_width/self.speed * (self.hit_line_percent)
        #         
        # self.animation = u['animation_data']
        #=======================================================================
        
    def _visuals_piano_roll(self):
        global_min_note = self.parent_song.global_min_note
        global_max_note = self.parent_song.global_max_note
        offset = self.parent_song.global_offset
        for note in self.note_list:
            if self.scale_note_length:
                width = (note.time_off-note.time_on) * self.speed
            else:
                width = self.size*note.velocity/100
            object_data = {'shape': self.shape,
                           'height': self.size*note.velocity/100,
                           'width': width
                          }
            current_object = MIDIVisualObject(self.batch,self.group,self.midi_clock,object_data)
            x = self.parent_song.window_width
            y = (note.pitch - global_min_note)/(global_max_note - global_min_note) \
                *(self.max_screen_region-self.min_screen_region) + self.min_screen_region
            current_object.set_position(x, y)
            current_object.set_timing(note.time_on+offset, note.time_off+offset)
            current_object.set_color(self.color)
            animation_data = [{'type':'scroll',
                               'scroll_on_time': note.time_on - self.scroll_on_amount + offset,
                               'scroll_off_time': note.time_off + self.scroll_off_amount + offset,
                               'scroll_speed': -self.speed
                              },
                              {'type':'highlight',
                               'highlight_on_color': self.animation['highlight_on_color'],
                               'highlight_off_color': self.animation['highlight_off_color']
                              }
                             ]
            current_object.set_animations(animation_data)
    def _visuals_static(self):
        pass

class Note(object):
    '''
    Data object for individual note
    '''
    def __init__(self,track,note_data):
        self.parent_track = track
        self.track_index = note_data['track_no']
        if self.parent_track.index != self.track_index:
            raise MIDIObjectException('track number mismatch')
                
        self.channel = note_data['channel']
        self.pitch = note_data['pitch']
        self.velocity = note_data['velocity']
        self.time_on = note_data['time_on']
        self.time_off = note_data['time_off']
        
class Tempo(object):
    '''
    Data object for tempo change
    '''
    def __init__(self,parent,time,data):
        self.parent_song = parent
        self.is_first = False
        self.midi_tick = time
        self.tempo_raw = data
        mpqn = int.from_bytes(data, 'big') #microseconds per quarter note
        self.tempo = int(round(60000000/mpqn,0)) # convert MIDI's ridiculous tempo numbers into beats per minute
        
    def schedule_tempo(self,midi_clock):
        if self.is_first:
            midi_clock.schedule_once(midi_clock.change_tempo, self.midi_tick, self.tempo)
        else:
            midi_clock.schedule_once(midi_clock.change_tempo, self.midi_tick+self.parent_song.global_offset, self.tempo)
    
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
            