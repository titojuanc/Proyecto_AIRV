"""The special names @DEFAULT_SINK@, @DEFAULT_SOURCE@ and @DEFAULT_MONITOR@
can be used to specify the default sink, source and monitor.

The output of most subcommands can be parsed by Python: run the exec()
Python built-in on the output, or redirect the output to a file and import the
file as a Python module. For example start an interactive Python session and
inspect the 'cards' object with:

    $ ./pactl.py list cards > cards.py && python -i cards.py
"""

import sys
import os
import argparse
import inspect
import asyncio
import ctypes as ct
from textwrap import dedent, wrap
from itertools import chain

from libpulse.libpulse import (
    LibPulse, LibPulseError, LibPulseInstanceExistsError, PulseStructure,
    struct_ctypes, Pa_cvolume, Pa_channel_map, LibPulseOperationError,
    PA_VOLUME_NORM, PA_VOLUME_MUTED, PA_VOLUME_IS_VALID, PA_INVALID_INDEX,
    PA_DEVICE_TYPE_SINK, PA_SUBSCRIPTION_MASK_ALL, PA_CHANNELS_MAX,
    PA_OPERATION_DONE,

    # Non-async functions.
    pa_cvolume_snprint_verbose, pa_cvolume_get_balance, pa_cvolume_set,
    pa_sw_cvolume_multiply, pa_sw_volume_from_linear, pa_sw_volume_from_dB,
    pa_format_info_from_string, pa_format_info_free, pa_strerror,
    pa_context_errno,
    )

__VERSION__ = '0.1'
PGM = os.path.basename(sys.argv[0].rstrip(os.sep))

PA_CVOLUME_SNPRINT_VERBOSE_MAX = 1984   # Defined in volume.h.
PA_MAX_FORMATS = 256                    # Defined in internal.h.
VOL_UINT     = 0
VOL_PERCENT  = 1
VOL_LINEAR   = 2
VOL_DECIBEL  = 3
VOL_ABSOLUTE = 0 << 4
VOL_RELATIVE = 1 << 4

VOLUME_DOC = """ VOLUME can be specified as an integer (e.g. 2000,
        16384), a linear factor (e.g. 0.4, 1.100), a percentage (e.g. 10%,
        100%) or a decibel value (e.g. 0dB, 20dB). If the volume specification
        start with a + or - the volume adjustment will be relative to the
        current sink volume. A single volume value affects all channels; if
        multiple volume values are given their number has to match the sink's
        number of channels.

        Note: The subcommand MUST be followed by '--' when entering a negative
        volume value (otherwise this will be understood as an invalid option).
        For example:
            'pactl.py set-sink-volume -- 0 -1db +1db'
"""

def print_volume(info):
    c_volume = Pa_cvolume(info.volume.channels, info.volume.values)
    c_channel_map = Pa_channel_map(info.channel_map.channels,
                                 info.channel_map.map)
    buff = ct.create_string_buffer(PA_CVOLUME_SNPRINT_VERBOSE_MAX)

    volume = pa_cvolume_snprint_verbose(buff,
                        PA_CVOLUME_SNPRINT_VERBOSE_MAX,
                        c_volume.byref(), c_channel_map.byref(), 1)
    balance = pa_cvolume_get_balance(
        c_volume.byref(), c_channel_map.byref())

    print(f'Volume: {volume.decode()}\n'
          f'        balance {balance:.2f}')

def volume_relative_adjust(cv, c_volume):
    sflag = c_volume.flags & 0x0f
    if sflag in (VOL_UINT, VOL_PERCENT):
        for i in range(cv.channels):
            add = cv.values[i] + c_volume.values[i]
            if add < PA_VOLUME_NORM:
                c_volume.values[i] = PA_VOLUME_MUTED
            else:
                c_volume.values[i] = add - PA_VOLUME_NORM
    if sflag in (VOL_LINEAR, VOL_DECIBEL):
        c_cv = Pa_cvolume(cv.channels, cv.values)
        pa_sw_cvolume_multiply(c_volume.byref(), c_cv.byref(),
                                                        c_volume.byref())

def fill_volume(info, c_volume):
    supported = info.channel_map.channels
    if c_volume.channels == 1:
        pa_cvolume_set(c_volume.byref(), supported, c_volume.values[0])
    elif c_volume.channels != supported:
        sys.exit(f'Failed to set volume: You tried to set c_volume for'
                 f' {c_volume.channels} channels, whereas channel(s) supported'
                 f' = {supported}')

    if c_volume.flags & VOL_RELATIVE:
        volume_relative_adjust(info.volume, c_volume)

class PactlSubCommands:
    """Provide the methods that implement the pactl commands.

    The 'upload-sample' command is not implemented (requires libsndfile).
    """

    def __init__(self, lib_pulse):
        self.lib_pulse = lib_pulse

    def exit_no_info(self, entity):
        error = pa_strerror(pa_context_errno(self.lib_pulse.c_context))
        sys.exit(f'Failed to get {entity} information: {error.decode()}')

    async def run(self, args):
        command = args.command
        command = command.replace('-', '_')
        method = getattr(self, command)
        try:
            await method(args)
        except LibPulseOperationError as e:
            sys.exit(e.args[0])

    async def cmd_stat(self, args):
        "Dump few statistics about memory usage of the PulseAudio daemon."
        lp = self.lib_pulse
        pa_stat_info = await lp.pa_context_stat()
        print(f'pa_stat_info = {pa_stat_info}')

    async def cmd_info(self, args):
        "Dump some info about the PulseAudio daemon."
        lp = self.lib_pulse
        pa_server_info = await lp.pa_context_get_server_info()
        print(f'pa_server_info = {pa_server_info}')

    async def cmd_list(self, args):
        """Dump all currently loaded modules, available sinks, sources, streams, etc.

        The argument must be set to: modules, sinks, sources, sink-inputs,
        source-outputs, clients, samples, cards, message-handlers. If not
        specified, all info is listed with the exception of the
        message-handlers.
        """
        lp = self.lib_pulse
        list_methods = {
            'modules': lp.pa_context_get_module_info_list,
            'sinks': lp.pa_context_get_sink_info_list,
            'sources': lp.pa_context_get_source_info_list,
            'sink-inputs': lp.pa_context_get_sink_input_info_list,
            'source-outputs': lp.pa_context_get_source_output_info_list,
            'clients': lp.pa_context_get_client_info_list,
            'samples': lp.pa_context_get_sample_info_list,
            'cards': lp.pa_context_get_card_info_list,
            'message-handlers': lp.pa_context_send_message_to_object,
            }

        if not args.type:
            for type, method in list_methods.items():
                if type == 'message-handlers':
                    continue
                type_list = await method()
                print(f"{type.replace('-', '_')} = {type_list}")
        else:
            assert args.type in list_methods
            if args.type == 'message-handlers':
                type_list = await list_methods[args.type]('/core',
                                                        'list-handlers', None)
            else:
                type_list = await list_methods[args.type]()
            print(f"{args.type.replace('-', '_')} = {type_list}")

    async def cmd_exit(self, args):
        "Ask the PulseAudio server to terminate."
        lp = self.lib_pulse
        await lp.pa_context_exit_daemon()
        print("result = 'PA_OPERATION_DONE'")

    async def cmd_play_sample(self, args):
        """Play the specified sample from the sample cache.

        It is played on the default sink, unless the symbolic name or the
        numerical index of the sink to play it on is specified.
        """
        lp = self.lib_pulse
        await lp.pa_context_play_sample(args.name,
                                                    args.sink, PA_VOLUME_NORM)
        print("result = 'PA_OPERATION_DONE'")

    async def cmd_remove_sample(self, args):
        """Remove the specified sample from the sample cache."""
        lp = self.lib_pulse
        await lp.pa_context_remove_sample(args.name)
        print("result = 'PA_OPERATION_DONE'")

    async def cmd_load_module(self, args):
        """Load a module with the specified arguments into the sound server.

        Prints the numeric index of the module just loaded. You can use it to
        unload the module later.
        """
        lp = self.lib_pulse
        index = await lp.pa_context_load_module(args.name, args.arguments)
        if index == PA_INVALID_INDEX:
            error = pa_strerror(pa_context_errno(lp.c_context))
            sys.exit(f'Failure: {error.decode()}')

        print(f'index = {index}')

    async def cmd_unload_module(self, args):
        """Unload module(s).

        Unload the module instance identified by the specified numeric index
        or unload all modules by the specified name.
        """
        lp = self.lib_pulse
        try:
            index = int(args.id_name)
        except ValueError:
            name = args.id_name
            count = 0
            for module in await lp.pa_context_get_module_info_list():
                if module.name == name:
                    await lp.pa_context_unload_module(module.index)
                    print("result = 'PA_OPERATION_DONE'")
                    count += 1
            if count:
                print("result = 'PA_OPERATION_DONE'")
            return
        await lp.pa_context_unload_module(index)
        print("result = 'PA_OPERATION_DONE'")

    async def cmd_move_sink_input(self, args):
        """Move the specified playback stream to the  specified sink.

        Move the specified playback stream (identified by its numerical index)
        to the specified sink (identified by its symbolic name or numerical
        index).
        """
        lp = self.lib_pulse
        await lp.pa_context_move_sink_input_by_name(args.idx, args.sink)
        print("result = 'PA_OPERATION_DONE'")

    async def cmd_move_source_output(self, args):
        lp = self.lib_pulse
        await lp.pa_context_move_source_output_by_name(args.idx, args.source)
        print("result = 'PA_OPERATION_DONE'")
    cmd_move_source_output.__doc__ = cmd_move_sink_input.__doc__.replace(
                        'sink', 'source').replace('playback', 'recording')

    async def cmd_suspend_sink(self, args):
        """Suspend or resume the specified sink.

        Suspend or resume the specified sink (which may be specified either by
        its symbolic name or numerical index), depending whether true
        (suspend) or false (resume) is passed as last argument. Suspending a
        sink will pause all playback. Depending on the module implementing the
        sink this might have the effect that the underlying device is closed,
        making it available for other applications to use. The exact behaviour
        depends on the module.
        """
        lp = self.lib_pulse
        if args.sink:
            await lp.pa_context_suspend_sink_by_name(args.sink, args.bool)
        else:
            await lp.pa_context_suspend_sink_by_index(
                                                PA_INVALID_INDEX, args.bool)
        print("result = 'PA_OPERATION_DONE'")

    async def cmd_suspend_source(self, args):
        lp = self.lib_pulse
        if args.source:
            await lp.pa_context_suspend_source_by_name(args.source, args.bool)
        else:
            await lp.pa_context_suspend_source_by_index(
                                                PA_INVALID_INDEX, args.bool)
        print("result = 'PA_OPERATION_DONE'")
    cmd_suspend_source.__doc__ = cmd_suspend_sink.__doc__.replace(
                        'sink', 'source').replace('playback', 'capturing')

    async def cmd_set_card_profile(self, args):
        """Set the specified card to  the specified profile.

        Set the specified card (identified by its symbolic name or numerical
        index) to the specified profile (identified by its symbolic name).
        """
        lp = self.lib_pulse
        await lp.pa_context_set_card_profile_by_name(args.card, args.profile)
        print("result = 'PA_OPERATION_DONE'")

    async def cmd_get_default_sink(self, args):
        """Returns the symbolic name of the default sink."""
        lp = self.lib_pulse
        pa_server_info = await lp.pa_context_get_server_info()
        default_sink_name = (f"'{pa_server_info.default_sink_name}'" if
                                                    pa_server_info else None)
        print(f"default_sink_name = {default_sink_name}")

    async def cmd_get_default_source(self, args):
        """Returns the symbolic name of the default source."""
        lp = self.lib_pulse
        pa_server_info = await lp.pa_context_get_server_info()
        default_source_name = (f"'{pa_server_info.default_source_name}'" if
                                                    pa_server_info else None)
        print(f"default_source_name = {default_source_name}")

    async def cmd_set_default_sink(self, args):
        """Make the specified sink the default sink.

        Make the specified sink (identified by its symbolic name or numerical
        index) the default sink. Use the special name @NONE@ to unset the user
        defined default sink. This will make pulseaudio return to the default
        sink selection based on sink priority.
        """
        lp = self.lib_pulse
        await lp.pa_context_set_default_sink(args.sink)
        print("result = 'PA_OPERATION_DONE'")

    async def cmd_set_default_source(self, args):
        lp = self.lib_pulse
        await lp.pa_context_set_default_source(args.source)
        print("result = 'PA_OPERATION_DONE'")
    cmd_set_default_source.__doc__ = cmd_set_default_sink.__doc__.replace(
                                                            'sink', 'source')

    async def cmd_set_sink_port(self, args):
        """Set the specified sink to the specified port.

        Set the specified sink (identified by its symbolic name or numerical
        index) to the specified port (identified by its symbolic name).
        """
        lp = self.lib_pulse
        await lp.pa_context_set_sink_port_by_name(args.sink, args.port)
        print("result = 'PA_OPERATION_DONE'")

    async def cmd_set_source_port(self, args):
        lp = self.lib_pulse
        await lp.pa_context_set_source_port_by_name(
                                                    args.source, args.port)
        print("result = 'PA_OPERATION_DONE'")
    cmd_set_source_port.__doc__ = cmd_set_sink_port.__doc__.replace('sink',
                                                                    'source')

    async def cmd_get_sink_volume(self, args):
        """Get the volume of the specified sink."""
        lp = self.lib_pulse
        sink = await lp.pa_context_get_sink_info_by_name(args.sink)
        if sink:
            print_volume(sink)
        else:
            self.exit_no_info('sink')

    async def cmd_get_source_volume(self, args):
        """Get the volume of the specified source."""
        lp = self.lib_pulse
        source = await lp.pa_context_get_source_info_by_name(args.source)
        if source:
            print_volume(source)
        else:
            self.exit_no_info('source')

    async def cmd_get_sink_mute(self, args):
        """Get the mute status of the specified sink."""
        lp = self.lib_pulse
        sink = await lp.pa_context_get_sink_info_by_name(args.sink)
        if sink:
            print(f"mute = {True if sink.mute else False}")
        else:
            self.exit_no_info('sink')

    async def cmd_get_source_mute(self, args):
        """Get the mute status of the specified source."""
        lp = self.lib_pulse
        source = await lp.pa_context_get_source_info_by_name(args.source)
        if source:
            print(f"mute = {True if source.mute else False}")
        else:
            self.exit_no_info('source')

    async def cmd_set_sink_volume(self, args):
        """Set the  volume  of the specified sink.

        Set the volume of the specified sink (identified by its symbolic name
        or numerical index)."""
        lp = self.lib_pulse
        c_volume = parse_volumes(args.volumes)
        sink = await lp.pa_context_get_sink_info_by_name(args.sink)
        if not sink:
            self.exit_no_info('sink')
        fill_volume(sink, c_volume)
        await lp.pa_context_set_sink_volume_by_name(
                                                args.sink, c_volume.byref())
        print("result = 'PA_OPERATION_DONE'")
    cmd_set_sink_volume.__doc__ += VOLUME_DOC

    async def cmd_set_source_volume(self, args):
        lp = self.lib_pulse
        c_volume = parse_volumes(args.volumes)
        source = await lp.pa_context_get_source_info_by_name(args.source)
        if not source:
            self.exit_no_info('source')
        fill_volume(source, c_volume)
        await lp.pa_context_set_source_volume_by_name(
                                                args.source, c_volume.byref())
        print("result = 'PA_OPERATION_DONE'")
    cmd_set_source_volume.__doc__ = cmd_set_sink_volume.__doc__.replace(
                                                            'sink', 'source')

    async def cmd_set_sink_input_volume(self, args):
        """Set  the volume of the specified sink input.

        Set  the volume of the specified sink input (identified by its
        numerical index).
        """
        lp = self.lib_pulse
        c_volume = parse_volumes(args.volumes)
        sink_input = await lp.pa_context_get_sink_input_info(args.idx)
        if not sink_input:
            self.exit_no_info('sink-input')
        fill_volume(sink_input, c_volume)
        await lp.pa_context_set_sink_input_volume(args.idx, c_volume.byref())
        print("result = 'PA_OPERATION_DONE'")
    cmd_set_sink_input_volume.__doc__ += VOLUME_DOC.replace('sink',
                                                            'sink-input')

    async def cmd_set_source_output_volume(self, args):
        """Set the volume of the specified source output.

        Set the volume of the specified source output (identified by its
        numerical index).
        """
        lp = self.lib_pulse
        c_volume = parse_volumes(args.volumes)
        source_output = await lp.pa_context_get_source_output_info(args.idx)
        if not source_output:
            self.exit_no_info('source-output')
        fill_volume(source_output, c_volume)
        await lp.pa_context_set_source_output_volume(
                                                args.idx, c_volume.byref())
        print("result = 'PA_OPERATION_DONE'")
    cmd_set_source_output_volume.__doc__ += VOLUME_DOC.replace('sink',
                                                            'source-output')

    async def cmd_set_sink_mute(self, args):
        """Set the mute status of the specified sink.

        Set the mute status of the specified sink (identified by its symbolic
        name or numerical index).
        """
        lp = self.lib_pulse
        if args.mute == 'toggle':
            sink = await lp.pa_context_get_sink_info_by_name(args.sink)
            mute = 0 if sink.mute else 1
            await lp.pa_context_set_sink_mute_by_name(args.sink, mute)
        else:
            await lp.pa_context_set_sink_mute_by_name(args.sink, args.mute)
        print("result = 'PA_OPERATION_DONE'")

    async def cmd_set_source_mute(self, args):
        """Set the mute status of the specified source.

        Set the mute status of the specified source (identified by its symbolic
        name or numerical index).
        """
        lp = self.lib_pulse
        if args.mute == 'toggle':
            source = await lp.pa_context_get_source_info_by_name(args.source)
            mute = 0 if source.mute else 1
            await lp.pa_context_set_source_mute_by_name(args.source, mute)
        else:
            await lp.pa_context_set_source_mute_by_name(args.source,
                                                                args.mute)
        print("result = 'PA_OPERATION_DONE'")

    async def cmd_set_sink_input_mute(self, args):
        """Set the mute status of the specified sink input.

        Set the mute status of the specified sink input (identified by its
        numerical index).
        """
        lp = self.lib_pulse
        if args.mute == 'toggle':
            sink_input = await lp.pa_context_get_sink_input_info(args.idx)
            mute = 0 if sink_input.mute else 1
            await lp.pa_context_set_sink_input_mute(args.idx, mute)
        else:
            await lp.pa_context_set_sink_input_mute(args.idx, args.mute)
        print("result = 'PA_OPERATION_DONE'")

    async def cmd_set_source_output_mute(self, args):
        """Set the mute status of the specified source output.

        Set the mute status of the specified source output (identified by its
        numerical index).
        """
        lp = self.lib_pulse
        if args.mute == 'toggle':
            src_output = await lp.pa_context_get_source_output_info(args.idx)
            mute = 0 if src_output.mute else 1
            await lp.pa_context_set_source_output_mute(args.idx, mute)
        else:
            await lp.pa_context_set_source_output_mute(args.idx, args.mute)
        print("result = 'PA_OPERATION_DONE'")

    async def cmd_set_sink_formats(self, args):
        """Set the supported formats of the specified sink.

        Set the supported formats of the specified sink (identified by its
        numerical  index) if supported by the sink. FORMATS is specified as a
        semi-colon (;) separated list of formats in the form 'encoding[,
        key1=value1, key2=value2, ...]' (for example, AC3 at 32000, 44100 and
        48000 Hz would be specified as 'ac3-iec61937, format.rate = "[32000,
        44100, 48000  ]"'). See
        https://www.freedesktop.org/wiki/Software/PulseAudio/Documentation/User/SupportedAudioFormats/
        for possible encodings.
        """
        c_format_pointers = []
        try:
            for format in args.formats.split(';'):
                f = pa_format_info_from_string(format.strip().encode())
                if not f:
                    sys.exit(
                    f"Failed to set format: invalid format string '{format}'")
                c_format_pointers.append(f)

            lp = self.lib_pulse
            PA_FORMAT_INFO_PTR = ct.POINTER(struct_ctypes['pa_format_info'])
            F_ARRAY = PA_FORMAT_INFO_PTR * PA_MAX_FORMATS
            await lp.pa_ext_device_restore_save_formats(
                                                PA_DEVICE_TYPE_SINK, args.idx,
                                                len(c_format_pointers),
                                                F_ARRAY(*c_format_pointers))
            print("result = 'PA_OPERATION_DONE'")
        finally:
            for f in c_format_pointers:
                pa_format_info_free(f)

    async def cmd_send_message(self, args):
        """Send  a message to the specified recipient object.

        If applicable an additional string containing message parameters can
        be specified. A string is returned as a response to the  message. For
        available messages see
        https://cgit.freedesktop.org/pulseaudio/pulseaudio/tree/doc/messaging_api.txt
        """
        lp = self.lib_pulse
        result, response = await lp.pa_context_send_message_to_object(
                                            args.rcv, args.msg, args.params)
        if result != PA_OPERATION_DONE:
            error = pa_strerror(pa_context_errno(lp.c_context))
            sys.exit(f'Failure: {error.decode()}')

        print(f'response = {response}')

    async def cmd_subscribe(self, args):
        """Subscribe to events.

        pactl does not exit by itself, but keeps waiting for new events.

        The optional EOF parameter allows for conditional exit, mostly for
        testing.
        """
        lp = self.lib_pulse

        # All events except autoload events.
        await lp.pa_context_subscribe(PA_SUBSCRIPTION_MASK_ALL)
        iterator = lp.get_events_iterator()
        async for event in iterator:
            event = f"Event '{event.type}' on {event.facility} #{event.index}"
            print(event)

            if args.eof is not None and event.startswith(args.eof):
                return

def dispatch_help(args):
    """Print help on a subcommand with 'pactl.py help SUBCOMMAND'."""

    command = args.subcommand
    if command is None:
        command = 'help'
    args.parsers[command].print_help()

    command = command.replace('-', '_')
    cmd_func = getattr(PactlSubCommands, 'cmd_%s' % command, None)
    if cmd_func:
        lines = cmd_func.__doc__.splitlines()
        print('\n%s\n' % lines[0])
        paragraph = []
        for l in dedent('\n'.join(lines[2:])).splitlines():
            if l == '':
                if paragraph:
                    print('\n'.join(wrap(' '.join(paragraph), width=80)))
                    print()
                    paragraph = []
                continue
            paragraph.append(l)
        if paragraph:
            print('\n'.join(wrap(' '.join(paragraph), width=80)))

def parse_volume(volume):
    flags = VOL_RELATIVE if volume.startswith(('+', '-')) else VOL_ABSOLUTE
    if volume.endswith('%'):
        flags |= VOL_PERCENT
        volume = volume[:-1]
    elif volume.endswith(('db', 'dB')):
        flags |= VOL_DECIBEL
        volume = volume[:-2]
    elif '.' in volume:
        flags |= VOL_LINEAR

    try:
        value = float(volume)
    except ValueError as e:
        sys.exit(f'{e!r}')

    sflag = flags & 0x0f
    if flags & VOL_RELATIVE:
        if sflag == VOL_UINT:
            value += PA_VOLUME_NORM
        elif sflag == VOL_PERCENT:
            value += 100.0
        elif sflag == VOL_LINEAR:
            value += 1.0

    if sflag == VOL_PERCENT:
        value = value * PA_VOLUME_NORM / 100
    elif sflag == VOL_LINEAR:
        value = pa_sw_volume_from_linear(value)
    elif sflag == VOL_DECIBEL:
        value = pa_sw_volume_from_dB(value)

    if not PA_VOLUME_IS_VALID(value):
        sys.exit('Volume outside permissible range')

    return value, flags

def parse_volumes(volumes):
    length = len(volumes)
    if length >= PA_CHANNELS_MAX:
        sys.exit('Invalid number of volume specifications')

    volume_flags = None
    values = []
    for volume in volumes:
        value, flags = parse_volume(volume)
        if volume_flags is None:
            volume_flags = flags
        elif flags != volume_flags:
            sys.exit('Inconsistent volume specification')
        values.append(int(value))
    c_volume = Pa_cvolume(length, values)
    c_volume.flags = volume_flags
    return c_volume

def parse_boolean(val):
    true = ('1', 'y', 't', 'yes', 'true', 'on')
    false = ('0', 'n', 'f', 'no', 'false', 'off')
    if val in chain(true, (v.upper() for v in true)):
        return 1
    elif val in chain(false, (v.upper() for v in false)):
        return 0
    else:
        raise argparse.ArgumentTypeError
def parse_mute(val):
    if val == 'toggle':
        return val
    return parse_boolean(val)

def to_bytes(val):
    if val is None:
        return None
    return val.encode()

def parse_args(argv):
    # Instantiate the main parser.
    usage= ('pactl.py --version | help | help SUBCOMMAND |'
            ' SUBCOMMAND [ARGS ...]')
    main_parser = argparse.ArgumentParser(prog=PGM, usage=usage,
                    formatter_class=argparse.RawDescriptionHelpFormatter,
                    description=__doc__, add_help=False)
    main_parser.add_argument('--version', '-v', action='version',
                    version='%(prog)s ' + __VERSION__)

    # The help subparser handles the help for each command and uses the
    # 'parsers' dict for that purpose.
    subparsers = main_parser.add_subparsers(title='subcommands',
                                            prog='pactl.py', required=True)
    parsers = { 'help': main_parser }
    parser = subparsers.add_parser('help', add_help=False,
                                   help=dispatch_help.__doc__)
    parser.add_argument('subcommand', choices=parsers, nargs='?',
                        default=None)
    parser.set_defaults(command='dispatch_help', parsers=parsers)

    # Add the subcommands subparsers.
    d = dict(inspect.getmembers(PactlSubCommands, inspect.isfunction))
    for command in sorted(d):
        if not command.startswith('cmd_'):
            continue
        cmd = command[4:]
        cmd = cmd.replace('_', '-')
        func = d[command]
        parser = subparsers.add_parser(cmd, help=func.__doc__.splitlines()[0],
                                       add_help=False)
        parser.set_defaults(command=command)
        parser.add_argument('--server', '-s',
                            help='name of the server to connect to')
        parser.add_argument('--client-name', '-n', metavar='NAME',
                            help='how to call this client on the server')

        if cmd == 'list':
            parser.add_argument('type', nargs='?',
                choices=['modules', 'sinks', 'sources', 'sink-inputs',
                         'source-outputs', 'clients', 'samples', 'cards',
                         'message-handlers'],  metavar='TYPE')
        if cmd in ('play-sample', 'remove-sample', 'load-module'):
            parser.add_argument('name', metavar='NAME')
        if cmd in ('move-sink-input', 'move-source-output',
                   'set-sink-input-volume', 'set-source-output-volume',
                   'set-sink-input-mute', 'set-source-output-mute',
                   'set-sink-formats'):
            parser.add_argument('idx', metavar='INDEX', type=int)
        if cmd in ('move-sink-input', 'suspend-sink', 'set-default-sink',
                   'set-sink-port', 'get-sink-volume', 'get-sink-mute',
                   'set-sink-volume', 'set-sink-mute'):
            parser.add_argument('sink', metavar='SINK')
        if cmd in ('move-source-output', 'suspend-source',
                   'set-default-source', 'set-source-port',
                   'get-source-volume', 'get-source-mute',
                   'set-source-volume', 'set-source-mute'):
            parser.add_argument('source', metavar='SOURCE')
        if cmd == 'set-card-profile':
            parser.add_argument('card', metavar='CARD')
        if cmd == 'send-message':
            parser.add_argument('rcv', type=to_bytes, metavar='RECIPIENT')
            parser.add_argument('msg', type=to_bytes, metavar='MESSAGE')
            parser.add_argument('params', type=to_bytes,
                                metavar='MESSAGE_PARAMETERS', nargs='?')
        if cmd == 'set-card-profile':
            parser.add_argument('profile', metavar='PROFILE')
        if cmd in ('set-sink-port', 'set-source-port'):
            parser.add_argument('port', metavar='PORT')
        if cmd == 'play-sample':
            parser.add_argument('sink', metavar='SINK', nargs='?')
        if cmd == 'load-module':
            parser.add_argument('arguments', metavar='ARGUMENTS', nargs='?')
        if cmd == 'unload-module':
            parser.add_argument('id_name', metavar='ID|NAME')
        if cmd == 'set-sink-formats':
            parser.add_argument('formats', metavar='FORMATS')
        if cmd in ('suspend-sink', 'suspend-source'):
            parser.add_argument('bool', type=parse_boolean,
                                                        metavar='true|false')
        if cmd in ('set-sink-mute', 'set-source-mute', 'set-sink-input-mute',
                   'set-source-output-mute'):
            parser.add_argument('mute', type=parse_mute,
                                                        metavar='1|0|toggle')
        if cmd in ('set-sink-volume', 'set-source-volume',
                   'set-sink-input-volume', 'set-source-output-volume'):
            parser.add_argument('volumes', metavar='VOLUME', nargs='+')
        if cmd in 'subscribe':
            parser.add_argument('eof', metavar='EOF', nargs='?')

        parsers[cmd] = parser

    return main_parser.parse_args(argv[1:])

async def main(argv=sys.argv):
    args = parse_args(argv)
    if args.command == 'dispatch_help':
        dispatch_help(args)
    else:
        name = args.client_name if args.client_name else 'pactl.py'
        server = args.server if args.server else None
        try:
            try:
                async with LibPulse(name, server=server, flags=0) as lib_pulse:
                    await PactlSubCommands(lib_pulse).run(args)
            except LibPulseInstanceExistsError:
                lib_pulse = await LibPulse.get_current_instance()
                await PactlSubCommands(lib_pulse).run(args)
        except LibPulseError as e:
            sys.exit(f'{e!r}')

def script_main():
    asyncio.run(main())

if __name__ == '__main__':
    asyncio.run(main())
