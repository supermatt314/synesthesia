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
    song_data['window_width']= window_width = main_window.width
    song_data['window_height'] = main_window.height
    hit_line = window_width * song_data['hit_line_percent']
    for track in settings_data['track_data'].values():
        offset = 0
        if track['type'] == 'piano_roll':
            track['scroll_on_time'] = (window_width - hit_line)/track['speed']
            track['scroll_off_time'] = hit_line/track['speed']
            offset = max(offset,track['scroll_on_time'])
    song_data['offset'] = offset

    global note_list
    note_list = []
    midifile = midi_parse.MidiFile()
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
    
def setup_animation(main_window,data):
    batch = main_window.main_batch
    media_player = main_window.media_player
    midi_clock = main_window.midi_clock
    song_data = data['song_data']
    track_data = data['track_data']
    tempo_data = data['tempo_data']
    
    for t in tempo_data:
        midi_clock.schedule_once(midi_clock.change_tempo, t['midi_tick'], t['tempo'])    
            
    bg_group = pyglet.graphics.OrderedGroup(0)
    background = midi_objects.Background(batch,bg_group,pyglet.clock.get_default(),**song_data)
    
    for track in track_data.values():
        group = pyglet.graphics.OrderedGroup(track['z_order'])
        animation_data = track['animation_data']
        notes = [item for item in note_list if item['track_no']==track['index']]
        for note in notes:
            data_to_send = {'song_data':song_data,
                            'track_data':track,
                            'animation_data':animation_data,
                            'note_data':note}
            if track['type'] == 'piano_roll':
                thing = midi_objects.PianoRollObject(batch,group,midi_clock,**data_to_send)
            elif track['type'] == 'none':
                pass

    # Setup music player
    if song_data['mp3_file'] != '':
        music = song_data['mp3_file']
        media_player.set_music(music)
    media_player.set_delay(song_data['mp3_delay'])