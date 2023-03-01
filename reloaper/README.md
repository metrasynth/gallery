# Reloaper: The Reloading Looper for SunVox

What this app does:

- Watches a SunVox song file for changes.
- When a change is detected (not currently rendering):
  - Renders the audio for the song and writes to a WAV.
  - Renders the time map for the song and writes to a CSV.
- When a change is detected (currently rendering):
  - Enqueues a re-render to start after the current one finishes.
- When a song and time map are both rendered:
  - Replaces the current playback audio with the new render.
  - If the frames for the current loop region in the time map have changed:
    - Moves the playhead to the start frame of the current loop. 
- When starting playback:
  - If the loop region is unset, starts playing at line 0.
  - If the loop region is set, starts playing at the first frame of the loop beginning.
- During playback:
  - If the loop region is set, audio loops when the last frame of the last line is reached.
- Display:
  - Playback state.
  - Rendering state.
  - Current line is shown.
  - Current time position in song is shown.
- Initial state:
  - Not playing.
  - No loop region.
- User can perform these actions:
  - Adjust start + length of loop region, specified by line number.
  - Play audio
  - Stop audio
  - Pause audio
  - Quit
