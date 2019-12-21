---
title: Video(mp4) to audio (mp3) conversion tool
categories:
    - Tech
Tags:
    - python
    - tools
---

I had a bunch of video files of a lecture that I wanted to listen offline while doing errands or driving. They do play well in phones but I could not use them as is because of few reasons: 1) they take considerable storage space 2) does not play well in the background, so can't listen during  3) distracting while driving and so on. There are indeed some apps available in the App Store to extract the audio stream out of the mp4 videos. But I did want to download a third party app just for a rare use. Also those apps are usually heavy weight and comes with boat load of stuff that I probably will never use. So I looked out for a command line tool or a library that I can simply use inside a Python program. That way I can script the process and can have more control over how files are handled and named. I chose to give a try with [moviepy](https://pypi.org/project/moviepy/) library mainly because of its super simple interfaces.

I installed the moviepy packages inside a virtual environment since I didn't have any plans to use this package outside of this use case. Installing third party packages in a virtual environment makes it much easier and cleaner to handle the dependencies than installing in the user environment.

```text
$ python3 -m venv .venv

$ ls .venv
bin  include  lib  pyvenv.cfg
$ ls .venv/bin
activate  activate.fish  easy_install-3.6 pip3   python
activate.csh  easy_install  pip   pip3.6   python3

$ source .venv/bin/activate
(.venv) $ pip3 search moviepy
moviepy (1.0.1)                             - Video editing with Python
moviepy-wumii (0.2.3.6.1)                   - Video editing with Python
livingbio-moviepy (0.2.2.11.3)              - Video editing with Python
mediadecoder (0.1.5)                        - Moviepy based media decoding library
opensesame-plugin-media_player_mpy (0.1.6)  - Media player plugin for OpenSesame, based on MoviePy

(.venv) $ pip3 install moviepy
(.venv) $ pip3 list
Package        Version
-------------- ----------
certifi        2019.11.28
chardet        3.0.4
decorator      4.4.1
idna           2.8
imageio        2.6.1
imageio-ffmpeg 0.3.0
moviepy        1.0.1
numpy          1.17.4
Pillow         6.2.1
pip            19.3.1
proglog        0.1.9
requests       2.22.0
setuptools     28.8.0
tqdm           4.41.0
urllib3        1.25.7
```

Here is a sample code that extracts the audio from a mp4 file and saves it into mp3, using the moviepy library. You can find the app code here. **add the python app into its own folder with requirements.txt and link it here**

```python
import moviepy.editor as mp
import os.path as path

def extract_audio(source: str):
    """
    Extracts the audio from the given source video file
    and saves into a mp3 file, with same name
    """
    video = mp.VideoFileClip(source)
    target = path.splitext(source)[0] + ".mp3"
    video.audio.write_audiofile(target, bitrate="64k", write_logfile=True)
```

...Executing the python program

```text
(.venv) $ time  ./mp4_to_mp3.py -s 01@.mp4
MoviePy - Writing audio in 01@.mp3
MoviePy - Done.
./mp4_to_mp3.py -s 01@.mp4  19.16s user 0.56s system 115% cpu 17.031 total

(.venv) $ ls -1sSk 01*
14980 01@.mp4
 3328 01@.mp3
    8 01@.mp3.log
```

It worked great, although slightly slower than I expected. I checked out the [docs](http://zulko.github.io/moviepy/getting_started/quick_presentation.html) where it was given that it may not be optimal to use this if the sole requirement is simple conversions. This library also uses ffmpeg in the backend, so it is better to use that directly instead of through this library. I downloaded the [ffmpeg binary](https://evermeet.cx/ffmpeg/ffmpeg-96102-g26f4ee37f7.zip) and gave that a try. It was significantly faster than the moviepy library. The only downside is that I have to download a different binary if I switch the operating system, but I don't have such plans for now. So I ended up using just the ffmpeg binary.

```text
$ time ./ffmpeg2 -vn -i lectures/01@.mp4 lectures/01@.mp3
ffmpeg version N-96102-g26f4ee37f7-tessus  https://evermeet.cx/ffmpeg/  Copyright (c) 2000-2019 the FFmpeg developers
  built with Apple clang version 11.0.0 (clang-1100.0.33.16)
  configuration: --cc=/usr/bin/clang --prefix=/opt/ffmpeg --extra-version=tessus --enable-avisynth --enable-fontconfig --enable-gpl --enable-libaom --enable-libass --enable-libbluray --enable-libdav1d --enable-libfreetype --enable-libgsm --enable-libmodplug --enable-libmp3lame --enable-libmysofa --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libopenh264 --enable-libopenjpeg --enable-libopus --enable-librubberband --enable-libshine --enable-libsnappy --enable-libsoxr --enable-libspeex --enable-libtheora --enable-libtwolame --enable-libvidstab --enable-libvmaf --enable-libvo-amrwbenc --enable-libvorbis --enable-libvpx --enable-libwavpack --enable-libwebp --enable-libx264 --enable-libx265 --enable-libxavs --enable-libxvid --enable-libzimg --enable-libzmq --enable-libzvbi --enable-version3 --pkg-config-flags=--static --disable-ffplay
  libavutil      56. 36.101 / 56. 36.101
  libavcodec     58. 65.100 / 58. 65.100
  libavformat    58. 35.101 / 58. 35.101
  libavdevice    58.  9.101 / 58.  9.101
  libavfilter     7. 69.101 /  7. 69.101
  libswscale      5.  6.100 /  5.  6.100
  libswresample   3.  6.100 /  3.  6.100
  libpostproc    55.  6.100 / 55.  6.100
Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'lectures/01@.mp4':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2avc1mp41
    encoder         : Lavf57.71.100
  Duration: 00:05:51.71, start: 0.000000, bitrate: 348 kb/s
    Stream #0:0(eng): Video: h264 (Main) (avc1 / 0x31637661), yuv420p, 1280x720, 214 kb/s, 23.98 fps, 23.98 tbr, 24k tbn, 47.95 tbc (default)
    Metadata:
      handler_name    : VideoHandler
    Stream #0:1(eng): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, mono, fltp, 128 kb/s (default)
    Metadata:
      handler_name    : SoundHandler
File 'lectures/01@.mp3' already exists. Overwrite? [y/N] y
Stream mapping:
  Stream #0:1 -> #0:0 (aac (native) -> mp3 (libmp3lame))
Press [q] to stop, [?] for help
Output #0, mp3, to 'lectures/01@.mp3':
  Metadata:
    major_brand     : isom
    minor_version   : 512
    compatible_brands: isomiso2avc1mp41
    TSSE            : Lavf58.35.101
    Stream #0:0(eng): Audio: mp3 (libmp3lame), 44100 Hz, mono, fltp (default)
    Metadata:
      handler_name    : SoundHandler
      encoder         : Lavc58.65.100 libmp3lame
size=    2748kB time=00:05:51.68 bitrate=  64.0kbits/s speed=  27x
video:0kB audio:2748kB subtitle:0kB other streams:0kB global headers:0kB muxing overhead: 0.011728%
./ffmpeg2 -vn -i lectures/01@.mp4 lectures/01@.mp3  12.12s user 0.14s system 84% cpu 14.457 total
```
