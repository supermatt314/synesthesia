'''
Created on Jul 10, 2013

@author: matt
'''

import pyglet
import midi_parse
import midi_objects
import config_parse
                
# Overloads midi_parse's register note function and captures notes in 'note_list'
note_list = []
def register_note(t, c, p, v, t1, t2):
    note_list.append({'track_no':t,'channel':c,'pitch':p,'velocity':v,'time_on':t1,'time_off':t2})
midi_parse.register_note = register_note           

def get_data(main_window):
     
    settings_data = config_parse.read_config()
    
    if not settings_data:
        return None
      
    # Pre-calculations
    song_data = settings_data['song_data']      
    song_data['window_width'] = window_width = main_window.width
    song_data['window_height'] = main_window.height
    hit_line = window_width * song_data['hit_line_percent']
    for track in settings_data['track_data'].values():
        offset = 0
        if track['type'] == 'piano_roll':
            track['scroll_on_amount'] = (window_width - hit_line)/track['speed']
            track['scroll_off_amount'] = hit_line/track['speed']
            offset = max(offset,track['scroll_on_amount'])
    song_data['offset'] = offset

    global note_list
    note_list = []
    midifile = midi_parse.MidiFile()
    # Reading the midi file will automatically populate 'note_list' via the register_note hook
    midifile.read(settings_data['song_data']['midi_file'])
    
    unk_index = 0
    for t in midifile.tracks:
        for e in t.events:
            if e.type == 'SEQUENCE_TRACK_NAME':
                name = e.data.replace(b' ',b'_')
                break
        else:
            name = 'Unknown_Name_{}'.format(unk_index)
            unk_index += 1
        for note in note_list:
            if note['track_no'] == t.index:
                note['track_name'] = name
                
    tempo_data = [{'midi_tick':e.time+offset, 'tempo_raw':e.data} for t in midifile.tracks for e in t.events if e.type == "SET_TEMPO"]
    for t in tempo_data:
        mpqn = int.from_bytes(t['tempo_raw'], 'big') #microseconds per quarter note
        t['tempo'] = int(round(60000000/mpqn,0)) # convert MIDI's ridiculous tempo numbers into beats per minute
    sorted(tempo_data, key=lambda k: k['midi_tick'])
    tempo_data[0]['midi_tick'] = 0

    max_note, min_note = 0, 127
    for note in note_list:
        max_note = max(max_note,note['pitch'])
        min_note = min(min_note,note['pitch'])
    song_data['max_note'], song_data['min_note'] = max_note, min_note
    
    data = {'song_data':song_data,'track_data':settings_data['track_data'],'tempo_data':tempo_data}
    return data
    
def setup_animation(main_window, data):
    batch = main_window.main_batch
    media_player = main_window.media_player
    midi_clock = main_window.midi_clock
    song_data = data['song_data']
    track_data = data['track_data']
    tempo_data = data['tempo_data']
    
    for t in tempo_data:
        midi_clock.schedule_once(midi_clock.change_tempo, t['midi_tick'], t['tempo'])    
            
    bg_group = pyglet.graphics.OrderedGroup(0)
    bg_data = {'shape': 'rectangle',
               'height': song_data['window_height'],
               'width': song_data['window_width']
               }
    background = midi_objects.MIDIObject(batch,bg_group,pyglet.clock.get_default(),bg_data)
    background.set_position(0, song_data['window_height']/2)
    background.set_color(song_data['bg_color'])
    
    for track in track_data.values():
        if track['type'] == 'none':
            continue        
        group = pyglet.graphics.OrderedGroup(track['z_order'])
        notes = [item for item in note_list if item['track_no']==track['index']]
        if track['type'] == 'piano_roll':
            for note in notes:
                object_data = {'shape': track['shape'],
                               'height': track['size']*note['velocity']/100,
                               'width': (note['time_off']-note['time_on']) * track['speed']
                              }
                current_object = midi_objects.MIDIObject(batch,group,midi_clock,object_data)
                x = song_data['window_width']
                y = (note['pitch']-song_data['min_note'])/(song_data['max_note']-song_data['min_note']) \
                    *(song_data['window_height']-2*song_data['screen_buffer'])+song_data['screen_buffer']
                current_object.set_position(x, y)
                current_object.set_color(track['color'])
                on_time = note['time_on']+song_data['offset']
                off_time = note['time_off']+song_data['offset']
                current_object.set_timing(on_time, off_time)
                animation_data = [{'type':'scroll',
                                   'scroll_on_time': note['time_on'] - track['scroll_on_amount'] + song_data['offset'],
                                   'scroll_off_time':note['time_off'] + track['scroll_off_amount'] + song_data['offset'],
                                   'scroll_speed': -track['speed']
                                  },
                                  {'type':'highlight',
                                   'highlight_on_color':track['animation_data']['highlight_on_color'],
                                   'highlight_off_color':track['animation_data']['highlight_off_color']
                                  }
                                 ]
                current_object.set_animations(animation_data)
        elif track['type'] == 'static':
            pass
        else:
            assert('Unknown track type')

    # Setup music player
    if song_data['mp3_file'] != '':
        music = song_data['mp3_file']
        media_player.set_music(music)
    media_player.set_delay(song_data['mp3_delay'])
    print('Done setting up')
    
    
#===============================================================================
# def setup_note_data(song, track, note):
#     animation_data = track['animation_data']    
#     morph_data = {'shape': track['shape'],
#                   'color': track['color'],
#                   'height': track['size']*note['velocity']/100
#                   }
#     positional_data = {}
#     timing_data = {'time_on': note['time_on'] + song['offset'],
#                    'time_off': note['time_off'] + song['offset']}
# 
#     if track['type'] == 'piano_roll':
#         animation_data['scroll_speed'] = -track['speed']
#         morph_data['width'] = (note['time_off']-note['time_on']) * track['speed']
#         positional_data['x'] = song['window_width']
#         positional_data['y'] = (note['pitch']-song['min_note'])/(song['max_note']-song['min_note']) \
#                                 *(song['window_height']-2*song['screen_buffer'])+song['screen_buffer']
#         timing_data['scroll_on_time'] = note['time_on'] - track['scroll_on_amount'] + song['offset']
#         timing_data['scroll_off_time'] = note['time_off'] + track['scroll_off_amount'] + song['offset']
#     elif track['type'] == 'static':
#         pass
#     return {'animation': animation_data, 'morph': morph_data, 'position':positional_data, 'timing':timing_data}
#     
#===============================================================================