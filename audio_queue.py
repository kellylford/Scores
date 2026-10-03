"""Plays pitch sounds off the UI thread, one at a time, in order.

winsound.Beep and PlaySound (without SND_ASYNC) block until the sound ends:
0.2 to 0.75 seconds a pitch, during which the window ignored the keyboard,
and a chained pitch sequence held it for several seconds. SND_ASYNC alone
isn't enough, because each new sound cuts off the one playing. A single
worker thread keeps sounds in order and never overlapping, the way they
played before, without holding up the UI.
"""

from concurrent.futures import ThreadPoolExecutor

_player = ThreadPoolExecutor(max_workers=1, thread_name_prefix="pitch-audio")


def play_in_background(fn, *args):
    """Queue fn(*args) to run after any sound already queued."""
    _player.submit(fn, *args)
