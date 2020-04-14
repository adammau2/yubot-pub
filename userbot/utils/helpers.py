import asyncio
import datetime
import logging
import os
import os.path
import sys
import time
from typing import Tuple, Union

from heroku3 import from_key

from telethon import errors
from telethon.tl import types
from telethon.utils import get_display_name

from .client import UserBotClient
from .log_formatter import CEND, CUSR
from .events import NewMessage

async def is_ffmpeg_there():
    cmd = await asyncio.create_subprocess_shell(
        'ffmpeg -version',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await cmd.communicate()
    return True if cmd.returncode == 0 else False

class ProgressCallback():
    """Custom class to handle upload and download progress."""
    def __init__(self, event, start=None, filen='unamed'):
        self.event = event
        self.start = start or time.time()
        self.last_edit = None
        self.filen = filen
        self.upload_finished = False
        self.download_finished = False

    async def resolve_prog(self, current, total):
        """Calculate the necessary info and make a dict from it."""
        if not self.last_edit:
            self.last_edit = datetime.datetime.now(datetime.timezone.utc)
        now = time.time()
        elp = now - self.start
        speed = int(float(current) / elp)
        eta = await calc_eta(elp, speed, current, total)
        s0, s1, s2 = await format_speed(speed, ("byte", 1))
        c0, c1, c2 = await format_speed(current, ("byte", 1))
        t0, t1, t2 = await format_speed(total, ("byte", 1))
        percentage = round(current / total * 100, 2)
        return {
            'filen': self.filen, 'percentage': percentage,
            'eta': await _humanfriendly_seconds(eta),
            'elp': await _humanfriendly_seconds(elp),
            'current': f'{c0:.2f}{c1}{c2[0]}',
            'total': f'{t0:.2f}{t1}{t2[0]}',
            'speed': f'{s0:.2f}{s1}{s2[0]}/s'
        }

    async def up_progress(self, current, total):
        """Handle the upload progress only."""
        d = await self.resolve_prog(current, total)
        edit, finished = ul_progress(d, self.event)
        if finished:
            if not self.upload_finished:
                self.event = await self.event.answer(edit)
                self.upload_finished = True
        elif edit:
            self.event = await self.event.answer(edit)

    async def dl_progress(self, current, total):
        """Handle the download progress only."""
        d = await self.resolve_prog(current, total)
        edit, finished = dl_progress(d, self.event)
        if finished:
            if not self.download_finished:
                self.event = await self.event.answer(edit)
                self.download_finished = True
        elif edit:
            self.event = await self.event.answer(edit)