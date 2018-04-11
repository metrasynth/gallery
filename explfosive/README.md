# ExpLFOsive for SunVox

ExpLFOsive is a set of exponential LFO MetaModules.

Choose anywhere from 2 to 16 LFOs, and you will have the power to construct a wide range of useful curves beyond the standard ones provided by SunVox.

## How to use it

Use it in place of a standard LFO set to generator mode.

Change the `all.*` controllers to affect all LFOs.

Change the `lfo_[0-15].*` controllers to affect individual LFOs in the series.

SunVox LFO rules still apply, so when you change the `waveform` or `set_phase` of an individual LFO, it will become out of sync with the rest of the LFOs.

As with a single LFO, resync all LFOs by sending any note to the ExpLFOsive module. This will cause them all to immediately set their phase to whatever value `set_phase` is currently at for each 

### As a traditional LFO

Use it to drive a Sound2Ctl module to create exponential curves for filter sweeps, velocity changes, or whatever your imagination likes.

Use it as the modulator signal (second input) to a Modulator module to create interesting amplification envelopes, or to create weird FM wobbles.

### As a sound source

Change controller `0B` (`all.frequency_unit`) to `2` ("Hz" mode).

Then, change controller `08` to set pitch.

If you want to manipulate it with notes, set up a Pitch2Ctl module, set its OUT controller to `8`, then connect it to the ExpLFOsive module.

## How it works

It is implemented as a series of LFOs whose phase and controller values are kept in sync.

Each LFO acts as a multiplier for the previous in the series.

The more LFOs there are in series, the stronger the exponentiation will be.
