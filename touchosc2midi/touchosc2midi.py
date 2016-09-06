#!/usr/bin/env python
"""
touchosc2midi -- a TouchOSC to Midi Bridge.

(c) 2015 velolala <fiets@einstueckheilewelt.de>

Usage:
    touchosc2midi --help
    touchosc2midi list (backends | ports) [-v]
    touchosc2midi [(--midi-in <in> --midi-out <out>)] [--ip <oscserveraddress>] [-v] [-c]

Options:
    -h, --help                          Show this screen.
    --midi-in=<in>                      Full name or ID of midi input port.
    --midi-out=<out>                    Full name of or ID midi output port.
    --ip=<oscserveraddress>             Network address for OSC server (default: guess).
    -v, --verbose                       Verbose output.
    -c, --compliant                     Run in OSC spec compliant mode.
"""

from __future__ import absolute_import

import logging
import socket
import time

from functools import partial

import liblo
import mido

from docopt import docopt

from . import __version__
from .advertise import PORT, main_ip, Advertisement
from .configuration import list_backends, list_ports, configure_ioports, get_mido_backend

try:
    from .x11keyboard import key_down, key_press, key_up
    _have_x11 = True
except ImportError:
    _have_x11 = False


log = logging.getLogger(__name__)


def message_from_oscsysexpayload(payload):
    """Convert the OSC string into a mido sysex message.
    """
    payload = payload.lower()

    if len(payload) < 2:
        raise ValueError("sysex too short")
    elif not payload.startswith('f0'):
        raise ValueError("sysex doesn't start with F0")
    elif not payload.endswith('f7'):
        raise ValueError("sysex doesn't end with F7")

    sysex = tuple(int(payload[i:i+2], 16) for i in range(0, len(payload), 2))

    return mido.Message('sysex', data=sysex[1:-1])


def message_from_oscmidipayload(bites, compliant=True):
    """Convert the last 4 OSC-midi bytes into a mido message.
    """
    if not compliant and bites[-1] & 0x80:
        bites = bites[::-1]

    return mido.parse(bites[0:4])


def message_to_oscmidipayload(message, compliant=True):
    """Convert a mido Message instance into a 4-byte tuple for the OSC payload.

    The OSC 1.0 spec says:

    > Bytes from MSB to LSB are: port id, status byte, data1, data2

    However, TouchOSC uses: port id, data2, data1, status byte
    """
    bites = message.bytes()
    bites.extend([0] * (3 - len(bites)))

    if not compliant:
        bites.reverse()

    # FIXME: port-id is always 0?
    return tuple([0] + bites)


def message_to_oscsysexpayload(message):
    """Convert a sysex message into an OSC payload string.
    """
    return message.hex().replace(' ', '')


class OscHandler(object):
    _repl = {'control': 'ctrl', 'command': 'win'}

    def __init__(self, sink, compliant=False):
        self.sink = sink
        self.compliant = compliant
        self._program = {}

    def _log_osc(self, path, args, types, src):
        log.debug("OSC received {},{} {!r} from: {}:{} UDP: {} URL: {}".format(
            path,
            types,
            args,
            src.get_hostname(),
            src.get_port(),
            src.get_protocol() == liblo.UDP,
            src.get_url()))

    def dispatch(self, path, args, types, src):
        if path.startswith('/key/') and types == 'f':
            self.on_key(path, args, types, src)

    def on_midi(self, path, args, types, src):
        self._log_osc(path, args, types, src)
        if path == '/midi' and types == 'm':
            msg = message_from_oscmidipayload(args[0], self.compliant)
        elif path == '/sysex' and types == 's':
            msg = message_from_oscsysexpayload(args[0])

        msg = self.filter_message(msg)

        if msg:
            log.debug("Sending MIDI message {}".format(msg))
            self.sink.send(msg)
        else:
            log.warning("OSC message did not yield a valid MIDI message.")

    def on_key(self, path, args, types, src):
        self._log_osc(path, args, types, src)
        if _have_x11:
            if path == '/key' and types == 'si':
                key, state = args
                keys = [self._repl.get(k, k) for k in key.lower().split('+')]

                if state == 0:
                    for key in keys:
                        key_down(key)
                elif state == 1:
                    for key in reversed(keys):
                        key_up(key)
            elif path.startswith('/key/') and types == 'f':
                key = path.split('/', 2)[-1]
                key = self._repl.get(key, key)

                if key == 'capslock':
                    key_press(key)
                elif bool(args[0]):
                    key_down(key)
                else:
                    key_up(key)

    def filter_message(self, msg):
        if msg is None:
            return

        if msg.type == 'program_change':
            # ignore repeated program change on same channel
            if msg.program == self._program.get(msg.channel):
                return
            else:
                self._program[msg.channel] = msg.program
        elif msg.type == 'control_change':
            # ignore channel mode messages (except local on/off)
            # with value >= 64
            if (msg.control in (120, 121, 123, 124, 125, 126, 127) and
                    msg.value >= 64):
                return

        return msg


class MidiHandler(object):
    def __init__(self, target, compliant=True):
        self.target = target
        self.compliant = compliant

    def on_midi(self, message):
        if message.type == "clock":
            return

        log.debug("MIDI received: {}".format(message))

        if message.type == "sysex":
            addr = '/sysex'
            arg = ('s', message_to_oscsysexpayload(message))
        else:
            addr = '/midi'
            arg = ('m', message_to_oscmidipayload(message, self.compliant))

        osc = liblo.Message(addr, arg)
        log.debug("Sending OSC {}, {} to: {}:{} UDP: {} URL: {}".format(
            addr,
            arg,
            self.target.get_hostname(),
            self.target.get_port(),
            self.target.get_protocol() == liblo.UDP,
            self.target.get_url()))
        liblo.send(self.target, osc)


def wait_for_target_address(ip=None):
    """Waits for a byte on the OSC-PORT to arrive.
    Extract the sender IP-address, this will become our OSC target.
    """
    log.info("Waiting for first package from TouchOSC in order to setup target address...")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((ip or main_ip(), PORT))
    _, (address, _) = s.recvfrom(1)
    return address


def main():
    OSCPORT = 9001

    options = docopt(__doc__, version=__version__)
    logging.basicConfig(level=logging.DEBUG if options.get('--verbose') else logging.INFO,
                        format="%(message)s")

    log.debug("Options from cmdline are {}".format(options))
    backend = get_mido_backend()

    if not _have_x11:
        log.warning("Could not import X Windows library. Support for "
                    "generating keyboard events will not be available.")

    if options.get('list'):
        if options.get('backends'):
            list_backends()
        elif options.get('ports'):
            list_ports(backend)
    else:
        try:
            midibridge = keybridge = None
            midi_in, midi_out = configure_ioports(backend,
                                                  virtual=not (options.get('--midi-in') or
                                                               options.get('--midi-out')),
                                                  mido_in=options.get('--midi-in'),
                                                  mido_out=options.get('--midi-out'))

            psa = Advertisement(ip=options.get('--ip'))
            psa.register()

            target_address = wait_for_target_address(psa.ip)

            log.debug("Listening for TouchOSC MIDI Bridge on {}:{}.".format(psa.ip, PORT))
            midibridge = liblo.ServerThread(PORT)
            osc_handler = OscHandler(midi_out, compliant=options.get('--compliant'))

            midibridge.add_method('/midi', 'm', osc_handler.on_midi)
            midibridge.add_method('/sysex', 's', osc_handler.on_midi)
            #midibridge.add_method('/key', 'si', osc_handler.on_key)

            log.debug("Listening for regular TouchOSC OSC messages on {}:{}.".format(psa.ip, OSCPORT))
            keybridge = liblo.ServerThread(OSCPORT)

            keybridge.add_method(None, None, osc_handler.dispatch)

            target = liblo.Address(target_address, PORT + 1, liblo.UDP)
            log.info("Will send to {}.".format(target.get_url()))

            midi_handler = MidiHandler(target, compliant=options.get('--compliant'))
            midi_in.callback = midi_handler.on_midi

            log.info("Listening for midi at {}.".format(midi_in))
            midibridge.start()
            keybridge.start()

            while True:
                time.sleep(.0001)
        except KeyboardInterrupt:
            psa.unregister()
            psa.close()

            if midibridge:
                midibridge.stop()
                midibridge.free()

            if keybridge:
                keybridge.stop()
                keybridge.free()

            midi_in.close()
            log.info("closed all ports")


if __name__ == '__main__':
    main()
