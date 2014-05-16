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
    '''
    Reads data from config file
    Sets up Song data structure
    
    Input: PlaybackWindow (to get window sizes)
    Output: Song or
            None if read error occurred
    '''
    
    # Returns none if data not valid 
    settings_data = config_parse.read_config()
    
    if not settings_data:
        return None
    
    song = midi_objects.Song()
    song.set_midi_file(settings_data['song_data']['midi_file'])
    song.set_mp3_file(settings_data['song_data']['mp3_file'])
    song.set_mp3_delay(settings_data['song_data']['mp3_delay'])
    song.set_window_dimensions(main_window)
    song.set_background_color(settings_data['song_data']['bg_color'])
    
    for region in settings_data['visual_region_data'].values():
        song.register_visual_region(region)

    global note_list
    note_list = []
    midifile = midi_parse.MidiFile()
    # Reading the midi file will automatically populate 'note_list' via the register_note hook
    midifile.read(settings_data['song_data']['midi_file'])
    
    for t in midifile.tracks:
        song.register_track(t)
        for e in t.events:
            if e.type == "SET_TEMPO":
                song.register_tempo(e.time,e.data)
        
    for note_data in note_list:
        track = song.get_track_by_index(note_data['track_no'])
        track.register_note(note_data)
    
    for track in song.track_list:
        for user_data in settings_data['track_data'].values():
            if user_data['index'] == track.index:
                track.set_user_data(user_data)
    
    for region in song.visual_region_list:
        region.set_note_bounds()
    
    if song.mp3_delay < 0:
        mp3_delay_amount = abs(song.mp3_delay)
    else:
        mp3_delay_amount = None
    song.set_global_offset(delay_amount=mp3_delay_amount)
    
    song.optimize_z_order()
    print('Done getting data')
    return song
    
def setup_animation(main_window, song):
    '''
    Sets up drawing batch, media player
    Schedules tempo changes in song
    Draws background
    Calls setup_visuals for Song
    
    Inputs: PlaybackWindow, Song
    Outputs: nothing
    
    '''
    batch = main_window.main_batch
    media_player = main_window.media_player
    midi_clock = main_window.midi_clock
    
    for t in song.tempo_list:
        t.schedule_tempo(midi_clock)     
            
    bg_group = pyglet.graphics.OrderedGroup(0)
    bg_data = {'shape': 'rectangle',
               'height': song.window_height,
               'width': song.window_width
               }
    background = midi_objects.MIDIVisualObject(batch,bg_group,pyglet.clock.get_default(),bg_data)
    background.set_position(0, song.window_height/2)
    background.set_color(song.bg_color)
    
    song.setup_visuals(batch, midi_clock)

    # Setup music player
    if song.mp3_file != '':
        music = song.mp3_file
        media_player.set_music(music)
    media_player.set_delay(song.mp3_delay)
    print('Done setting up')