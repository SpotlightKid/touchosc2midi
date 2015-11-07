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


# The _keyname2keycode dict maps a string that can be passed to key_down(),
# key_up(), or key_press() into the OS-specific keyboard code.
#
# They should always be lowercase, and the same keys should be used across all
# OSes.

_keyname2keycode = {
    'add': _keycode('KP_Add'),
    'alt': _keycode('Alt_L'),
    'altleft': _keycode('Alt_L'),
    'altright': _keycode('Alt_R'),
    'apps': _keycode('Super_L'),
    'browserback': _keycode('XF86_Back'),
    'browserfavorites': _keycode('XF86_Favorites'),
    'browserforward': _keycode('XF86_Forward'),
    'browserhome': _keycode('XF86_HomePage'),
    'browserrefresh': _keycode('XF86_Refresh'),
    'browsersearch': _keycode('XF86_Search'),
    'browserstop': _keycode('XF86_Stop'),
    'backspace': _keycode('BackSpace'),
    'capslock': _keycode('Caps_Lock'),
    'clear': _keycode('Clear'),
    'command': _keycode('Super_L'),
    'ctrl': _keycode('Control_L'),
    'ctrlleft': _keycode('Control_L'),
    'ctrlright': _keycode('Control_R'),
    'decimal': _keycode('KP_Decimal'),
    'delete': _keycode('Delete'),
    'del': _keycode('Delete'),
    'divide': _keycode('KP_Divide'),
    'down': _keycode('Down'),
    'end': _keycode('End'),
    'enter': _keycode('Return'),
    'escape': _keycode('Escape'),
    'esc': _keycode('Escape'),
    'execute': _keycode('Execute'),
    'f10': _keycode('F10'),
    'f11': _keycode('F11'),
    'f12': _keycode('F12'),
    'f13': _keycode('F13'),
    'f14': _keycode('F14'),
    'f15': _keycode('F15'),
    'f16': _keycode('F16'),
    'f17': _keycode('F17'),
    'f18': _keycode('F18'),
    'f19': _keycode('F19'),
    'f1': _keycode('F1'),
    'f20': _keycode('F20'),
    'f21': _keycode('F21'),
    'f22': _keycode('F22'),
    'f23': _keycode('F23'),
    'f24': _keycode('F24'),
    'f2': _keycode('F2'),
    'f3': _keycode('F3'),
    'f4': _keycode('F4'),
    'f5': _keycode('F5'),
    'f6': _keycode('F6'),
    'f7': _keycode('F7'),
    'f8': _keycode('F8'),
    'f9': _keycode('F9'),
    'hangul': _keycode('Hangul'),
    'hanja': _keycode('Hangul_Hanja'),
    'help': _keycode('Help'),
    'home': _keycode('Home'),
    'insert': _keycode('Insert'),
    'kana': _keycode('Katakana'),
    'kanji': _keycode('Kanji'),
    'launchapp1': _keycode('XF86_Launch0'),
    'launchapp2': _keycode('XF86_Launch1'),
    'launchmail': _keycode('XF86_Mail'),
    'left': _keycode('Left'),
    'modechange': _keycode('Mode_switch'),
    'multiply': _keycode('KP_Multiply'),
    'nexttrack': _keycode('XF86_AudioNext'),
    'num0': _keycode('KP_0'),
    'num1': _keycode('KP_1'),
    'num2': _keycode('KP_2'),
    'num3': _keycode('KP_3'),
    'num4': _keycode('KP_4'),
    'num5': _keycode('KP_5'),
    'num6': _keycode('KP_6'),
    'num7': _keycode('KP_7'),
    'num8': _keycode('KP_8'),
    'num9': _keycode('KP_9'),
    'numlock': _keycode('Num_Lock'),
    'option': _keycode('XF86_Option'),
    'optionleft': _keycode('XF86_Option'),
    'optionright': _keycode('XF86_Option'),
    'pagedown': _keycode('Page_Down'),
    'pageup': _keycode('Page_Up'),
    'pause': _keycode('Pause'),
    'pgdn': _keycode('Page_Down'),
    'pgup': _keycode('Page_Up'),
    'playpause': _keycode('XF86_AudioPlay'),
    'prevtrack': _keycode('XF86_AudioPrev'),
    'print': _keycode('Print'),
    'printscreen': _keycode('Print'),
    'prntscrn': _keycode('Print'),
    'prtsc': _keycode('Print'),
    'prtscr': _keycode('Print'),
    'return': _keycode('Return'),
    'right': _keycode('Right'),
    'scrolllock': _keycode('Scroll_Lock'),
    'select': _keycode('Select'),
    'separator': _keycode('KP_Separator'),
    'shift': _keycode('Shift_L'),
    'shiftleft': _keycode('Shift_L'),
    'shiftright': _keycode('Shift_R'),
    'sleep': _keycode('XF86_Sleep'),
    'space': _keycode('space'),
    'stop': _keycode('XF86_AudioStop'),
    'subtract': _keycode('KP_Subtract'),
    'tab': _keycode('Tab'),
    'up': _keycode('Up'),
    'volumedown': _keycode('XF86_AudioLowerVolume'),
    'volumemute': _keycode('XF86_AudioMute'),
    'volumeup': _keycode('XF86_AudioRaiseVolume'),
    'win': _keycode('Super_L'),
    'winleft': _keycode('Super_L'),
    'winright': _keycode('Super_R'),
    'yen': _keycode('yen'),
    '\b': _keycode('BackSpace'),
    '\e': _keycode('Escape'),
    '\n': _keycode('Return'),
    '\r': _keycode('Return'),
    '\t': _keycode('Tab'),
    '\\': _keycode('backslash'),
    '&': _keycode('ampersand'),
    "'": _keycode('apostrophe'),
    '^': _keycode('asciicircum'),
    '~': _keycode('asciitilde'),
    '*': _keycode('asterisk'),
    '@': _keycode('at'),
    '|': _keycode('bar'),
    '{': _keycode('braceleft'),
    '}': _keycode('braceright'),
    '[': _keycode('bracketleft'),
    ']': _keycode('bracketright'),
    ':': _keycode('colon'),
    ',': _keycode('comma'),
    '$': _keycode('dollar'),
    '=': _keycode('equal'),
    '!': _keycode('exclam'),
    '`': _keycode('grave'),
    '>': _keycode('greater'),
    '<': _keycode('less'),
    '-': _keycode('minus'),
    '#': _keycode('numbersign'),
    '(': _keycode('parenleft'),
    ')': _keycode('parenright'),
    '%': _keycode('percent'),
    '.': _keycode('period'),
    '+': _keycode('plus'),
    '?': _keycode('question'),
    '"': _keycode('quotedbl'),
    ';': _keycode('semicolon'),
    '/': _keycode('slash'),
    ' ': _keycode('space'),
    '_': _keycode('underscore'),
}

for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890":
    _keyname2keycode[c] = _keycode(c)

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
