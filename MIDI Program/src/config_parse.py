'''
Created on Feb 7, 2014

@author: Matt
'''

from configobj import ConfigObj, flatten_errors
import tkinter as tk
import tkinter.filedialog as filedialog
import os
import validate as val
import midi_parse

def create_new_config():
    '''
    Create new config file from MIDI file
    '''
    root = tk.Tk()
    root.withdraw()
    options = {'defaultextension':'.mid',
               'filetypes':[('MIDI', '.mid'),('All files', '.*')],
               'initialdir':os.path.expanduser('~'),
               'parent':root,
               'title':'Choose MIDI file'}
    midi_filename = filedialog.askopenfilename(**options)
    if not midi_filename:
        return
    config_suggestion = midi_filename.split('/')[-1].split('.')[0]+'.ini'
    cfg_options = {'defaultextension':'.ini',
               'filetypes':[('Config File', '.ini')],
               'initialdir':os.path.expanduser('~'),
               'initialfile':config_suggestion,
               'parent':root,
               'title':'Choose location for config file'}
    config_filename = filedialog.asksaveasfilename(**cfg_options)
    if not config_filename:
        return
    mp3_options = {'defaultextension':'.mp3',
               'filetypes':[('All types', '.*')],
               'initialdir':os.path.expanduser('~'),
               'parent':root,
               'title':'Choose accompanying music'}
    mp3_filename = filedialog.askopenfilename(**mp3_options)
    new_config = ConfigObj()
    new_config.filename = config_filename
    
    song_data = {
                 'midi_file': midi_filename,
                 'mp3_file': mp3_filename,
                 'mp3_delay': 0,
                 'bg_color': [0,0,0,255]
                 }
    new_config['song_data'] = song_data
    
    track_data = {}
    midifile = midi_parse.MidiFile()
    midifile.read(midi_filename)  
    unk_index = 0
    extra_name_index = 1
    for t in midifile.tracks:
        for e in t.events:
            if e.type == 'SEQUENCE_TRACK_NAME':
                name = e.data.replace(b' ',b'_').decode(encoding='UTF-8')
                break
        else:
            name = 'Unknown_Name_{}'.format(unk_index)
            unk_index += 1
        # To prevent key errors in the event of duplicate track names
        if name in track_data.keys():
            name = name + '_{}'.format(extra_name_index)
            extra_name_index += 1
        track_data[name] = {'index':t.index,
                            'z_order':t.index,
                            'style':'simple',
                            'style_parameters':{
                                              'color':(255,0,0,255),
                                              'highlight_color': (255,200,200,255),
                                              }
                            }
    new_config['track_data'] = track_data
    new_config.write()
    root.destroy()

def read_config():
    print('Read config file')
    root = tk.Tk()
    root.withdraw()
    cfg_options = {'defaultextension':'.ini',
               'filetypes':[('Config File', '.ini')],
               'initialdir':os.path.expanduser('~'),
               'parent':root,
               'title':'Choose location for config file'}
    config_filename = filedialog.askopenfilename(**cfg_options)
    if not config_filename:
        print('No file opened')
        return None
    configspec_filename = os.path.join(os.path.dirname(__file__),os.pardir,'Resources\default_config.ini')
    validator = val.Validator()
    validator.functions['color_list'] = color_list
    config = ConfigObj(config_filename,configspec=configspec_filename)
    result = config.validate(validator)
    flat_result = flatten_errors(config,result)
    if flat_result:
        print('File not validated', flat_result)     
    else:
        return config

def color_list(value):
    """
    Function used in validator
    
    Check that the supplied value is a list of integers of length
    3 or 4 and the integers are between 0 and 255
    
    If length is 3, add 255 (full alpha channel) to list
    """
    # length is supplied as a string
    # we need to convert it to an integer
    #
    # Check the supplied value is a list
    if not isinstance(value, list):
        raise val.VdtTypeError(value)
    #
    # check the length of the list is correct
    if len(value) > 4:
        raise val.VdtValueTooLongError(value)
    elif len(value) < 3:
        raise val.VdtValueTooShortError(value)
    #
    # Next, check every member in the list
    # converting strings as necessary
    out = []
    for entry in value:
        if not isinstance(entry, (str, int)):
            # a value in the list
            # is neither an integer nor a string
            raise val.VdtTypeError(value)
        elif isinstance(entry, str):
            if not entry.isdigit():
                raise val.VdtTypeError(value)
            else:
                entry = int(entry)
        if entry < 0:
            raise val.VdtValueTooSmallError(value)
        elif entry > 255:
            raise val.VdtValueTooBigError(value)
        out.append(entry)
    if len(value) == 3:
        out.append(255)
    #
    # if we got this far, all is well
    # return the new list
    return out    