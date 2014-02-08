'''
Created on Jul 11, 2013

@author: matt
'''
example_settings = {
                    'song_data':{
                                 'midi_file': "D:\Matt's Stuff\Git\MIDI Program\MIDI Program\Resources\Gravity Falls Theme Song.mid",
                                 'mp3_file': "D:\Matt's Stuff\Git\MIDI Program\MIDI Program\Resources\Gravity Falls Theme Song.mp3",
                                 'mp3_delay': 2.33,
                                 'screen_buffer': 20,
                                 'hit_line_percent': 0.5,
                                 'bg_color': [0,0,0,255],
                                 },
                    'track_data':{
                             '0' :{
                                        'index': 0,
                                        'type': 'piano_roll',
                                        'shape': 'rectangle',
                                        'size': 10,
                                        'speed': 1,
                                        'color': (255,0,0,255),
                                        'z_order': 0,
                                        #'scroll_on_time': scroll_on_time, # derived
                                        #'scroll_off_time': scroll_off_time, # derived
                                        'animation_data':{
                                                          'hit_animations': ['highlight'],
                                                          'highlight_on_color': (255,200,200,255),
                                                          'highlight_off_color': (255,0,0,255),
                                                          },
                                        },
                            '1' :{
                                        'index': 1,
                                        'type': 'piano_roll',
                                        'shape': 'rectangle',
                                        'size': 10,
                                        'speed': 1.5,
                                        'color': (255,100,0,255),
                                        'z_order': 10,
                                        #'scroll_on_time': scroll_on_time, # derived
                                        #'scroll_off_time': scroll_off_time, # derived
                                        'animation_data':{
                                                          'hit_animations': ['highlight'],
                                                          'highlight_on_color': (255,200,200,255),
                                                          'highlight_off_color': (255,100,0,255),
                                                          },
                                        },
                            '2' :{
                                        'index': 2,
                                        'type': 'piano_roll',
                                        'shape': 'rectangle',
                                        'size': 10,
                                        'speed': 1,
                                        'color': (0,255,0,255),
                                        'z_order': 2,
                                        #'scroll_on_time': scroll_on_time, # derived
                                        #'scroll_off_time': scroll_off_time, # derived
                                        'animation_data':{
                                                          'hit_animations': ['highlight'],
                                                          'highlight_on_color': (255,200,200,255),
                                                          'highlight_off_color': (0,255,0,255),
                                                          },
                                        },
                            '3' :{
                                        'index': 3,
                                        'type': 'piano_roll',
                                        'shape': 'rectangle',
                                        'size': 10,
                                        'speed': 1,
                                        'color': (0,0,255,255),
                                        'z_order': 3,
                                        #'scroll_on_time': scroll_on_time, # derived
                                        #'scroll_off_time': scroll_off_time, # derived
                                        'animation_data':{
                                                          'hit_animations': ['highlight'],
                                                          'highlight_on_color': (255,200,200,255),
                                                          'highlight_off_color': (0,0,255,255),
                                                          },
                                        },
                            '4' :{
                                        'index': 4,
                                        'type': 'piano_roll',
                                        'shape': 'rectangle',
                                        'size': 10,
                                        'speed': 1,
                                        'color': (255,0,100,255),
                                        'z_order': 4,
                                        #'scroll_on_time': scroll_on_time, # derived
                                        #'scroll_off_time': scroll_off_time, # derived
                                        'animation_data':{
                                                          'hit_animations': ['highlight'],
                                                          'highlight_on_color': (255,200,200,255),
                                                          'highlight_off_color': (255,0,100,255),
                                                          },
                                        },
                            '5' :{
                                        'index': 5,
                                        'type': 'piano_roll',
                                        'shape': 'rectangle',
                                        'size': 10,
                                        'speed': 1,
                                        'color': (100,0,100,255),
                                        'z_order': 5,
                                        #'scroll_on_time': scroll_on_time, # derived
                                        #'scroll_off_time': scroll_off_time, # derived
                                        'animation_data':{
                                                          'hit_animations': ['highlight'],
                                                          'highlight_on_color': (255,200,200,255),
                                                          'highlight_off_color': (100,0,100,255),
                                                          },
                                        },
                             '6' :{
                                        'index': 6,
                                        'type': 'piano_roll',
                                        'shape': 'rectangle',
                                        'size': 10,
                                        'speed': 1,
                                        'color': (75,255,75,255),
                                        'z_order': 6,
                                        #'scroll_on_time': scroll_on_time, # derived
                                        #'scroll_off_time': scroll_off_time, # derived
                                        'animation_data':{
                                                          'hit_animations': ['highlight'],
                                                          'highlight_on_color': (255,200,200,255),
                                                          'highlight_off_color': (75,255,75,255),
                                                          },
                                        },
                             '7' :{
                                        'index': 7,
                                        'type': 'piano_roll',
                                        'shape': 'rectangle',
                                        'size': 10,
                                        'speed': 1,
                                        'color': (255,255,100,255),
                                        'z_order': 7,
                                        #'scroll_on_time': scroll_on_time, # derived
                                        #'scroll_off_time': scroll_off_time, # derived
                                        'animation_data':{
                                                          'hit_animations': ['highlight'],
                                                          'highlight_on_color': (255,200,200,255),
                                                          'highlight_off_color': (255,255,100,255),
                                                          },
                                        },
                             '8' :{
                                        'index': 8,
                                        'type': 'piano_roll',
                                        'shape': 'rectangle',
                                        'size': 10,
                                        'speed': 1,
                                        'color': (180,0,90,255),
                                        'z_order': 8,
                                        #'scroll_on_time': scroll_on_time, # derived
                                        #'scroll_off_time': scroll_off_time, # derived
                                        'animation_data':{
                                                          'hit_animations': ['highlight'],
                                                          'highlight_on_color': (255,200,200,255),
                                                          'highlight_off_color': (180,0,90,255),
                                                          },
                                        },
                             '9' :{
                                        'index': 9,
                                        'type': 'piano_roll',
                                        'shape': 'rectangle',
                                        'size': 10,
                                        'speed': 1,
                                        'color': (10,255,50,255),
                                        'z_order': 9,
                                        #'scroll_on_time': scroll_on_time, # derived
                                        #'scroll_off_time': scroll_off_time, # derived
                                        'animation_data':{
                                                          'hit_animations': ['highlight'],
                                                          'highlight_on_color': (255,200,200,255),
                                                          'highlight_off_color': (10,255,50,255),
                                                          },
                                    },
                                  },

                    }