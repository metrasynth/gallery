from scipy.io import wavfile


def load_wav_to_sampler_slot(path, sampler, slot, **kwargs):
    sample = sampler.Sample()
    freq, snd = wavfile.read(str(path))
    if snd.dtype.name == 'int16':
        sample.format = sampler.Format.int16
    elif snd.dtype.name == 'float32':
        sample.format = sampler.Format.float32
    else:
        raise Exception('Not supported')
    if len(snd.shape) == 1:
        size, = snd.shape
        channels = 1
    else:
        size, channels = snd.shape
    sample.rate = freq
    sample.channels = {
        1: m.Sampler.Channels.mono,
        2: m.Sampler.Channels.stereo,
    }[channels]
    sample.data = snd.data.tobytes()
    for key, value in kwargs.items():
        setattr(sample, key, value)
    sampler.samples[slot] = sample
    return sample
