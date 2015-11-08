# -*- coding: utf-8 -*-
"""Generate X11 keyboard events using the XTEST extension."""

from __future__ import absolute_import

import os
import time

if not 'DISPLAY' in os.environ:
    raise ImportError("The x11keyboard module can only function on Unix "
                      "systems with an X11 display.")

from Xlib import X
from Xlib.display import Display
from Xlib.XK import string_to_keysym

from .xtest import fake_key_event


__all__ = (
    'KEY_NAMES',
    'hotkey',
    'is_valid_key',
    'key_down',
    'key_up',
    'key_press',
    'typewrite'
)

__version__ = '0.1'

_display = None

def _get_display():
    global _display
    if _display is None:
        # TODO - Display() can have other values passed to it.
        # Implement that later.
        _display = Display(None)
    return _display


def _keycode(s):
    keysym = string_to_keysym(s)
    keycode = _get_display().keysym_to_keycode(keysym)
    return (keycode, keysym, _needs_shift(keycode, keysym))


def _needs_shift(keycode, keysym):
    """Returns True if the key character is uppercase or shifted."""
    display = _get_display()
    normal = display.keycode_to_keysym(keycode, 0)
    shifted = display.keycode_to_keysym(keycode, 1)
    return keysym == shifted and keysym != normal


_keysyms = {
    'add': 'KP_Add',
    'alt': 'Alt_L',
    'altleft': 'Alt_L',
    'altright': 'Alt_R',
    'apps': 'Super_L',
    'browserback': 'XF86_Back',
    'browserfavorites': 'XF86_Favorites',
    'browserforward': 'XF86_Forward',
    'browserhome': 'XF86_HomePage',
    'browserrefresh': 'XF86_Refresh',
    'browsersearch': 'XF86_Search',
    'browserstop': 'XF86_Stop',
    'backspace': 'BackSpace',
    'capslock': 'Caps_Lock',
    'clear': 'Clear',
    'command': 'Super_L',
    'ctrl': 'Control_L',
    'ctrlleft': 'Control_L',
    'ctrlright': 'Control_R',
    'decimal': 'KP_Decimal',
    'delete': 'Delete',
    'del': 'Delete',
    'divide': 'KP_Divide',
    'down': 'Down',
    'end': 'End',
    'enter': 'Return',
    'escape': 'Escape',
    'esc': 'Escape',
    'execute': 'Execute',
    'f10': 'F10',
    'f11': 'F11',
    'f12': 'F12',
    'f13': 'F13',
    'f14': 'F14',
    'f15': 'F15',
    'f16': 'F16',
    'f17': 'F17',
    'f18': 'F18',
    'f19': 'F19',
    'f1': 'F1',
    'f20': 'F20',
    'f21': 'F21',
    'f22': 'F22',
    'f23': 'F23',
    'f24': 'F24',
    'f2': 'F2',
    'f3': 'F3',
    'f4': 'F4',
    'f5': 'F5',
    'f6': 'F6',
    'f7': 'F7',
    'f8': 'F8',
    'f9': 'F9',
    'hangul': 'Hangul',
    'hanja': 'Hangul_Hanja',
    'help': 'Help',
    'home': 'Home',
    'insert': 'Insert',
    'kana': 'Katakana',
    'kanji': 'Kanji',
    'launchapp1': 'XF86_Launch0',
    'launchapp2': 'XF86_Launch1',
    'launchmail': 'XF86_Mail',
    'left': 'Left',
    'modechange': 'Mode_switch',
    'multiply': 'KP_Multiply',
    'nexttrack': 'XF86_AudioNext',
    'num0': 'KP_0',
    'num1': 'KP_1',
    'num2': 'KP_2',
    'num3': 'KP_3',
    'num4': 'KP_4',
    'num5': 'KP_5',
    'num6': 'KP_6',
    'num7': 'KP_7',
    'num8': 'KP_8',
    'num9': 'KP_9',
    'numlock': 'Num_Lock',
    'option': 'XF86_Option',
    'optionleft': 'XF86_Option',
    'optionright': 'XF86_Option',
    'pagedown': 'Page_Down',
    'pageup': 'Page_Up',
    'pause': 'Pause',
    'pgdn': 'Page_Down',
    'pgup': 'Page_Up',
    'playpause': 'XF86_AudioPlay',
    'prevtrack': 'XF86_AudioPrev',
    'print': 'Print',
    'printscreen': 'Print',
    'prntscrn': 'Print',
    'prtsc': 'Print',
    'prtscr': 'Print',
    'return': 'Return',
    'right': 'Right',
    'scrolllock': 'Scroll_Lock',
    'select': 'Select',
    'separator': 'KP_Separator',
    'shift': 'Shift_L',
    'shiftleft': 'Shift_L',
    'shiftright': 'Shift_R',
    'sleep': 'XF86_Sleep',
    'space': 'space',
    'stop': 'XF86_AudioStop',
    'subtract': 'KP_Subtract',
    'tab': 'Tab',
    'up': 'Up',
    'volumedown': 'XF86_AudioLowerVolume',
    'volumemute': 'XF86_AudioMute',
    'volumeup': 'XF86_AudioRaiseVolume',
    'win': 'Super_L',
    'winleft': 'Super_L',
    'winright': 'Super_R',
    'yen': 'yen',
    '\b': 'BackSpace',
    '\e': 'Escape',
    '\n': 'Return',
    '\r': 'Return',
    '\t': 'Tab',
    '\\': 'backslash',
    '&': 'ampersand',
    "'": 'apostrophe',
    '^': 'asciicircum',
    '~': 'asciitilde',
    '*': 'asterisk',
    '@': 'at',
    '|': 'bar',
    '{': 'braceleft',
    '}': 'braceright',
    '[': 'bracketleft',
    ']': 'bracketright',
    ':': 'colon',
    ',': 'comma',
    '$': 'dollar',
    '=': 'equal',
    '!': 'exclam',
    '`': 'grave',
    '>': 'greater',
    '<': 'less',
    '-': 'minus',
    '#': 'numbersign',
    '(': 'parenleft',
    ')': 'parenright',
    '%': 'percent',
    '.': 'period',
    '+': 'plus',
    '?': 'question',
    '"': 'quotedbl',
    ';': 'semicolon',
    '/': 'slash',
    ' ': 'space',
    '_': 'underscore'
}

# The _keyname2keycode dict maps a string that can be passed to key_down(),
# key_up(), or key_press() into a 3-item tuple with the OS-specific keyboard
# code, the keyboard symbolic name, and a boolean indicating, whether shift
# must be pressed to generate the key string using this keycode.
#
# The key string should always be lowercase, and the same keys should be used
# across all OSes.

_keyname2keycode = {}

for key in _keysyms:
    keysym = _keysyms[key]
    keyspec = _keycode(keysym)
    _keyname2keycode[key] = _keyname2keycode[keysym.lower()] = keyspec

for key in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890":
    _keyname2keycode[key] = _keycode(key)

SHIFT = _keyname2keycode['shift'][0]
KEY_NAMES = list(_keyname2keycode) + [
    # Included for compatibility with PyAutoGUI. We don't support these.
    'accept', 'convert', 'final', 'fn', 'hanguel', 'junja',
    'launchmediaselect', 'nonconvert'
]



def is_valid_key(key):
    """Returns a Boolean value if the given key is a valid value to pass
    key_down() or key_up().

    This function is here because passing an invalid value to the PyAutoGUI
    keyboard functions currently is a no-op that does not raise an exception.

    Some keys are only valid on some platforms. For example, while 'esc' is
    valid for the Escape key on all platforms, 'browserback' is only used on
    Windows operating systems.

    Args:
      key (str): The key value.

    Returns:
      bool: True if key is a valid value, False if not.

    """
    return key in _keyname2keycode


def key_down(key):
    """Performs a keyboard key press without the release. This will put that
    key in a held down state.

    NOTE: For some reason, this does not seem to cause key repeats like would
    happen if a keyboard key was held down on a text field.

    Args:
      key (str): The key to be pressed down. The valid names are listed in
      KEY_NAMES.

    Returns:
      None

    """
    if isinstance(key, int):
        fake_key_event(key)
    else:
        keyspec = _keyname2keycode.get(key.lower())

        if not keyspec:
            return

        if keyspec[2]:
            fake_key_event(SHIFT)

        fake_key_event(keyspec[0])

        if keyspec[2]:
            fake_key_event(SHIFT, False)

    _get_display().sync()


def key_up(key):
    """Performs a keyboard key release (without the press down beforehand).

    Release a given character key. Also works with character keycodes as
    integers, but not keysyms.

    Args:
      key (str): The key to be released up. The valid names are listed in
      KEY_NAMES.

    Returns:
      None

    """
    if isinstance(key, int):
        fake_key_event(key, False)
    else:
        keyspec = _keyname2keycode.get(key.lower())

        if not keyspec:
            return

        fake_key_event(keyspec[0], False)

    _get_display().sync()


def key_press(keys, presses=1, interval=0.0):
    """Performs a keyboard key press down, followed by a release.

    Args:
      key (str, list): The key to be pressed. The valid names are listed in
        KEY_NAMES. Can also be a list of such strings.
      presses (integer, optional): the number of press repetition
        1 by default, for just one press
      interval (float, optional): How many seconds between each press.
        0.0 by default, for no pause between presses.

    Returns:
      None

    """
    if type(keys) == str:
        keys = [keys] # put string in a list

    for i in range(presses):
        for k in keys:
            key_down(k)
            key_up(k)

            if interval:
                time.sleep(interval)


def typewrite(message, interval=0.0):
    """Performs a keyboard key press down, followed by a release, for each of
    the characters in message.

    The message argument can also be list of strings, in which case any valid
    keyboard name can be used.

    Since this performs a sequence of keyboard presses and does not hold down
    keys, it cannot be used to perform keyboard shortcuts. Use the hotkey()
    function for that.

    Args:
      message (str, list): If a string, then the characters to be pressed. If a
        list, then the key names of the keys to press in order. The valid names
        are listed in KEYBOARD_KEYS.
      interval (float, optional): The number of seconds in between each press.
        0.0 by default, for no pause in between presses.

    Returns:
      None

    """
    for c in message:
        press(c)
        time.sleep(interval)


def hotkey(*args, **kwargs):
    """Performs key down presses on the arguments passed in order, then
    performs key releases in reverse order.

    The effect is that calling hotkey('ctrl', 'shift', 'c') would perform a
    "Ctrl-Shift-C" hotkey/keyboard shortcut press.

    Args:
      key(s) (str): The series of keys to press, in order. This can also be a
        list of key strings to press.
      interval (float, optional): The number of seconds in between each press.
        0.0 by default, for no pause in between presses.

    Returns:
      None

    """
    interval = kwargs.get('interval', 0.0)

    for c in args:
        key_down(c)

        if interval:
            time.sleep(interval)

    for c in reversed(args):
        key_up(c)

        if interval:
            time.sleep(interval)
