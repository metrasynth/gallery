from __future__ import annotations

from ctypes import POINTER, c_uint32, c_int16, c_float, Structure, c_ubyte, c_ushort

import js

# noinspection PyUnresolvedReferences
from js import console, svlib

# noinspection PyUnresolvedReferences
from js import (
    sv_init,
    sv_deinit,
    sv_get_sample_rate,
    sv_update_input,
    sv_audio_callback,
    sv_audio_callback2,
    sv_open_slot,
    sv_close_slot,
    sv_lock_slot,
    sv_unlock_slot,
    sv_load_from_memory,
    sv_play,
    sv_play_from_beginning,
    sv_stop,
    sv_pause,
    sv_resume,
    sv_sync_resume,
    sv_set_autostop,
    sv_get_autostop,
    sv_end_of_song,
    sv_rewind,
    sv_volume,
    sv_set_event_t,
    sv_send_event,
    sv_get_current_line,
    sv_get_current_line2,
    sv_get_current_signal_level,
    sv_get_song_name,
    sv_get_song_bpm,
    sv_get_song_tpl,
    sv_get_song_length_frames,
    sv_get_song_length_lines,
    sv_get_time_map,
    sv_new_module,
    sv_remove_module,
    sv_connect_module,
    sv_disconnect_module,
    sv_load_module_from_memory,
    sv_sampler_load_from_memory,
    sv_get_number_of_modules,
    sv_find_module,
    sv_get_module_flags,
    sv_get_module_inputs,
    sv_get_module_outputs,
    sv_get_module_name,
    sv_get_module_xy,
    sv_get_module_color,
    sv_get_module_finetune,
    sv_get_module_scope2,
    sv_module_curve,
    sv_get_number_of_module_ctls,
    sv_get_module_ctl_name,
    sv_get_module_ctl_value,
    sv_get_number_of_patterns,
    sv_find_pattern,
    sv_get_pattern_x,
    sv_get_pattern_y,
    sv_get_pattern_tracks,
    sv_get_pattern_lines,
    sv_get_pattern_name,
    sv_get_pattern_data,
    sv_set_pattern_event,
    sv_get_pattern_event,
    sv_pattern_mute,
    sv_get_ticks,
    sv_get_ticks_per_second,
    sv_get_log,
)


class sunvox_note(Structure):
    _fields_ = [
        # NN: 0 - nothing; 1..127 - note num; 128 - note off; 129, 130...
        # - see NOTECMD enum
        ("note", c_ubyte),
        # VV: Velocity 1..129; 0 - default
        ("vel", c_ubyte),
        # MM: 0 - nothing; 1..65535 - module number + 1
        ("module", c_ushort),
        # 0xCCEE: CC: 1..127 - controller number + 1; EE - effect
        ("ctl", c_ushort),
        # 0xXXYY: value of controller or effect
        ("ctl_val", c_ushort),
    ]


class SunVoxApi:

    # Initialization of SunVox WASM
    # =============================

    @classmethod
    async def init_sunvox(cls):
        module = await svlib
        return cls.init_svlib(module)

    @staticmethod
    def init_svlib(module) -> SunVoxApi:
        js.svlib = module
        return SunVoxApi

    # SunVox API wrapper
    # ==================

    @staticmethod
    def init(
        config: str | None,
        freq: int,
        channels: int,
        flags: int,
    ) -> int:
        """
        global sound system init

        Parameters:
          config -
            string with additional configuration in the following format:
              "option_name=value|option_name=value";
            example: "buffer=1024|audiodriver=alsa|audiodevice=hw:0,0";
            use null if you agree to the automatic configuration;
          freq -
            desired sample rate (Hz); min - 44100;
            the actual rate may be different, if INIT_FLAG.USER_AUDIO_CALLBACK is not set;
          channels - only 2 supported now;
          flags - mix of the INIT_FLAG.xxx flags.
        """
        return sv_init(config, freq, channels, flags)

    @staticmethod
    def deinit() -> int:
        """
        global sound system deinit
        """
        return sv_deinit()

    @staticmethod
    def get_sample_rate() -> int:
        """
        Get current sampling rate (it may differ from the frequency specified in sv_init())
        """
        return sv_get_sample_rate()

    @staticmethod
    def update_input() -> int:
        """
        handle input ON/OFF requests to enable/disable input ports of the sound card
        (for example, after the Input module creation).

        Call it from the main thread only, where the SunVox sound stream is not locked.
        """
        return sv_update_input()

    @staticmethod
    def audio_callback(
        buf: bytes,
        frames: int,
        latency: int,
        out_time: int,
    ) -> int:
        """
        get the next piece of SunVox audio from the Output module.

        With audio_callback() you can ignore the built-in SunVox sound output mechanism
        and use some other sound system.

        INIT_FLAG.USER_AUDIO_CALLBACK flag in sv_init() mus be set.

        Parameters:
          buf -
            destination buffer of type int16_t (if INIT_FLAG.AUDIO_INT16 used in init())
              or float (if INIT_FLAG.AUDIO_FLOAT32 used in init());
            stereo data will be interleaved in this buffer: LRLR... ;
            where the LR is the one frame (Left+Right channels);
          frames - number of frames in destination buffer;
          latency - audio latency (in frames);
          out_time - buffer output time (in system ticks, SunVox time space);

        Return values: 0 - silence (buffer filled with zeroes); 1 - some signal.

        Example 1 (simplified, without accurate time sync) - suitable for most cases:
          sv_audio_callback( buf, frames, 0, sv_get_ticks() );

        Example 2 (accurate time sync) - when you need to maintain exact time intervals
                                         between incoming events (notes, commands, etc.):
          user_out_time = ... ; //output time in user time space
                                //(depends on your own implementation)
          user_cur_time = ... ; //current time in user time space
          user_ticks_per_second = ... ; //ticks per second in user time space
          user_latency = user_out_time - user_cur_time; //latency in user time space
          uint32_t sunvox_latency =
            ( user_latency * sv_get_ticks_per_second() ) / user_ticks_per_second;
            //latency in SunVox time space
          uint32_t latency_frames =
            ( user_latency * sample_rate_Hz ) / user_ticks_per_second;
            //latency in frames
          sv_audio_callback( buf, frames, latency_frames, sv_get_ticks() + sunvox_latency );
        """
        return sv_audio_callback(buf, frames, latency, out_time)

    @staticmethod
    def audio_callback2(
        buf: bytes,
        frames: int,
        latency: int,
        out_time: int,
        in_type: int,
        in_channels: int,
        in_buf: bytes,
    ) -> int:
        """
        send some data to the Input module and receive the filtered data from the Output
        module.

        It's the same as sv_audio_callback() but you also can specify the input buffer.

        Parameters:
          ...
          in_type - input buffer type:
            0 - int16_t (16bit integer);
            1 - float (32bit floating point);
          in_channels - number of input channels;
          in_buf -
            input buffer;
            stereo data must be interleaved in this buffer: LRLR... ;
            where the LR is the one frame (Left+Right channels);
        """
        return sv_audio_callback2(
            buf,
            frames,
            latency,
            out_time,
            in_type,
            in_channels,
            in_buf,
        )

    @staticmethod
    def open_slot(slot: int) -> int:
        """
        open sound slot for SunVox.

        You can use several slots simultaneously (each slot with its own SunVox engine).

        Use lock/unlock when you simultaneously read and modify SunVox data from different
        threads (for the same slot);

        example:
          thread 1: sv_lock_slot(0); sv_get_module_flags(0,mod1); sv_unlock_slot(0);
          thread 2: sv_lock_slot(0); sv_remove_module(0,mod2); sv_unlock_slot(0);

        Some functions (marked as "USE LOCK/UNLOCK") can't work without lock/unlock at all.
        """
        return sv_open_slot(slot)

    @staticmethod
    def close_slot(
        slot: int,
    ) -> int:
        """
        close sound slot for SunVox.

        You can use several slots simultaneously (each slot with its own SunVox engine).

        Use lock/unlock when you simultaneously read and modify SunVox data from different
        threads (for the same slot);

        example:
          thread 1: sv_lock_slot(0); sv_get_module_flags(0,mod1); sv_unlock_slot(0);
          thread 2: sv_lock_slot(0); sv_remove_module(0,mod2); sv_unlock_slot(0);

        Some functions (marked as "USE LOCK/UNLOCK") can't work without lock/unlock at all.
        """
        return sv_close_slot(slot)

    @staticmethod
    def lock_slot(
        slot: int,
    ) -> int:
        """
        lock sound slot for SunVox.

        You can use several slots simultaneously (each slot with its own SunVox engine).

        Use lock/unlock when you simultaneously read and modify SunVox data from different
        threads (for the same slot);

        example:
          thread 1: sv_lock_slot(0); sv_get_module_flags(0,mod1); sv_unlock_slot(0);
          thread 2: sv_lock_slot(0); sv_remove_module(0,mod2); sv_unlock_slot(0);

        Some functions (marked as "USE LOCK/UNLOCK") can't work without lock/unlock at all.
        """
        return sv_lock_slot(slot)

    @staticmethod
    def unlock_slot(
        slot: int,
    ) -> int:
        """
        unlock sound slot for SunVox.

        You can use several slots simultaneously (each slot with its own SunVox engine).

        Use lock/unlock when you simultaneously read and modify SunVox data from different
        threads (for the same slot);

        example:
          thread 1: sv_lock_slot(0); sv_get_module_flags(0,mod1); sv_unlock_slot(0);
          thread 2: sv_lock_slot(0); sv_remove_module(0,mod2); sv_unlock_slot(0);

        Some functions (marked as "USE LOCK/UNLOCK") can't work without lock/unlock at all.
        """
        return sv_unlock_slot(slot)

    @staticmethod
    def load_from_memory(
        slot: int,
        data: bytes,
        data_size: int,
    ) -> int:
        """
        load SunVox project from the memory block.
        """
        return sv_load_from_memory(slot, data, data_size)

    @staticmethod
    def play(
        slot: int,
    ) -> int:
        """
        play from the current position
        """
        return sv_play(slot)

    @staticmethod
    def play_from_beginning(
        slot: int,
    ) -> int:
        """
        play from the beginning (line 0)
        """
        return sv_play_from_beginning(slot)

    @staticmethod
    def stop(
        slot: int,
    ) -> int:
        """
        first call - stop playing;
        second call - reset all SunVox activity and switch the engine to standby mode.
        """
        return sv_stop(slot)

    @staticmethod
    def pause(
        slot: int,
    ) -> int:
        """
        pause the audio stream on the specified slot
        """
        return sv_pause(slot)

    @staticmethod
    def resume(
        slot: int,
    ) -> int:
        """
        resume the audio stream on the specified slot
        """
        return sv_resume(slot)

    @staticmethod
    def sync_resume(
        slot: int,
    ) -> int:
        """
        wait for sync (pattern effect 0x33 on any slot)
        and resume the audio stream on the specified slot
        """
        return sv_sync_resume(slot)

    @staticmethod
    def set_autostop(
        slot: int,
        autostop: int,
    ) -> int:
        """
        autostop values:
          0 - disable autostop;
          1 - enable autostop.

        When disabled, song is playing infinitely in the loop.
        """
        return sv_set_autostop(slot, autostop)

    @staticmethod
    def get_autostop(
        slot: int,
    ) -> int:
        """
        autostop values:
          0 - disable autostop;
          1 - enable autostop.

        When disabled, song is playing infinitely in the loop.
        """
        return sv_get_autostop(slot)

    @staticmethod
    def end_of_song(
        slot: int,
    ) -> int:
        """
        return values:
          0 - song is playing now;
          1 - stopped.
        """
        return sv_end_of_song(slot)

    @staticmethod
    def rewind(
        slot: int,
        line_num: int,
    ) -> int:
        return sv_rewind(slot, line_num)

    @staticmethod
    def volume(
        slot: int,
        vol: int,
    ) -> int:
        """
        set volume from 0 (min) to 256 (max 100%);

        negative values are ignored;

        return value: previous volume;
        """
        return sv_volume(slot, vol)

    @staticmethod
    def set_event_t(
        slot: int,
        set: int,
        t: int,
    ) -> int:
        """
        set the time of events to be sent by sv_send_event()

        Parameters:
          slot;
          set:
            1 - set;
            0 - reset (use automatic time setting - the default mode);
          t: the time when the events occurred (in system ticks, SunVox time space).

        Examples:
          sv_set_event_t( slot, 1, 0 )
            //not specified - further events will be processed as quickly as possible
          sv_set_event_t( slot, 1, sv_get_ticks() )
            //time when the events will be processed = NOW + sound latancy * 2
        """
        return sv_set_event_t(slot, set, t)

    @staticmethod
    def send_event(
        slot: int,
        track_num: int,
        note: int,
        vel: int,
        module: int,
        ctl: int,
        ctl_val: int,
    ) -> int:
        """
        send an event (note ON, note OFF, controller change, etc.)

        Parameters:
          slot;
          track_num - track number within the pattern;
          note:
            0 - nothing;
            1..127 - note num;
            128 - note off;
            129, 130... - see NOTECMD.xxx enums;
          vel: velocity 1..129; 0 - default;
          module: 0 (empty) or module number + 1 (1..65535);
          ctl: 0xCCEE. CC - number of a controller (1..255). EE - effect;
          ctl_val: value of controller or effect.
        """
        return sv_send_event(slot, track_num, note, vel, module, ctl, ctl_val)

    @staticmethod
    def get_current_line(slot: int) -> int:
        """
        Get current line number
        """
        return sv_get_current_line(slot)

    @staticmethod
    def get_current_line2(slot: int) -> int:
        """
        Get current line number in fixed point format 27.5
        """
        return sv_get_current_line2(slot)

    @staticmethod
    def get_current_signal_level(slot: int, channel: int) -> int:
        """
        From 0 to 255
        """
        return sv_get_current_signal_level(slot, channel)

    @staticmethod
    def get_song_name(slot: int) -> str:
        return sv_get_song_name(slot)

    @staticmethod
    def get_song_bpm(slot: int) -> int:
        return sv_get_song_bpm(slot)

    @staticmethod
    def get_song_tpl(slot: int) -> int:
        return sv_get_song_tpl(slot)

    @staticmethod
    def get_song_length_frames(slot: int) -> int:
        """
        Get the project length in frames.

        Frame is one discrete of the sound. Sample rate 44100 Hz means, that you hear 44100
        frames per second.
        """
        return sv_get_song_length_frames(slot)

    @staticmethod
    def get_song_length_lines(slot: int) -> int:
        """
        Get the project length in lines.
        """
        return sv_get_song_length_lines(slot)

    @staticmethod
    def get_time_map(
        slot: int,
        start_line: int,
        len: int,
        dest: POINTER(c_uint32),
        flags: int,
    ) -> int:
        """
        Parameters:
          slot;
          start_line - first line to read (usually 0);
          len - number of lines to read;
          dest -
            pointer to the buffer
            (size = len*sizeof(uint32_t)) for storing the map values;
          flags:
            TIME_MAP.SPEED: dest[X] = BPM | ( TPL << 16 )
              (speed at the beginning of line X);
            TIME_MAP.FRAMECNT: dest[X] = frame counter at the beginning of line X;

        Return value: 0 if successful, or negative value in case of some error.
        """
        return sv_get_time_map(slot, start_line, len, dest, flags)

    @staticmethod
    def new_module(
        slot: int,
        type: str,
        name: str,
        x: int,
        y: int,
        z: int,
    ) -> int:
        """
        Create a new module.
        """
        return sv_new_module(slot, type, name, x, y, z)

    @staticmethod
    def remove_module(
        slot: int,
        mod_num: int,
    ) -> int:
        """
        Remove selected module.
        """
        return sv_remove_module(slot, mod_num)

    @staticmethod
    def connect_module(
        slot: int,
        source: int,
        destination: int,
    ) -> int:
        """
        Connect the source to the destination.
        """
        return sv_connect_module(slot, source, destination)

    @staticmethod
    def disconnect_module(
        slot: int,
        source: int,
        destination: int,
    ) -> int:
        """
        Disconnect the source from the destination.
        """
        return sv_disconnect_module(slot, source, destination)

    @staticmethod
    def load_module_from_memory(
        slot: int,
        data: bytes,
        data_size: int,
        x: int,
        y: int,
        z: int,
    ) -> int:
        """
        load a module or sample from the memory block
        """
        return sv_load_module_from_memory(slot, data, data_size, x, y, z)

    @staticmethod
    def sampler_load_from_memory(
        slot: int,
        sampler_module: int,
        data: bytes,
        data_size: int,
        sample_slot: int,
    ) -> int:
        """
        load a sample to already created Sampler;
        to replace the whole sampler - set sample_slot to -1;
        """
        return sv_sampler_load_from_memory(
            slot,
            sampler_module,
            data,
            data_size,
            sample_slot,
        )

    @staticmethod
    def get_number_of_modules(slot: int) -> int:
        """
        get the number of module slots (not the actual number of modules).
        The slot can be empty or it can contain a module.
        Here is the code to determine that the module slot X is not empty:
        ( sv_get_module_flags( slot, X ) & SV_MODULE_FLAG_EXISTS ) != 0;
        """
        return sv_get_number_of_modules(slot)

    @staticmethod
    def find_module(
        slot: int,
        name: str,
    ) -> int:
        """
        find a module by name;

        return value: module number or -1 (if not found);
        """
        return sv_find_module(slot, name)

    @staticmethod
    def get_module_flags(
        slot: int,
        mod_num: int,
    ) -> int:
        """
        sunvox.types.MODULE.FLAG_xxx
        """
        return sv_get_module_flags(slot, mod_num)

    @staticmethod
    def get_module_inputs(
        slot: int,
        mod_num: int,
    ) -> int:
        """
        get pointers to the int[] arrays with the input links.
        Number of input links = ( module_flags & MODULE.INPUTS_MASK ) >> MODULE.INPUTS_OFF
        (this is not the actual number of connections: some links may be empty (value = -1))
        """
        return sv_get_module_inputs(slot, mod_num)

    @staticmethod
    def get_module_outputs(
        slot: int,
        mod_num: int,
    ) -> int:
        """
        get pointers to the int[] arrays with the output links.
        Number of output links =
        ( module_flags & MODULE.OUTPUTS_MASK ) >> MODULE.OUTPUTS_OFF
        (this is not the actual number of connections: some links may be empty (value = -1))
        """
        return sv_get_module_outputs(slot, mod_num)

    @staticmethod
    def get_module_name(
        slot: int,
        mod_num: int,
    ) -> str:
        return sv_get_module_name(slot, mod_num)

    @staticmethod
    def get_module_xy(
        slot: int,
        mod_num: int,
    ) -> int:
        """
        get module XY coordinates packed in a single uint32 value:

        ( x & 0xFFFF ) | ( ( y & 0xFFFF ) << 16 )

        Normal working area: 0x0 ... 1024x1024
        Center: 512x512

        Use GET_MODULE_XY() macro to unpack X and Y.
        """
        return sv_get_module_xy(slot, mod_num)

    @staticmethod
    def get_module_color(
        slot: int,
        mod_num: int,
    ) -> int:
        """
        get module color in the following format: 0xBBGGRR
        """
        return sv_get_module_color(slot, mod_num)

    @staticmethod
    def get_module_finetune(
        slot: int,
        mod_num: int,
    ) -> int:
        """
        get the relative note and finetune of the module;

        return value: ( finetune & 0xFFFF ) | ( ( relative_note & 0xFFFF ) << 16 ).

        Use GET_MODULE_FINETUNE() macro to unpack finetune and relative_note.
        """
        return sv_get_module_finetune(slot, mod_num)

    @staticmethod
    def get_module_scope2(
        slot: int,
        mod_num: int,
        channel: int,
        dest_buf: POINTER(c_int16),
        samples_to_read: int,
    ) -> int:
        """
        return value = received number of samples (may be less or equal to samples_to_read).

        Example:
          int16_t buf[ 1024 ];
          int received = sv_get_module_scope2( slot, mod_num, 0, buf, 1024 );
          //buf[ 0 ] = value of the first sample (-32768...32767);
          //buf[ 1 ] = value of the second sample;
          //...
          //buf[ received - 1 ] = value of the last received sample;
        """
        return sv_get_module_scope2(slot, mod_num, channel, dest_buf, samples_to_read)

    @staticmethod
    def module_curve(
        slot: int,
        mod_num: int,
        curve_num: int,
        data: POINTER(c_float),
        len: int,
        w: int,
    ) -> int:
        """
        access to the curve values of the specified module

        Parameters:
          slot;
          mod_num - module number;
          curve_num - curve number;
          data - destination or source buffer;
          len - number of items to read/write;
          w - read (0) or write (1).

        return value: number of items processed successfully.

        Available curves (Y=CURVE[X]):
          MultiSynth:
            0 - X = note (0..127); Y = velocity (0..1); 128 items;
            1 - X = velocity (0..256); Y = velocity (0..1); 257 items;
          WaveShaper:
            0 - X = input (0..255); Y = output (0..1); 256 items;
          MultiCtl:
            0 - X = input (0..256); Y = output (0..1); 257 items;
          Analog Generator, Generator:
            0 - X = drawn waveform sample number (0..31); Y = volume (-1..1); 32 items;
        """
        return sv_module_curve(slot, mod_num, curve_num, data, len, w)

    @staticmethod
    def get_number_of_module_ctls(
        slot: int,
        mod_num: int,
    ) -> int:
        return sv_get_number_of_module_ctls(slot, mod_num)

    @staticmethod
    def get_module_ctl_name(
        slot: int,
        mod_num: int,
        ctl_num: int,
    ) -> str:
        return sv_get_module_ctl_name(slot, mod_num, ctl_num)

    @staticmethod
    def get_module_ctl_value(
        slot: int,
        mod_num: int,
        ctl_num: int,
        scaled: int,
    ) -> int:
        return sv_get_module_ctl_value(slot, mod_num, ctl_num, scaled)

    @staticmethod
    def get_number_of_patterns(
        slot: int,
    ) -> int:
        """
        get the number of pattern slots (not the actual number of patterns).
        The slot can be empty or it can contain a pattern.
        Here is the code to determine that the pattern slot X is not empty:
        sv_get_pattern_lines( slot, X ) > 0;
        """
        return sv_get_number_of_patterns(slot)

    @staticmethod
    def find_pattern(
        slot: int,
        name: str,
    ) -> int:
        """
        find a pattern by name;

        return value: pattern number or -1 (if not found);
        """
        return sv_find_pattern(slot, name)

    @staticmethod
    def get_pattern_x(
        slot: int,
        pat_num: int,
    ) -> int:
        """
        get pattern information

        x - time (line number)
        """
        return sv_get_pattern_x(slot, pat_num)

    @staticmethod
    def get_pattern_y(
        slot: int,
        pat_num: int,
    ) -> int:
        """
        get pattern information

        y - vertical position on timeline;
        """
        return sv_get_pattern_y(slot, pat_num)

    @staticmethod
    def get_pattern_tracks(
        slot: int,
        pat_num: int,
    ) -> int:
        """
        get pattern information

        tracks - number of pattern tracks;
        """
        return sv_get_pattern_tracks(slot, pat_num)

    @staticmethod
    def get_pattern_lines(
        slot: int,
        pat_num: int,
    ) -> int:
        """
        get pattern information

        lines - number of pattern lines;
        """
        return sv_get_pattern_lines(slot, pat_num)

    @staticmethod
    def get_pattern_name(
        slot: int,
        pat_num: int,
    ) -> str:
        """
        get pattern information

        name - pattern name or NULL;
        """
        return sv_get_pattern_name(slot, pat_num)

    @staticmethod
    def get_pattern_data(
        slot: int,
        pat_num: int,
    ) -> POINTER(sunvox_note):
        """
        get the pattern buffer (for reading and writing)

        containing notes (events) in the following order:
          line 0: note for track 0, note for track 1, ... note for track X;
          line 1: note for track 0, note for track 1, ... note for track X;
          ...
          line X: ...

        Example:
          int pat_tracks = sv_get_pattern_tracks( slot, pat_num ); //number of tracks
          sunvox_note* data = sv_get_pattern_data( slot, pat_num );
            //get the buffer with all the pattern events (notes)
          sunvox_note* n = &data[ line_number * pat_tracks + track_number ];
          ... and then do someting with note n ...
        """
        return sv_get_pattern_data(slot, pat_num)

    @staticmethod
    def set_pattern_event(
        slot: int,
        pat_num: int,
        track: int,
        line: int,
        nn: int,
        vv: int,
        mm: int,
        ccee: int,
        xxyy: int,
    ) -> int:
        """
        write the pattern event to the cell at the specified line and track
        nn,vv,mm,ccee,xxyy are the same as the fields of sunvox_note structure.
        Only non-negative values will be written to the pattern.
        Return value: 0 (sucess) or negative error code.
        """
        return sv_set_pattern_event(slot, pat_num, track, line, nn, vv, mm, ccee, xxyy)

    @staticmethod
    def get_pattern_event(
        slot: int,
        pat_num: int,
        track: int,
        line: int,
        column: int,
    ) -> int:
        """
        read a pattern event at the specified line and track
        column (field number):
           0 - note (NN);
           1 - velocity (VV);
           2 - module (MM);
           3 - controller number or effect (CCEE);
           4 - controller value or effect parameter (XXYY);
        Return value: value of the specified field or negative error code.
        """
        return sv_get_pattern_event(slot, pat_num, track, line, column)

    @staticmethod
    def pattern_mute(
        slot: int,
        pat_num: int,
        mute: int,
    ) -> int:
        """
        mute (1) / unmute (0) specified pattern;

        negative values are ignored;

        return value: previous state (1 - muted; 0 - unmuted) or -1 (error);
        """
        return sv_pattern_mute(slot, pat_num, mute)

    @staticmethod
    def get_ticks() -> int:
        """
        SunVox engine uses its own time space, measured in system ticks (don't confuse it
        with the project ticks);

        required when calculating the out_time parameter in the sv_audio_callback().

        Use sv_get_ticks() to get current tick counter (from 0 to 0xFFFFFFFF).
        """
        return sv_get_ticks()

    @staticmethod
    def get_ticks_per_second() -> int:
        """
        SunVox engine uses its own time space, measured in system ticks (don't confuse it
        with the project ticks);

        required when calculating the out_time parameter in the sv_audio_callback().

        Use sv_get_ticks_per_second() to get the number of SunVox ticks per second.
        """
        return sv_get_ticks_per_second()

    @staticmethod
    def get_log(
        size: int,
    ) -> str:
        """
        get the latest messages from the log

        Parameters:
          size - max number of bytes to read.

        Return value: pointer to the null-terminated string with the latest log messages.
        """
        return sv_get_log(size)
