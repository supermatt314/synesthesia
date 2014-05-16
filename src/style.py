'''
Created on May 6, 2014

@author: Matt
'''

import pyglet
import midi_objects

class StyleException(Exception):
    pass

class Base_Style(object):
    def __init__(self):
        self.name = None
        self.draw_function = None        
        self.is_scrolling = False
        self.validated_params = {}        
        self.valid_param_types = ()
        self.default_params = {}
        
    def validate(self, track):
        given_params = track.style_parameters
        for param in self.valid_param_types:
            if param not in given_params.keys():
                raise StyleException('Missing style parameter', param)
            if given_params[param] is None:
                self.validated_params[param] = self.default_params[param]
            else:
                self.validated_params[param] = given_params[param]
            setattr(track, param, self.validated_params[param])
        track.style_parameters = self.validated_params
        
        track.min_screen_region = track.parent_region.down * track.parent_song.window_height
        track.max_screen_region = track.parent_region.up   * track.parent_song.window_height
        if self.is_scrolling: 
            track.scroll_on_amount  = track.parent_song.window_width/track.speed * (1-track.hit_line_percent)
            track.scroll_off_amount = track.parent_song.window_width/track.speed * (track.hit_line_percent) 
                

class No_Style(Base_Style):
    def __init__(self):
        Base_Style.__init__(self)
        self.name = 'no_style'
        self.draw_function = self.none

    def none(self, track):
        '''
        No objects drawn for this track
        '''


class Simple(Base_Style):
    '''
    Valid Parameters:
    shape - string (rectangle, ellipse, diamond)
    speed - float x>0
    size - float x>0
    color - color list
    highlight color - color list
    hit line percent - float 0<x<1
    '''
    def __init__(self):
        Base_Style.__init__(self)
        self.name = 'simple'
        self.draw_function = self.simple
        self.is_scrolling = True
        self.valid_param_types = ('shape','speed','size','color','highlight_color','hit_line_percent')
        self.default_params = {
                               'shape':'rectangle',
                               'color':(255,0,0,255),
                               'speed':1,
                               'size':14,
                               'highlight_color':(255,200,200,255),
                               'hit_line_percent':0.5,
                               }   
    
    def simple(self, track):
        '''
        Draw scrolling highlighting shapes
        '''
        global_min_note = track.parent_region.min_note
        global_max_note = track.parent_region.max_note
        offset = track.parent_song.global_offset    
        for note in track.note_list:
            width = (note.time_off-note.time_on) * track.speed
            object_data = {'shape': track.shape,
                           'height': track.size*note.velocity/100,
                           'width': width
                          }
            current_object = midi_objects.MIDIVisualObject(track.parent_song.batch,
                                                           track.group,
                                                           track.parent_song.midi_clock,
                                                           object_data)
            x = track.parent_song.window_width
            y = (note.pitch - global_min_note)/(global_max_note - global_min_note) \
                *(track.max_screen_region-track.min_screen_region) + track.min_screen_region
            current_object.set_position(x, y, relative='left_center')
            current_object.set_timing(note.time_on+offset, note.time_off+offset)
            current_object.set_color(track.color)
            animation_data = [{'type':'scroll',
                               'scroll_on_time': current_object.time_on - track.scroll_on_amount,
                               'scroll_off_time': current_object.time_off + track.scroll_off_amount,
                               'scroll_speed': -track.speed
                              },
                              {'type':'highlight',
                               'time': current_object.time_on,
                               'color': track.highlight_color,
                              },
                              {'type':'highlight',
                               'time': current_object.time_off,
                               'color': track.color,
                              },
                             ]
            current_object.set_animations(animation_data)

class Simple_Fade(Base_Style):
    '''
    Valid Parameters:
    shape - string (rectangle, ellipse, diamond)
    speed - float x>0
    size - float x>0
    color - color list
    highlight color - color list
    hit line percent - float 0<x<1
    min_fade_time - float x>0
    max_fade_time - float x>0
    '''
    def __init__(self):
        Base_Style.__init__(self)
        self.name = 'fade'
        self.draw_function = self.fade
        self.is_scrolling = True
        self.valid_param_types = ('shape',
                                  'speed',
                                  'size',
                                  'color',
                                  'highlight_color',
                                  'hit_line_percent',
                                  'min_fade_time',
                                  'max_fade_time'
                                  )
        self.default_params = {
                               'shape':'rectangle',
                               'color':(255,0,0,255),
                               'speed':1,
                               'size':14,
                               'highlight_color':(255,200,200,255),
                               'hit_line_percent':0.5,
                               'min_fade_time':-1,
                               'max_fade_time':float("inf")
                               }   
    
    def fade(self, track):
        '''
        Draw scrolling shapes that fade from the highlight color to the normal color
        '''
        global_min_note = track.parent_region.min_note
        global_max_note = track.parent_region.max_note
        offset = track.parent_song.global_offset
        for note in track.note_list:
            width = (note.time_off-note.time_on) * track.speed
            object_data = {'shape': track.shape,
                           'height': track.size*note.velocity/100,
                           'width': width
                          }
            current_object = midi_objects.MIDIVisualObject(track.parent_song.batch,
                                                           track.group,
                                                           track.parent_song.midi_clock,
                                                           object_data)
            x = track.parent_song.window_width
            y = (note.pitch - global_min_note)/(global_max_note - global_min_note) \
                *(track.max_screen_region-track.min_screen_region) + track.min_screen_region
            current_object.set_position(x, y, relative='left_center')
            current_object.set_timing(note.time_on+offset, note.time_off+offset)
            current_object.set_color(track.color)
            fade_length = max(track.min_fade_time,
                              min(track.max_fade_time,
                                  current_object.time_off-current_object.time_on)
                              )
            animation_data = [{'type':'scroll',
                               'scroll_on_time': current_object.time_on - track.scroll_on_amount,
                               'scroll_off_time': current_object.time_off + track.scroll_off_amount,
                               'scroll_speed': -track.speed,
                              },
                              {'type':'fade',
                               'start_time': current_object.time_on,
                               'end_time': current_object.time_on + fade_length,
                               'start_color': track.highlight_color,
                               'end_color': track.color,
                              },
                             ]
            current_object.set_animations(animation_data)

class Simple_Static(Base_Style):
    '''
    Valid Parameters:
    shape - string (rectangle, ellipse, diamond)
    color - color list
    highlight color - color list
    '''    

style_list = {'none': No_Style(),
              'simple': Simple(),
              'fade': Simple_Fade(),
              'static': Simple_Static(),
              }

def get_style(style_key):
    style_object = style_list.get(style_key)
    if style_object is None:
        raise StyleException('Style not found:', style_key)
    else:
        return style_object

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