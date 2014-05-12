'''
Created on Jul 6, 2013

@author: matt
'''

import math
import pyglet
import shapes
import style

class MIDIObjectException(Exception):
    pass

class Animator(object):
    def __init__(self,midi_object):
        self.midi_clock = midi_object.midi_clock
        self.vertex_list = midi_object.vertex_list
        self.vertex_list_size = self.vertex_list.get_size()        
        self.fps = 60
        
class Fader(Animator):
    # Gradually changes color over time
    def __init__(self,midi_object,start_time,end_time,start_color,end_color,cancelling=False):
        Animator.__init__(self,midi_object)
        r_speed = (end_color[0]-start_color[0])/(end_time-start_time)
        g_speed = (end_color[1]-start_color[1])/(end_time-start_time)
        b_speed = (end_color[2]-start_color[2])/(end_time-start_time)
        a_speed = (end_color[3]-start_color[3])/(end_time-start_time)
        self.start_color = start_color
        self.end_color = end_color
        self.fade_speed = (r_speed, g_speed, b_speed, a_speed)
        self.true_color = list(self.start_color)
        if cancelling: # Cancel previous existing fade before starting new one
            self.midi_clock.schedule_once(self.stop_animation, start_time)
        self.midi_clock.schedule_once(self.start_animation, start_time)
        self.midi_clock.schedule_once(self.stop_animation, end_time)
        self.midi_clock.schedule_once(self.highlight, end_time, self.end_color) # Ensure return to proper color
        
    def start_animation(self,dt):
        self.midi_clock.schedule_interval(self.fade, 1/self.fps)
    
    def stop_animation(self,dt):
        self.midi_clock.unschedule(self.fade)
    
    def highlight(self,dt,new_color):
        for i in range(self.vertex_list_size):
            self.vertex_list.colors[4*i]   = int(new_color[0])
            self.vertex_list.colors[4*i+1] = int(new_color[1])
            self.vertex_list.colors[4*i+2] = int(new_color[2])            
            self.vertex_list.colors[4*i+3] = int(new_color[3])        
    
    def fade(self,dt):
        # Calculate "true" color separately
        # Prevents rounding errors due to necessary int conversion
        self.true_color[0] += self.fade_speed[0] * dt
        self.true_color[1] += self.fade_speed[1] * dt
        self.true_color[2] += self.fade_speed[2] * dt
        self.true_color[3] += self.fade_speed[3] * dt
        #print(self, self.true_color)
        for i in range(self.vertex_list_size):
            self.vertex_list.colors[4*i]   = int(self.true_color[0])
            self.vertex_list.colors[4*i+1] = int(self.true_color[1])
            self.vertex_list.colors[4*i+2] = int(self.true_color[2])
            self.vertex_list.colors[4*i+3] = int(self.true_color[3])

class Highlighter(Animator):
    # Changes object color at specified time    
    def __init__(self,midi_object,time,color):
        Animator.__init__(self,midi_object)
        self.midi_clock.schedule_once(self.highlight, time, color)
        
    def highlight(self,dt,new_color):
        # Assumes alpha channel present, new color must be list/tuple of 4 ints
        for i in range(self.vertex_list_size):
            self.vertex_list.colors[4*i]   = new_color[0]
            self.vertex_list.colors[4*i+1] = new_color[1]
            self.vertex_list.colors[4*i+2] = new_color[2]            
            self.vertex_list.colors[4*i+3] = new_color[3]
      
class Scroller(Animator):
    # Scrolls a vertex list by scroll speed
    def __init__(self,midi_object,start_time,end_time,speed):
        Animator.__init__(self,midi_object)
        self.midi_clock.schedule_once(self.start_animation, start_time)
        self.midi_clock.schedule_once(self.stop_animation, end_time+50)
        self.speed = speed
        
    def start_animation(self,dt):
        self.midi_clock.schedule_interval(self.animate, 1/self.fps, self.speed)
        
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
        self.animators = []
        self.vertex_format = 'v2f'
        self.color_format = 'c4B'
        self.mode = pyglet.gl.GL_TRIANGLES #default mode
        
        self.shape = data['shape']
        self.height = data['height']
        self.width = data['width']
        if self.shape == 'rectangle':
            shapes.rectangle(self, self.height, self.width)
        elif self.shape == 'ellipse':
            shapes.ellipse(self, self.height, self.width)
        elif self.shape == 'diamond':
            shapes.diamond(self, self.height, self.width)
        else:
            raise MIDIObjectException('Unknown MIDI shape:',self.shape)

        self.vertex_list = self.batch.add_indexed( self.v_count, self.mode, self.group, self.v_index, 
                                          (self.vertex_format, self.vertices),
                                          (self.color_format , self.v_colors)  )
        self.time_on = None
        self.time_off = None
        self.x = 0
        self.y = 0        

    def set_position(self, x, y, relative='center'):
        '''
        Sets position of MIDI object at coordinates (x,y)
        Position is relative to center of object by default
        Valid positions are:
        top_left, top_center, top_right
        left_center, center, right_center
        bottom_left, bottom_center, bottom_right
        '''
        self.x = x
        self.y = y
        if relative in ('top_left','top_center','top_right'):
            y_adjust = -self.height/2
        elif relative in ('left_center','center','right_center'):
            y_adjust = 0
        elif relative in ('bottom_left','bottom_center','bottom_right'):
            y_adjust = self.height/2
        else:
            raise MIDIObjectException('Unknown relative position',relative)
        if relative in ('top_left','left_center','bottom_left'):
            x_adjust = self.width/2
        elif relative in ('top_center','center','top_center'):
            x_adjust = 0
        elif relative in ('top_right','right_center','bottom_right'):
            x_adjust = -self.width/2
        else:
            raise MIDIObjectException('Unknown relative position',relative)
        
        for i in range(self.vertex_list.get_size()):
            self.vertex_list.vertices[2*i]   = x + self.vertices[2*i] + x_adjust
            self.vertex_list.vertices[2*i+1] = y + self.vertices[2*i+1] + y_adjust
    
    def set_color(self, color_list):
        '''
        color_list: 3 (RGB) or 4 (RGBA) length list
        If Alpha is not given, default to max opacity 255
        '''
        if len(color_list) == 3:
            color_list = (color_list[0], color_list[1], color_list[2], 255)
        for i in range(self.vertex_list.get_size()):
            self.vertex_list.colors[4*i]   = color_list[0]
            self.vertex_list.colors[4*i+1] = color_list[1]
            self.vertex_list.colors[4*i+2] = color_list[2]            
            self.vertex_list.colors[4*i+3] = color_list[3]
            
    def set_timing(self, time_on, time_off):
        self.time_on = time_on
        self.time_off = time_off
            
    def set_animations(self, animation_list):
        for animation in animation_list:
            if animation['type'] == 'scroll':
                self.animators.append(Scroller(self,
                                               animation['scroll_on_time'],
                                               animation['scroll_off_time'], 
                                               animation['scroll_speed'],
                                               )
                                      )
            elif animation['type'] == 'highlight':
                self.animators.append(Highlighter(self, animation['time'], animation['color']))
            elif animation['type'] == 'fade':
                self.animators.append(Fader(self, 
                                            animation['start_time'], 
                                            animation['end_time'],
                                            animation['start_color'],
                                            animation['end_color'],
                                            )
                                      )
            else:
                raise MIDIObjectException('Unknown animation type',animation['type'])
        
'''------------------------------------------------------'''

class Song(object):
    '''
    Data object for entire song
    '''
    def __init__(self):
        self.visual_region_list = []
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
        
    def register_visual_region(self,region_data):
        new_region = Visual_Region(self,region_data)
        self.visual_region_list.append(new_region)
        
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
            style_type = style.get_style(track.style)
            if style_type.is_scrolling:
                self.global_offset = max(track.scroll_on_amount,self.global_offset)
    
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
            style_type = style.get_style(track.style)
            style_type.draw_function(track)
            
    def get_region_by_name(self, name):
        for region in self.visual_region_list:
            if region.name == name:
                return region
        else:
            raise MIDIObjectException('No visual region found with name:', name)
        
    def get_track_by_index(self, index):
        for track in self.track_list:
            if track.index == index:
                return track
        else:
            raise MIDIObjectException('No track found with index:', index)
        
            
    def optimize_z_order(self):
        '''
        Reduce the number of pyglet ordered groups to
        minimum needed to optimize performance
        
        Assumes visual regions don't overlap
        '''
        new_track_list = []
        for region in self.visual_region_list:
            for track in region.track_list:
                # Collapse all undrawn tracks into bottom group
                if track.style == 'none':
                    track.z_order = 0
                else:
                    new_track_list.append(track)
            new_track_list_ordered = sorted(new_track_list, key=lambda k: k.z_order)
            for track in enumerate(new_track_list_ordered, start=1):
                track[1].z_order = track[0]
        
        
class Visual_Region(object):
    '''
    Visual regions are regions on the screen in which
    groups of tracks will be displayed. Properties of tracks
    that are interrelated (global min and max notes) are
    independent for each region.
    '''
    def __init__(self,parent,region_data):
        self.name = region_data['name']
        self.parent_song = parent
        self.track_list = []
        self.left = region_data['left']
        self.right = region_data['right']
        self.up = region_data['up']
        self.down = region_data['down']
        self.max_note = -1
        self.min_note = 128
        
    def register_track(self,track):
        self.track_list.append(track)
        
    def set_note_bounds(self):
        for track in self.track_list:
            self.max_note = max(track.max_note,self.max_note)
            self.min_note = min(track.min_note,self.min_note)
        
        
class Track(object):
    '''
    Data object for track
    '''
    def __init__(self,parent,track_data):
        self.parent_song = parent
        self.parent_region = None
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

        self.z_order = 255
        self.style = 'none'
        self.style_parameters = {}
            
    def register_note(self,note_data):
        new_note = Note(self,note_data)
        self.note_list.append(new_note)
        self.min_note = min(new_note.pitch,self.min_note)
        self.max_note = max(new_note.pitch,self.max_note)
        
    def set_user_data(self,u):
        '''
        Sets the user data for a track
        User data follows structure of default_config.ini
        '''
        self.parent_region = self.parent_song.get_region_by_name(u['region'])
        self.parent_region.register_track(self)
        self.z_order = u['z_order']
        self.style = u['style']
        self.style_parameters = u['style_parameters']
        style_type = style.get_style(self.style)
        style_type.validate(self)

class Note(object):
    '''
    Data object for individual note
    '''
    def __init__(self,track,note_data):
        self.parent_track = track
        self.track_index = note_data['track_no']
        if self.parent_track.index != self.track_index:
            raise MIDIObjectException('Track number mismatch')
                
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
            