This is a collection of alternative scales for SunVox.

They allow you to use standard MIDI notes to play these scales
on any SunVox synth, thanks to features introduced in SunVox 1.9.3
along with its general microtonal features. 

Please note that these scales are large, and contain hundreds of
MetaModules. As such, just having one of these scales loaded
can use a **significant amount of CPU**!

## Using the scales

1. Load the scale of your choice into your project's modules.
2. Connect it to the instrument you want to play.
3. Send notes to the scale module.
4. If using Glide, send notes from the scale to Glide, not the other way around.

## Compatibility

You cannot use the touch theremin in conjunction with these modules.

## How they're built

The grunt work is done by the "Ultrasonic Scaler", a tool built using the
MetaModule Construction Kit included in Metrasynth Solar Sails.

Scale information is fed into Ultrasonic, which generates the SunVox
modules needed to implement the scale.

You can find the ``ultrasonic.mmckpy`` source code in this directory.

## Future improvement ideas

Instead of using MetaModules to play notes using SP, 
can we translate SP values into transpose and finetune?

If that lets us achieve the same thing, without using MetaModules,
that could give us significant CPU savings.
