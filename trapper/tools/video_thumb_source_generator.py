# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image


def ffmpeg_frame(source, frame='00:00:01', **options):
    """
    Try to load a frame of the given video with ffmpeg, ignoring all errors.
    """
    data = Popen([
        'ffmpeg', '-i', source.file.name, '-an',
        '-vcodec', 'png', '-vframes', '1',
        '-ss', frame, '-y',
        '-f', 'rawvideo', '-'
    ], stdin=PIPE, stdout=PIPE, stderr=PIPE).communicate(source.read())[0]


    if not data:
        return

    image = Image.open(StringIO(data))
    image.load()

    return image
