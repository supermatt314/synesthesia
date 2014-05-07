'''
Created on May 6, 2014

@author: Matt
'''

import pyglet
import midi_objects

class Base_Style(object):
    def __init__(self):
        self.name = None
        self.draw_function = None        
        self.is_scrolling = False
        
    def validate(self, track):
        pass

class No_Style(Base_Style):
    def __init__(self):
        Base_Style.__init__(self)
        self.name = 'no_style'
        self.draw_function = self.none

    def none(self, track):
        '''
        No objects drawn for this track
        '''
        return

class Simple(Base_Style):
    def __init__(self):
        Base_Style.__init__(self)
        self.name = 'simple'
        self.draw_function = self.simple
        self.is_scrolling = True
           
    def none(self, track):
        '''
        No objects drawn for this track
        '''
        return
    
    def validate(self, track):
        param_dict = track.style_parameters
        if 'shape' in param_dict.keys():
            track.shape = param_dict['shape']
        else:
            track.shape = 'rectangle'
        if 'color' in param_dict.keys():
            track.color = param_dict['color']
        else:
            track.color = [255,0,0,255]
        if 'speed' in param_dict.keys():
            track.speed = param_dict['speed']
        else:
            track.speed = 1
        if 'size' in param_dict.keys():
            track.size = param_dict['size']
        else:
            track.size = 10
        if 'highlight_color' in param_dict.keys():
            track.highlight_color = param_dict['highlight_color']
        else:
            track.highlight_color = [255,200,200,255]
        
        track.min_screen_region = 20
        track.max_screen_region = track.parent_song.window_height - 20
        track.hit_line_percent = 0.5    
        track.scroll_on_amount  = track.parent_song.window_width/track.speed * (1-track.hit_line_percent)
        track.scroll_off_amount = track.parent_song.window_width/track.speed * (track.hit_line_percent)                
        return
    
    def simple(self, track):
        '''
        Draw scrolling highlighting shapes
        '''
        # Do stuff with style parameters
        # speed, color, highlight color, shape, size 
        global_min_note = track.parent_song.global_min_note
        global_max_note = track.parent_song.global_max_note
        offset = track.parent_song.global_offset
        track.group = pyglet.graphics.OrderedGroup(track.z_order)        
        for note in track.note_list:
            width = (note.time_off-note.time_on) * track.speed
            object_data = {'shape': track.shape,
                           'height': track.size*note.velocity/100,
                           'width': width
                          }
            current_object = midi_objects.MIDIVisualObject(track.parent_song.batch,track.group,track.parent_song.midi_clock,object_data)
            x = track.parent_song.window_width
            y = (note.pitch - global_min_note)/(global_max_note - global_min_note) \
                *(track.max_screen_region-track.min_screen_region) + track.min_screen_region
            current_object.set_position(x, y)
            current_object.set_timing(note.time_on+offset, note.time_off+offset)
            current_object.set_color(track.color)
            animation_data = [{'type':'scroll',
                               'scroll_on_time': note.time_on - track.scroll_on_amount + offset,
                               'scroll_off_time': note.time_off + track.scroll_off_amount + offset,
                               'scroll_speed': -track.speed
                              },
                              {'type':'highlight',
                               'highlight_on_color': track.highlight_color,
                               'highlight_off_color': track.color,
                              }
                             ]
            current_object.set_animations(animation_data)
        return

style_list = {'none': No_Style(),
              'simple': Simple(),
              }