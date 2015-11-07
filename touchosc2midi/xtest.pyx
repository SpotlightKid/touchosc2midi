# xtest.pyx
"""Minimal wrapper for XTest X server extension interface.

Used to generate fake X Windows keyboard events.

"""

cdef extern from "X11/extensions/XTest.h":
    ctypedef int Bool
    cdef struct _XDisplay:
        pass
    ctypedef _XDisplay Display

    cdef Bool XTestQueryExtension(Display*, int* event_base, int* error_basep,
                                  int* major, int* minor)
    cdef int XTestFakeKeyEvent(Display*, unsigned int keycode, Bool is_press,
                               unsigned long delay)
    cdef Display * XOpenDisplay(char* name)
    cdef int XSync(Display*, Bool onoff)


# keysym = XkbKeycodeToKeysym(display, keycode, 0, 0)

cdef Display* _display

cdef Display* _get_display():
    cdef int opcode, event_base, error_base, major_version, minor_version
    global _display

    if _display == NULL:
        _display = XOpenDisplay(NULL)

        if _display == NULL:
            raise RuntimeError("Unable to open X display.")

        if not XTestQueryExtension(_display, &event_base, &error_base,
                                   &major_version, &minor_version):
            raise NotImplementedError("XTest extension is not available!")

    return _display


def fake_key_event(unsigned int keycode, Bool is_press=True,
                   unsigned long delay=0):
    cdef Display* display = _get_display()

    XTestFakeKeyEvent(display, keycode, is_press, delay)
    XSync(display, False)
