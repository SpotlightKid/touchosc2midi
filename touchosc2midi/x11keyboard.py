# -*- coding: utf-8 -*-

import os
import time

if not 'DISPLAY' in os.environ:
    raise ImportError("The x11keyboard module can only function on Unix "
                      "systems with an X11 display.")

from Xlib import X
from Xlib.display import Display
from Xlib.ext.xtest import fake_input
from Xlib.XK import string_to_keysym


__all__ = (
    'KEY_NAMES',
    'hotkey',
    'is_valid_key',
    'key_down',
    'key_up',
    'press',
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
    return (_get_display().keysym_to_keycode(keysym), keysym)


def _needs_shift(keycode, keysym):
    """Returns True if the key character is uppercase or shifted."""
    return keysym == _get_display().keycode_to_keysym(keycode, 1)


KEY_NAMES = [
    '\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(',
    ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7',
    '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`',
    'a', 'b', 'c', 'd', 'e','f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
    'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~',
    'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace',
    'browserback', 'browserfavorites', 'browserforward', 'browserhome',
    'browserrefresh', 'browsersearch', 'browserstop', 'capslock', 'clear',
    'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete',
    'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10',
    'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20',
    'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9',
    'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert',
    'junja', 'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail',
    'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack',
    'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6',
    'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn',
    'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn',
    'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator',
    'shift', 'shiftleft', 'shiftright', 'sleep', 'stop', 'subtract', 'tab',
    'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright',
    'yen', 'command', 'option', 'optionleft', 'optionright'
]

# The _keyname2keycode dict maps a string that can be passed to key_down(),
# key_up(), or press() into the OS-specific keyboard code.
#
# They should always be lowercase, and the same keys should be used across all
# OSes.

_keyname2keycode = {key: None for key in KEY_NAMES}

for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890":
    _keyname2keycode[c] = _keycode(c)

_keyname2keycode.update({
    'backspace':    _keycode('BackSpace'),
    '\b':           _keycode('BackSpace'),
    'tab':          _keycode('Tab'),
    'enter':        _keycode('Return'),
    'return':       _keycode('Return'),
    'shift':        _keycode('Shift_L'),
    'ctrl':         _keycode('Control_L'),
    'alt':          _keycode('Alt_L'),
    'pause':        _keycode('Pause'),
    'capslock':     _keycode('Caps_Lock'),
    'esc':          _keycode('Escape'),
    'escape':       _keycode('Escape'),
    'pgup':         _keycode('Page_Up'),
    'pgdn':         _keycode('Page_Down'),
    'pageup':       _keycode('Page_Up'),
    'pagedown':     _keycode('Page_Down'),
    'end':          _keycode('End'),
    'home':         _keycode('Home'),
    'left':         _keycode('Left'),
    'up':           _keycode('Up'),
    'right':        _keycode('Right'),
    'down':         _keycode('Down'),
    'select':       _keycode('Select'),
    'print':        _keycode('Print'),
    'execute':      _keycode('Execute'),
    'prtsc':        _keycode('Print'),
    'prtscr':       _keycode('Print'),
    'prntscrn':     _keycode('Print'),
    'printscreen':  _keycode('Print'),
    'insert':       _keycode('Insert'),
    'del':          _keycode('Delete'),
    'delete':       _keycode('Delete'),
    'help':         _keycode('Help'),
    'winleft':      _keycode('Super_L'),
    'winright':     _keycode('Super_R'),
    'apps':         _keycode('Super_L'),
    'num0':         _keycode('KP_0'),
    'num1':         _keycode('KP_1'),
    'num2':         _keycode('KP_2'),
    'num3':         _keycode('KP_3'),
    'num4':         _keycode('KP_4'),
    'num5':         _keycode('KP_5'),
    'num6':         _keycode('KP_6'),
    'num7':         _keycode('KP_7'),
    'num8':         _keycode('KP_8'),
    'num9':         _keycode('KP_9'),
    'multiply':     _keycode('KP_Multiply'),
    'add':          _keycode('KP_Add'),
    'separator':    _keycode('KP_Separator'),
    'subtract':     _keycode('KP_Subtract'),
    'decimal':      _keycode('KP_Decimal'),
    'divide':       _keycode('KP_Divide'),
    'f1':           _keycode('F1'),
    'f2':           _keycode('F2'),
    'f3':           _keycode('F3'),
    'f4':           _keycode('F4'),
    'f5':           _keycode('F5'),
    'f6':           _keycode('F6'),
    'f7':           _keycode('F7'),
    'f8':           _keycode('F8'),
    'f9':           _keycode('F9'),
    'f10':          _keycode('F10'),
    'f11':          _keycode('F11'),
    'f12':          _keycode('F12'),
    'f13':          _keycode('F13'),
    'f14':          _keycode('F14'),
    'f15':          _keycode('F15'),
    'f16':          _keycode('F16'),
    'f17':          _keycode('F17'),
    'f18':          _keycode('F18'),
    'f19':          _keycode('F19'),
    'f20':          _keycode('F20'),
    'f21':          _keycode('F21'),
    'f22':          _keycode('F22'),
    'f23':          _keycode('F23'),
    'f24':          _keycode('F24'),
    'numlock':      _keycode('Num_Lock'),
    'scrolllock':   _keycode('Scroll_Lock'),
    'shiftleft':    _keycode('Shift_L'),
    'shiftright':   _keycode('Shift_R'),
    'ctrlleft':     _keycode('Control_L'),
    'ctrlright':    _keycode('Control_R'),
    'altleft':      _keycode('Alt_L'),
    'altright':     _keycode('Alt_R'),
    # These are added because unlike a-z, A-Z, 0-9,
    # the single characters do not have a ???
    ' ':            _keycode('space'),
    'space':        _keycode('space'),
    '\t':           _keycode('Tab'),
    # for some reason this needs to be cr, not lf XXX: ???
    '\n':           _keycode('Return'),
    '\r':           _keycode('Return'),
    '\e':           _keycode('Escape'),
    '!':            _keycode('exclam'),
    '#':            _keycode('numbersign'),
    '%':            _keycode('percent'),
    '$':            _keycode('dollar'),
    '&':            _keycode('ampersand'),
    '"':            _keycode('quotedbl'),
    "'":            _keycode('apostrophe'),
    '(':            _keycode('parenleft'),
    ')':            _keycode('parenright'),
    '*':            _keycode('asterisk'),
    '=':            _keycode('equal'),
    '+':            _keycode('plus'),
    ',':            _keycode('comma'),
    '-':            _keycode('minus'),
    '.':            _keycode('period'),
    '/':            _keycode('slash'),
    ':':            _keycode('colon'),
    ';':            _keycode('semicolon'),
    '<':            _keycode('less'),
    '>':            _keycode('greater'),
    '?':            _keycode('question'),
    '@':            _keycode('at'),
    '[':            _keycode('bracketleft'),
    ']':            _keycode('bracketright'),
    '\\':           _keycode('backslash'),
    '^':            _keycode('asciicircum'),
    '_':            _keycode('underscore'),
    '`':            _keycode('grave'),
    '{':            _keycode('braceleft'),
    '|':            _keycode('bar'),
    '}':            _keycode('braceright'),
    '~':            _keycode('asciitilde'),
})

SHIFT = _keyname2keycode['shift'][0]


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
    return _keyname2keycode.get(key) is not None


# Much of this code is based on information gleaned from Paul Barton's
# PyKeyboard in PyUserInput from 2013, itself derived from Akkana Peck's pykey
# in 2008 (http://www.shallowsky.com/software/crikey/pykey-0.1), itself derived
# from her "Crikey" lib.

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
        fake_input(_display, X.KeyPress, key)
    else:
        keyspec = _keyname2keycode.get(key.lower())

        if not keyspec:
            return

        _shift = _needs_shift(*keyspec)

        if _shift:
            fake_input(_display, X.KeyPress, SHIFT)

        fake_input(_display, X.KeyPress, keyspec[0])

        if _shift:
            fake_input(_display, X.KeyRelease, SHIFT)

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
        fake_input(_display, X.KeyRelease, key)
    else:
        keyspec = _keyname2keycode.get(key.lower())

        if not keyspec:
            return

        fake_input(_display, X.KeyRelease, keyspec[0])

    _get_display().sync()


def press(keys, presses=1, interval=0.0):
    """Performs a keyboard key press down, followed by a release.

    Args:
      key (str, list): The key to be pressed. The valid names are listed in
        KEY_NAMES. Can also be a list of such strings.
      presses (integer, optiional): the number of press repetition
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
