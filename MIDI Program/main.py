'''
Created on Jul 5, 2013

@author: matt
'''

import pyglet
pyglet.options['graphics_vbo'] = False
pyglet.options['debug_graphics_batch'] = False
from pyglet.gl import *
from classes import PlaybackWindow

def initial_setup():
    # OpenGL setup
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_POLYGON_SMOOTH)
    glHint(GL_POLYGON_SMOOTH_HINT,GL_NICEST)
   
    # Window setup
    config = pyglet.gl.Config(double_buffer=1)
    main_window = PlaybackWindow(1280, 720, config=config)
   
    return main_window

if __name__ == '__main__':
    main_window = initial_setup()
    pyglet.app.run()
