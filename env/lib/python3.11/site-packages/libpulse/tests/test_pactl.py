"""Pactl test cases."""

import io
import re
import asyncio
import inspect
import logging
from contextlib import redirect_stdout
from unittest import IsolatedAsyncioTestCase

# Load the tests in the order they are declared.
from . import load_ordered_tests as load_tests
from . import requires_resources, is_pipewire, min_python_version
from ..pactl import main, parse_boolean, PactlSubCommands
from ..libpulse import PA_ENCODING_AC3_IEC61937

async def subcommand(result_name, cmd, *args, as_str=False):
    with redirect_stdout(io.StringIO()) as output:
        argv = ['pactl.py', cmd]
        argv.extend(args)
        await main(argv)

    if as_str:
        return output.getvalue()

    # Return the result as a Python object.
    d={}
    exec(output.getvalue(), globals(), d)
    if result_name is None:
        return d
    return d[result_name]

async def get_entity_from_name(entity, name):
    entities = entity + 's' if not entity.endswith('s') else entity
    items = await subcommand(entities, 'list', entities)
    for item in items:
        if item['name'] == name:
            return item

class NullSinkModule:
    def __init__(self, pactl_tests, sink_name):
        self.sink_name = sink_name

    async def close(self):
        await subcommand('result', 'unload-module', str(self.index))

    async def __aenter__(self):
        self.index = await subcommand('index', 'load-module',
                    'module-null-sink',
                    f'sink_name="{self.sink_name}"')
        try:
            sink = await get_entity_from_name('sink', self.sink_name)
            if sink is None:
                assert False, f"Cannot find sink named '{self.sink_name}'"
            return sink
        except Exception:
            await self.close()
            raise

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()

@requires_resources('libpulse')
class PactlTests(IsolatedAsyncioTestCase):
    def check_volume(self, result, int1, percent1, db1, int2, percent2, db2):
        expected = (
            f'Volume: front-left:  {int1} / {percent1}% / {db1} dB,'
            f'        front-right: {int2} / {percent2}% / {db2} dB')
        self.assertTrue(result.replace(' ', '').startswith(
                                                expected.replace(' ', '')))

    async def run_test_volume(self, type, name):
        # 'name' is either the name or the index.
        set = f'set-{type}-volume'
        get = f'get-{type}-volume'

        result = await subcommand('result', set, name, '1.0')
        self.assertEqual(result, 'PA_OPERATION_DONE')
        result = await subcommand('result', get, name, as_str=True)
        self.check_volume(result, '65536', '100', '0.00',
                                      '65536', '100', '0.00')

        # Additive Relative adjust.
        result = await subcommand('result', set, name, '+1')
        self.assertEqual(result, 'PA_OPERATION_DONE')
        result = await subcommand('result', get, name, as_str=True)
        self.check_volume(result, '65537', '100', '0.00',
                                      '65537', '100', '0.00')

        # Multiplicative Relative adjust.
        result = await subcommand('result', set, '--', name, '-10db')
        self.assertEqual(result, 'PA_OPERATION_DONE')
        result = await subcommand('result', get, name, as_str=True)
        self.check_volume(result, '44650', '68', '-10.00',
                                      '44650', '68', '-10.00')

        # Different values on each channel.
        result = await subcommand('result', set, name, '1.0', '0.5')
        self.assertEqual(result, 'PA_OPERATION_DONE')
        result = await subcommand('result', get, name, as_str=True)
        self.check_volume(result, '65536', '100', '0.00',
                                      '52016',  '79', '-6.02')

        # Restore defaults.
        result = await subcommand('result', set, name, '1.0')
        self.assertEqual(result, 'PA_OPERATION_DONE')

    async def run_test_mute(self, type, index):
        def bool_to_int(flag):
            return parse_boolean(str(flag).lower())

        get = f'get-{type}-mute'
        set = f'set-{type}-mute'

        # Get default.
        result = await subcommand('mute', get, index)
        self.assertTrue(isinstance(result, bool))
        mute_default = result

        # Set to not default.
        result = await subcommand('result', set, index,
                        str(bool_to_int(not mute_default)))
        self.assertEqual(result, 'PA_OPERATION_DONE')

        # Toggle and restore default.
        result = await subcommand('result', set, index, 'toggle')
        self.assertEqual(result, 'PA_OPERATION_DONE')
        result = await subcommand('mute', get, index)
        self.assertEqual(result, mute_default)

    async def run_sink_input_test(self, test_function):
        name = '440 Hz Sine'
        async with NullSinkModule(self, 'foo') as sink:
            result = await subcommand('result', 'set-default-sink',
                                                        str(sink['index']))
            self.assertEqual(result, 'PA_OPERATION_DONE')

            sine_index = None
            try:
                sine_index = await subcommand('index', 'load-module',
                                                                'module-sine')
                sink_inputs = await subcommand('sink_inputs', 'list',
                                                                'sink-inputs')
                for sink_input in sink_inputs:
                    if sink_input['name'] == name:
                        index = str(sink_input['index'])
                        break
                else:
                    assert False, f"'{name}' sink-input not found as a source"
                await test_function(index)
            finally:
                await subcommand('result', 'unload-module', str(sine_index))

    async def test_stat(self):
        pa_stat_info = await subcommand('pa_stat_info', 'stat')
        keys = ['memblock_total', 'scache_size', 'memblock_allocated']
        self.assertTrue(set(keys).issubset(pa_stat_info))

    async def test_info(self):
        pa_server_info = await subcommand('pa_server_info', 'info')
        keys = ['default_sink_name', 'channel_map', 'server_name']
        self.assertTrue(set(keys).issubset(pa_server_info))

    async def test_list_modules(self):
        modules = await subcommand('modules', 'list', 'modules')
        self.assertTrue(isinstance(modules, list))
        keys = ['index', 'name', 'auto_unload']
        for module in modules:
            self.assertTrue(set(keys).issubset(module))

    async def test_list_clients(self):
        clients = await subcommand('clients', 'list', 'clients')
        self.assertTrue(isinstance(clients, list))
        names = []
        keys = ['index', 'name', 'owner_module']
        for client in clients:
            self.assertTrue(set(keys).issubset(client))
            names.append(client['name'])
        self.assertIn('pactl.py', names)

    async def test_list_cards(self):
        cards = await subcommand('cards', 'list', 'cards')
        self.assertTrue(isinstance(cards, list))
        keys = ['index', 'name', 'owner_module', 'driver', 'n_profiles',
                'profiles', 'active_profile', 'proplist', 'n_ports', 'ports',
                'profiles2', 'active_profile2']
        for card in cards:
            self.assertTrue(set(keys).issubset(card))

    async def test_list_all(self):
        all = await subcommand(None, 'list')
        keys = ['modules', 'sinks', 'sources', 'sink_inputs',
                'source_outputs', 'clients', 'samples', 'cards']
        self.assertTrue(set(keys).issubset(all.keys()))

    async def test_list_message_handlers(self):
        message_handlers = await subcommand('message_handlers', 'list',
                                                        'message-handlers')
        self.assertTrue(isinstance(message_handlers, list))
        if is_pipewire():
           self.assertTrue(re.search(r'[Pp]ipe[Ww]ire', message_handlers[1]))
        else:
            self.assertIn('Core message handler', message_handlers[1])

    @requires_resources('pulseaudio')
    async def test_load_module(self):
        with self.assertRaises(SystemExit) as cm:
            await subcommand('index', 'load-module',
                                        'this is an unknown module name')
        e = cm.exception
        self.assertTrue(re.search(r'Module initialization failed', e.args[0]))

    async def test_unload_by_index(self):
        index = await subcommand('index', 'load-module',
                                                    'module-null-sink')
        self.assertTrue(isinstance(index, int))

        result = await subcommand('result', 'unload-module', str(index))
        self.assertEqual(result, 'PA_OPERATION_DONE')

    async def test_unload_by_name(self):
        # Check that no module exists with this name.
        name = 'module-null-sink'
        modules = await subcommand('modules', 'list', 'modules')
        for module in modules:
            if module['name'] == name:
                self.skipTest(f"At least one module named '{name}' exists")

        await subcommand('index', 'load-module', name)
        result = await subcommand('result', 'unload-module', name)
        self.assertEqual(result, 'PA_OPERATION_DONE')

    async def test_operation_null_pointer(self):
        with self.assertRaises(SystemExit) as cm:
            # type of 'idx' argument of pa_context_move_sink_input_by_name()
            # is uint32_t, and the PA_INVALID_INDEX definition is
            # ((uint32_t) -1). The function returns NULL in that case.
            await subcommand(None, 'move-sink-input', '-1', 'foo')
        e = cm.exception
        self.assertTrue(re.search(r'NULL .pa_operation. pointer'
                                  r': Invalid argument', e.args[0]))

    async def test_unknown_argument(self):
        with self.assertRaises(SystemExit) as cm:
            await subcommand(None, 'move-source-output', '0',
                                                        'invalid_source_name')
        e = cm.exception
        self.assertTrue(re.search(r'Failure: No such entity', e.args[0]))

    @requires_resources('pulseaudio')
    async def test_move_sink_input(self):
        async def move_sink_input(index):
            async with NullSinkModule(self, 'bar') as sink:
                result = await subcommand('result', 'move-sink-input',
                                                    index, str(sink['index']))
                self.assertEqual(result, 'PA_OPERATION_DONE')

        await self.run_sink_input_test(move_sink_input)

    async def test_suspend_sink(self):
        name = 'foo'
        async with NullSinkModule(self, name):
            result = await subcommand('result', 'suspend-sink', name,
                                                                    'true')
            self.assertEqual(result, 'PA_OPERATION_DONE')
            result = await subcommand('result', 'suspend-sink', name,
                                                                    'false')
            self.assertEqual(result, 'PA_OPERATION_DONE')

    @requires_resources('pulseaudio')
    async def test_suspend_source(self):
        index = None
        name = 'sine_input'
        try:
            index = await subcommand('index', 'load-module',
                                                        'module-sine-source')
            result = await subcommand('result', 'suspend-source', name,
                                                                    'true')
            self.assertEqual(result, 'PA_OPERATION_DONE')
            result = await subcommand('result', 'suspend-source', name,
                                                                    'false')
            self.assertEqual(result, 'PA_OPERATION_DONE')
        finally:
            await subcommand('result', 'unload-module', str(index))

    @requires_resources('pulseaudio')
    async def test_default_sink(self):
        name = 'foo'
        async with NullSinkModule(self, name) as sink:
            result = await subcommand('result', 'set-default-sink',
                                                        str(sink['index']))
            self.assertEqual(result, 'PA_OPERATION_DONE')
            default_sink_name = await subcommand('default_sink_name',
                                                        'get-default-sink')
            self.assertEqual(default_sink_name, name)

    @requires_resources('pulseaudio')
    async def test_default_source(self):
        name = 'foo'
        monitor = f'{name}.monitor'
        async with NullSinkModule(self, name):
            sources = await subcommand('sources', 'list', 'sources')
            for source in sources:
                if source['name'] == monitor:
                    index = str(source['index'])
                    break
            else:
                assert False, f"'{monitor}' sink monitor not found as a source"
            result = await subcommand('result', 'set-default-source', index)
            self.assertEqual(result, 'PA_OPERATION_DONE')
            default_source_name = await subcommand('default_source_name',
                                                        'get-default-source')
            self.assertEqual(default_source_name, monitor)

    async def test_sink_volume(self):
        async with NullSinkModule(self, 'foo') as sink:
            await self.run_test_volume('sink', str(sink['index']))

    async def test_source_volume(self):
        name = 'foo'
        monitor = f'{name}.monitor'
        async with NullSinkModule(self, name):
            await self.run_test_volume('source', monitor)

    @requires_resources('pulseaudio')
    async def test_sink_input_volume(self):
        async def set_volume(index):
            # Multiplicative Relative adjust.
            result = await subcommand('result', 'set-sink-input-volume',
                                                        '--', index, '-10db')
            self.assertEqual(result, 'PA_OPERATION_DONE')

        await self.run_sink_input_test(set_volume)

    async def test_sink_mute(self):
        async with NullSinkModule(self, 'foo') as sink:
            index = str(sink['index'])
            await self.run_test_mute('sink', index)

    async def test_source_mute(self):
        name = 'foo'
        monitor = f'{name}.monitor'
        async with NullSinkModule(self, name):
            sources = await subcommand('sources', 'list', 'sources')
            for source in sources:
                if source['name'] == monitor:
                    index = str(source['index'])
                    break
            else:
                assert False, f"'{monitor}' sink monitor not found as a source"
            await self.run_test_mute('source', index)

    @requires_resources('pulseaudio')
    async def test_sink_input_mute(self):
        async def set_mute(index):
            result = await subcommand('result', 'set-sink-input-mute',
                                                                index, '0')
            self.assertEqual(result, 'PA_OPERATION_DONE')

        await self.run_sink_input_test(set_mute)

    @requires_resources('pulseaudio')
    async def test_sink_formats(self):
        name = 'foo'
        format_rate = '[32000, 44100, 48000]'
        async with NullSinkModule(self, name) as sink:
            index = str(sink['index'])
            result = await subcommand('result', 'set-sink-formats', index,
                            f'ac3-iec61937, format.rate = "{format_rate}"')
            self.assertEqual(result, 'PA_OPERATION_DONE')

            sink = await get_entity_from_name('sink', sink['name'])
            self.assertEqual(sink['formats'][0]['encoding'],
                                                PA_ENCODING_AC3_IEC61937)
            self.assertEqual(sink['formats'][0]['plist']['format.rate'],
                                                                format_rate)

            # Restore default.
            result = await subcommand('result', 'set-sink-formats', index,
                                                                        'pcm')
            self.assertEqual(result, 'PA_OPERATION_DONE')

    async def test_send_message(self):
        response = await subcommand('response', 'send-message', '/core',
                                                            'list-handlers')
        for resp in response:
            if resp['name'] == '/core':
                if is_pipewire():
                    self.assertTrue(re.search(r'[Pp]ipe[Ww]ire',
                                                    resp['description']))
                else:
                    self.assertEqual(resp['description'],
                                                    'Core message handler')
                break
        else:
            assert False, '/core not found in response'

    @min_python_version((3, 11))
    async def test_subscribe(self):
        async def unload_by_index():
            await asyncio.sleep(0.5)
            await main(['pactl.py', 'unload-module', str(index)])

        eof = "Event 'remove' on module"
        async with asyncio.timeout(1):
            index = await subcommand('index', 'load-module',
                                                    'module-null-sink')
            asyncio.create_task(unload_by_index())
            result = await subcommand('result', 'subscribe', eof, as_str=True)
        self.assertTrue(eof in result)

    async def test_help(self):
        result = await subcommand('result', 'help', as_str=True)

    async def test_help_commands(self):
        # Avoid noisy asyncio warning:
        # Executing <Task finished ... coro=<PactlTests.test_help_commands()
        # ...  took 0.375 seconds.
        # Actually the warning is useless as this task releases control to the
        # asyncio event loop whenever it awaits the subcommand() coro.
        logging.getLogger('asyncio').setLevel(logging.ERROR)

        d = dict(inspect.getmembers(PactlSubCommands, inspect.isfunction))
        for command in d:
            if not command.startswith('cmd_'):
                continue
            cmd = command[4:].replace('_', '-')
            result = await subcommand('result', 'help', cmd, as_str=True)
