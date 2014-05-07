'''
Created on Jul 8, 2013

@author: matt

Custom Clock Function
Custom Media Player
Custom Window
'''

import time
import pyglet
import setup_animation
import config_parse

# MIDI tick based clock, pause/unpause functionality
class PlaybackClock(pyglet.clock.Clock):
    def __init__(self,tpqn=96,tempo=120):        
        self.running = False
        self.tpqn = tpqn # Ticks per quarter note
        self.ticks_per_second = self.tpqn*tempo/60
        self.ticks_elapsed = 0
        self.reference_time = time.time()
        super(PlaybackClock, self).__init__(time_function=self.time_function)
        # Tick clock with main clock
        pyglet.clock.schedule(lambda dt: self.tick())
        
    def time_function(self):
        self.current_time = time.time()
        if self.running == True:
            self.time_value = self.ticks_per_second*(self.current_time - self.reference_time) + self.ticks_elapsed
        else:
            self.time_value = self.ticks_elapsed
        return self.time_value
    
    def reset_timer(self):
        # Kill current timer and make a whole new one
        pyglet.clock.unschedule(lambda dt: self.tick())
        return PlaybackClock()
        
    def start_timer(self):
        if self.running == False:
            self.reference_time = time.time()     
            self.running = True

    def stop_timer(self):
        if self.running == True:
            current_time = time.time()
            self.ticks_elapsed += self.ticks_per_second*(current_time - self.reference_time)
            self.running = False
        
    def change_tempo(self,dt,tempo):
        current_time = time.time()
        if self.running == True: #Increment ticks elapsed only if timer is running
            self.ticks_elapsed += self.ticks_per_second*(current_time - self.reference_time)
            self.reference_time = current_time
        self.ticks_per_second = self.tpqn*tempo/60
        
# Media player setup
class DelayStartPlayer(pyglet.media.Player):
    def __init__(self,delay=0,volume=0.4,music_path=None):
        self.mp3_started = False
        self.delay = delay
        super(DelayStartPlayer, self).__init__()
        self.volume = volume
        self.music_path = music_path
        if music_path is not None:
            self.queue(pyglet.media.load(self.music_path))
    
    def kill_player(self):
        pyglet.clock.unschedule(self.start_media_player)
        self.pause()
    
    def play_media(self):
        if self.mp3_started == False:
            pyglet.clock.schedule_once(self.start_media_player, self.delay)
        else:
            self.play()
        
    def start_media_player(self,dt):
        self.mp3_started = True        
        self.play()
        
    def set_delay(self,delay):
        self.delay = delay
        
    def set_music(self,music):
        self.music_path = music
        self.queue(pyglet.media.load(self.music_path))
        
# Custom window
class PlaybackWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(PlaybackWindow, self).__init__(*args, **kwargs)

        self.main_batch = pyglet.graphics.Batch()
        self.media_player = DelayStartPlayer()
        self.midi_clock = PlaybackClock()
        self.data = None
        self.help_toggle = True # Read from preferences?
        self.setup_handler = SetupEventHandler(self)
        self.playback_handler = PlaybackEventHandler(self)
        
        self.push_handlers(self.setup_handler)
        
        self.draw_text('title','setup_help')
        
        self.fps_display = pyglet.clock.ClockDisplay()
        
    # Event setup    
    def on_draw(self):
        self.clear()
        self.main_batch.draw()
        self.fps_display.draw()

    def on_key_press(self,symbol,modifiers):
        # Close window with escape
        if symbol == pyglet.window.key.ESCAPE:
            self.dispatch_event('on_close')
                
    def draw_text(self,*args):
        if 'title' in args:
                self.title_text = pyglet.text.Label("SYNESTHESIA",
                                                         font_name='Arial',
                                                         font_size=28,
                                                         x=self.width/2,
                                                         y=self.height/2,
                                                         anchor_x='center',
                                                         anchor_y='center',
                                                         batch=self.main_batch)
        if self.help_toggle:
            if 'setup_help' in args:
                self.help_text_setup = pyglet.text.Label('Ctrl+N: Setup New Config File | Ctrl+L: Load Config File |  Esc: Close program | ?: Toggle Help Text',
                                                         font_name='Arial',
                                                         font_size=10,
                                                         x=0,
                                                         y=0,
                                                         anchor_x='left',
                                                         anchor_y='bottom',
                                                         batch=self.main_batch)
            if 'playback_help' in args:
                self.help_text_playback = pyglet.text.Label('Space: Play/Pause | Backspace: Restart | Esc: Return to Setup Menu | ?: Toggle Help Text',
                                                 font_name='Arial',
                                                 font_size=10,
                                                 x=0,
                                                 y=0,
                                                 anchor_x='left',
                                                 anchor_y='bottom',
                                                 batch=self.main_batch,
                                                 group=pyglet.graphics.OrderedGroup(255))
    def delete_text(self,*args):
        if 'title' in args:
            self.title_text.delete()
        if 'setup_help' in args:
            self.help_text_setup.delete()
        if 'playback_help' in args:
            self.help_text_playback.delete()
            
class SetupEventHandler(object):
    def __init__(self, window):
        self.window = window
        self.is_busy = False
    def on_key_press(self,symbol,modifiers):
        if symbol == pyglet.window.key.N and (modifiers & pyglet.window.key.MOD_CTRL):
            if not self.is_busy:
                config_parse.create_new_config()   
        if symbol == pyglet.window.key.L and (modifiers & pyglet.window.key.MOD_CTRL):
            if not self.is_busy:
                self.is_busy = True
                #print("Setting up")
                self.window.data = setup_animation.get_data(self.window)
                if self.window.data: # If actual data is returned
                    setup_animation.setup_animation(self.window, self.window.data)

                    # Switch to playback mode
                    self.window.pop_handlers()
                    self.window.delete_text('title','setup_help')
                    self.window.push_handlers(self.window.playback_handler)
                    self.window.draw_text('playback_help')
                    #print("Done setting up")
                self.is_busy = False                    
        if symbol == pyglet.window.key.SLASH and (modifiers & pyglet.window.key.MOD_SHIFT):
            if self.window.help_toggle:
                self.window.help_toggle = False
                self.window.delete_text('setup_help')
            else:
                self.window.help_toggle = True
                self.window.draw_text('setup_help')
            
class PlaybackEventHandler(object):
    def __init__(self, window):
        self.window = window
        self.is_paused = True
    def on_key_press(self,symbol,modifiers):        
        # Start and stop things with space bar
        if symbol == pyglet.window.key.SPACE:
            if self.is_paused:
                self.play()
            else:
                self.pause()
        # Reset with backspace
        if symbol == pyglet.window.key.BACKSPACE:
            if not self.is_paused:
                self.pause()
            self.reset()
        if symbol == pyglet.window.key.ESCAPE:
            if not self.is_paused:
                self.pause()
            self.destroy()
            # Switch to setup mode
            self.window.pop_handlers()
            self.window.delete_text('playback_help')
            self.window.push_handlers(self.window.setup_handler)
            self.window.draw_text('title','setup_help')
            return True
        if symbol == pyglet.window.key.SLASH and (modifiers & pyglet.window.key.MOD_SHIFT):
            if self.is_paused:
                if self.window.help_toggle:
                    self.window.help_toggle = False
                    self.window.delete_text('playback_help')
                else:
                    self.window.help_toggle = True
                    self.window.draw_text('playback_help')        
            
    def destroy(self):
        self.is_paused = True
        self.window.media_player.kill_player()
        self.window.media_player = DelayStartPlayer()
        self.window.midi_clock = PlaybackClock()
        self.window.main_batch = pyglet.graphics.Batch()
             
    def play(self):
        self.is_paused = False
        self.window.media_player.play_media()
        self.window.midi_clock.start_timer()
        self.window.delete_text('playback_help')
        
    def pause(self):
        self.is_paused = True
        self.window.media_player.pause()
        self.window.midi_clock.stop_timer()
        
    def reset(self):
        self.is_paused = True
        music = self.window.media_player.music_path
        delay = self.window.media_player.delay
        self.window.media_player = DelayStartPlayer(delay=delay,music_path=music)
        self.window.midi_clock = PlaybackClock()
        self.window.main_batch = pyglet.graphics.Batch()
        setup_animation.setup_animation(self.window, self.window.data)
        self.window.draw_text('playback_help')
