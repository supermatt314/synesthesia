'''
Created on May 6, 2014

@author: Matt
'''

import midi_objects

class StyleException(Exception):
    pass

class Base_Style(object):
    def __init__(self):
        self.name = None
        self.validated_params = {}        
        self.valid_param_types = ()
        self.default_params = {}
        
    def validate(self, track, param_list):
        given_params = param_list
        for param in self.valid_param_types:
            if param not in given_params.keys():
                raise StyleException('Missing style parameter', param)
            if given_params[param] is None:
                self.validated_params[param] = self.default_params[param]
            else:
                self.validated_params[param] = given_params[param]
            setattr(track, param, self.validated_params[param])
        return self.validated_params
                
class No_Mode(Base_Style):
    def __init__(self):
        Base_Style.__init__(self)
        self.name = 'no_mode'
        
    def draw_with_style(self, track, style):
        '''
        Draw nothing.
        '''
        pass 

class No_Style(Base_Style):
    def __init__(self):
        Base_Style.__init__(self)
        self.name = 'no_style'

    def add_animation(self, track, note, off_color):
        '''
        No objects drawn for this track
        '''
        pass
    
class Scroll_Mode(Base_Style):
    '''
    Valid Parameters:
    shape - string
    inactive_color - color_list
    color - color_list
    speed - float x>0
    height - float x>0
    width - float x>0 or None
    hit line percent - float 0<x<1
    '''
    def __init__(self):
        Base_Style.__init__(self)
        self.name = "scroll_mode"
        self.valid_param_types =('shape',
                                 'speed',
                                 'height',
                                 'width',
                                 'hit_line_percent',
                                 )
        
        self.default_params = {'shape':'rectangle',                               
                               'speed':1,
                               'height':14,
                               'width':None,
                               'hit_line_percent':0.5,
                               }
    def draw_with_style(self, track, style):
        '''
        Draw a scrolling object with specified style
        '''
        global_min_note = track.parent_region.min_note
        global_max_note = track.parent_region.max_note
        offset = track.offset
        for note in track.note_list:
            width = track.width or (note.time_off-note.time_on) * track.speed
            object_data = {'shape': track.shape,
                           'height': track.height,
                           'width': width
                          }
            current_object = midi_objects.MIDIVisualObject(track.parent_song.batch,
                                                           track.group,
                                                           track.parent_song.midi_clock,
                                                           object_data)
            x = track.parent_song.window_width
            y = (note.pitch - global_min_note)/(global_max_note - global_min_note) \
                *(track.top_edge-track.bottom_edge) + track.bottom_edge
            current_object.set_position(x, y, relative='left_center')
            current_object.set_initial_color(track.color)
            animation_data = [{'type':'scroll',
                               'scroll_on_time': note.time_on + offset - track.scroll_on_amount,
                               'scroll_off_time': note.time_off + offset + track.scroll_off_amount,
                               'scroll_speed': -track.speed
                              },
                              ]
            
            off_color = track.color
            style_animations = style.add_animation(track, note, off_color)
            animation_data.extend(style_animations)
            
            current_object.set_animations(animation_data)

class Static_Mode(Base_Style):
    '''
    Valid Parameters:
    height - float x>0
    width - float x>0 or None
    '''
    def __init__(self):
        Base_Style.__init__(self)
        self.name = "static_mode"
        self.valid_param_types =('shape',
                                 'height',
                                 'width',
                                 )
        self.default_params = {'shape':'rectangle',
                               'height':20,
                               'width':400,
                               }
    def draw_with_style(self, track, style):
        '''
        Draw a scrolling object with specified style
        '''
        global_min_note = track.parent_region.min_note
        global_max_note = track.parent_region.max_note
        object_data = {'shape': track.shape,
                       'height': track.height,
                       'width': track.width,
                      }
        off_color = track.inactive_color         
        for pitch in range(global_min_note,global_max_note+1):
            # draw note
            current_object = midi_objects.MIDIVisualObject(track.parent_song.batch,
                                                           track.group,
                                                           track.parent_song.midi_clock,
                                                           object_data)
            x = (track.right_edge - track.left_edge)/2 + track.left_edge
            y = (pitch - global_min_note)/(global_max_note - global_min_note) \
                *(track.top_edge-track.bottom_edge) + track.bottom_edge
            current_object.set_position(x, y, relative='center')
            current_object.set_initial_color(track.inactive_color)
            
            animation_data = []
            notes_this_pitch = [note for note in track.note_list if note.pitch == pitch]
                       
            for note in notes_this_pitch:
                style_animations = style.add_animation(track, note, off_color, canceling=True)
                animation_data.extend(style_animations)
            current_object.set_animations(animation_data)
        
class Simple(Base_Style):
    '''
    Highlights note when being played with highlight color
    Resets note to off_color
    
    Valid Parameters:
    inactive_color - color_list
    color - color_list
    highlight color - color list
    '''
    def __init__(self):
        Base_Style.__init__(self)
        self.name = 'simple'
        self.valid_param_types = ('inactive_color',
                                  'color',
                                  'highlight_color',
                                  )
        self.default_params = {
                               'inactive_color':(255,0,0,0),
                               'color':(255,0,0,255),
                               'highlight_color':(255,200,200,255),
                               }   
    
    def add_animation(self, track, note, off_color, **kwargs):
        animation_data = [{'type':'highlight',
                           'time': note.time_on+track.offset,
                           'color': track.highlight_color,
                          },
                          {'type':'highlight',
                           'time': note.time_off+track.offset,
                           'color': off_color,
                          },
                         ]
        return animation_data

class Fade(Base_Style):
    '''
    Highlights note when being played with fade color
    Fades note color gradually to off color over length of note,
    subject to min and max fade times
    
    Valid Parameters:
    inactive_color - color_list
    color - color_list
    fade_start_color - color_list
    fade_end_color - color_list
    fade_time - float x>0
    min_fade_time - float x>0
    max_fade_time - float x>0
    '''
    def __init__(self):
        Base_Style.__init__(self)
        self.name = 'fade'
        self.valid_param_types = ('inactive_color',
                                  'color',
                                  'fade_start_color',
                                  'fade_end_color',
                                  'fade_time',
                                  'min_fade_time',
                                  'max_fade_time'
                                  )
        self.default_params = {
                               'inactive_color':(255,0,0,0),
                               'color':(255,0,0,255),
                               'fade_start_color':(255,200,200,255),
                               'fade_end_color':None,
                               'fade_time':None,
                               'min_fade_time':-1,
                               'max_fade_time':float("inf"),
                               }   
    
    def add_animation(self, track, note, off_color, **kwargs):
        fade_length = track.fade_time or max(track.min_fade_time,
                                              min(track.max_fade_time,
                                                  note.time_off-note.time_on)
                                              )
        if 'canceling' in kwargs:
            canceling = kwargs['canceling']
        animation_data = [{'type':'fade',
                           'start_time': note.time_on + track.offset,
                           'end_time': note.time_on + track.offset + fade_length,
                           'start_color': track.fade_start_color,
                           'end_color': track.fade_end_color or off_color,
                           'canceling': canceling,
                          },
                         ]
        return animation_data
            
class Pulse(Base_Style):
    '''
    Quickly fades from off color to pulse peak color,
    then fades from peak color to pulse end color,
    then change to off color at end of note
    
    Valid Parameters:
    inactive_color - color_list
    color - color_list
    pulse_peak_color - color list
    pulse_end_color - color list
    pulse_time - float x>0
    '''
    def __init__(self):
        Base_Style.__init__(self)
        self.name = 'pulse'
        self.valid_param_types = ('inactive_color',
                                  'color',
                                  'pulse_peak_color',
                                  'pulse_end_color',                                  
                                  'pulse_time',
                                  )
        self.default_params = {'inactive_color':(255,0,0,255),
                               'color':(255,0,0,255),
                               'pulse_peak_color':(255,0,0,255),
                               'pulse_end_color':None,
                               'pulse_time':48,
                               }   
    
    def add_animation(self, track, note, off_color, **kwargs):
        end_color = track.pulse_end_color or track.color
        pulse_length = min(track.pulse_time,
                          note.time_off-note.time_on
                          )
        animation_data = [{'type':'fade',
                           'start_time': note.time_on + track.offset,
                           'end_time': note.time_on + track.offset + pulse_length/2,
                           'start_color': off_color,
                           'end_color': track.pulse_peak_color,
                           },
                          {'type':'fade',
                           'start_time': note.time_on + track.offset + pulse_length/2,
                           'end_time': note.time_on + track.offset + pulse_length,
                           'start_color': track.pulse_peak_color,
                           'end_color': end_color,
                           },                              
                          {'type':'highlight',
                           'time': note.time_off + track.offset,
                           'color': off_color,
                          },
                         ]
        return animation_data

style_list = {'none': No_Style(),
              'simple': Simple(),
              'fade': Fade(),
              'pulse': Pulse(),
              }

mode_list = {'none': No_Mode(),
             'scroll': Scroll_Mode(),
             'static': Static_Mode(),
             }

def get_style(style_key):
    style_object = style_list.get(style_key)
    if style_object is None:
        raise StyleException('Style not found:', style_key)
    else:
        return style_object
    
def get_mode(mode_key):
    mode_object = mode_list.get(mode_key)
    if mode_object is None:
        raise StyleException('Style not found:', mode_key)
    else:
        return mode_object    