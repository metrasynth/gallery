# WT1: Empty WaveTabulator sunsynth templates

This is a collection of "boring" (empty) WaveTabulator sunsynths for SunVox.

They act as mixers between a matrix of sound generators that you provide yourself.

The simplest is WT1-2, which is one dimension, two sound generators.
When you fade the value from 0 to 16384, it mixes from the first to the second generator.
When you fade the value from 16384 to 32768, it mixes back to the first.

The one-dimension templates go up to 16 slots.

The last slot always wraps around to the first.
This is to allow you to drive the dimensional selectors using a sawtooth LFO
to get seamless morphing between all sounds.

Some multi-dimensional configurations are available: 
2x2 (4 slots), 3x3x3 (27 slots), and 3x4x5 (60 slots).
You'll need to dig into more layers of MetaModules to fill in all the sound generators.

## About WaveTabulator

This is the original description for WaveTabulator,
straight from the [source code](https://github.com/metrasynth/gallery/blob/master/wavetabulator.mmckpy):

I am WaveTabulator, an n-dimensional (*) wavetable-inspired synthesizer constructor.

You select the number of dimensions, the size of the dimension (**), and a random seed.

I create a SunVox MetaModule that lets you address and mix synths along each dimension.

I can give you sound generators that create (mostly) tuned sounds based on gently randomized synths.

If you want, though, I be boring, and can just leave everything blank, for you to fill in yourself.

Regardless, you can replace the contents of these with anything you like!

I CAN BE CPU HEAVY! Remember that all synths are active regardless of being selected at a given time.

Demo videos:

- https://youtu.be/-UMQzHOZEzA

Module key:

    note in     Incoming notes are sent here
    D #.#...    Dimension #.#
    S #.#.#     Synth #.#.#
    V #         Value for position #
    F #         Value filter for position #
    smooth #    Value smoother for position #
    A #         Amplifier for position #
    D sel #     Position selector for dimension #
    S sel       Synth selector

(*) where n is [1..5]

(**) where the dimension size is [2..16]
