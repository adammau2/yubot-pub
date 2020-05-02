# Copyright (C) 2020 Adek Maulana.
# All rights reserved.
""" - a main for fallback userbot - """
import os
import asyncio
import requests
import math

from operator import itemgetter

from userbot import (
    heroku, mainn,
    HEROKU_APP_NAME_FALLBACK, HEROKU_API_KEY, HEROKU_API_KEY_FALLBACK,
    CMD_HELP
)
from userbot.events import register


heroku_api = "https://api.heroku.com"
useragent = (
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/81.0.4044.117 Mobile Safari/537.36'
)


@register(outgoing=True,
          pattern=(
              "^.dynofall "
              "(on|restart|off|cancel deploy|cancel build"
              "|get log)(?: (.*)|$)")
          )
async def dyno_manage(dyno):
    """ - Restart/Kill dyno - """
    await dyno.edit("`Sending information...`")
    app = heroku.app(HEROKU_APP_NAME_FALLBACK)
    exe = dyno.pattern_match.group(1)
    if exe == "on":
        try:
            Dyno = app.dynos()[0]
        except IndexError:
            app.scale_formation_process("worker", 1)
            text = f"`Starting` ⬢**{HEROKU_APP_NAME_FALLBACK}**"
            sleep = 1
            dot = "."
            await dyno.edit(text)
            while (sleep <= 24):
                await dyno.edit(text + f"`{dot}`")
                await asyncio.sleep(1)
                if len(dot) == 3:
                    dot = "."
                else:
                    dot += "."
                sleep += 1
            state = Dyno.state
            if state == "up":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME_FALLBACK}** `up...`")
            elif state == "crashed":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME_FALLBACK}** `crashed...`")
            return await dyno.delete()
        else:
            return await dyno.edit(f"⬢**{HEROKU_APP_NAME_FALLBACK}** `already on...`")
    if exe == "restart":
        try:
            """ - Catch error if dyno not on - """
            Dyno = app.dynos()[0]
        except IndexError:
            return await dyno.respond(f"⬢**{HEROKU_APP_NAME_FALLBACK}** `is not on...`")
        else:
            text = f"`Restarting` ⬢**{HEROKU_APP_NAME_FALLBACK}**"
            Dyno.restart()
            sleep = 1
            dot = "."
            await dyno.edit(text)
            while (sleep <= 24):
                await dyno.edit(text + f"`{dot}`")
                await asyncio.sleep(1)
                if len(dot) == 3:
                    dot = "."
                else:
                    dot += "."
                sleep += 1
            state = Dyno.state
            if state == "up":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME_FALLBACK}** `restarted...`")
            elif state == "crashed":
                await dyno.respond(f"⬢**{HEROKU_APP_NAME_FALLBACK}** `crashed...`")
            return await dyno.delete()
    elif exe == "off":
        """ - Complete shutdown - """
        app.scale_formation_process("worker", 0)
        text = f"`Shutdown` ⬢**{HEROKU_APP_NAME_FALLBACK}**"
        sleep = 1
        dot = "."
        while (sleep <= 3):
            await dyno.edit(text + f"`{dot}`")
            await asyncio.sleep(1)
            dot += "."
            sleep += 1
        await dyno.respond(f"⬢**{HEROKU_APP_NAME_FALLBACK}** `turned off...`")
        return await dyno.delete()
    elif exe == "cancel deploy" or exe == "cancel build":
        """ - Only cancel 1 recent builds from activity - """
        build_id = dyno.pattern_match.group(2)
        if build_id is None:
            build = app.builds(order_by='created_at', sort='desc')[0]
        else:
            build = app.builds().get(build_id)
            if build is None:
                return await dyno.edit(
                    f"`There is no such build.id`:  **{build_id}**")
        if build.status != "pending":
            return await dyno.edit("`Zero active builds to cancel...`")
        headers = {
            'User-Agent': useragent,
            'Authorization': f'Bearer {HEROKU_API_KEY_FALLBACK}',
            'Accept': 'application/vnd.heroku+json; version=3.cancel-build',
        }
        path = "/apps/" + build_app + "/builds/" + build_id
        r = requests.delete(heroku_api + path, headers=headers)
        text = f"`Stopping build`  **{build_id}**"
        await dyno.edit(text)
        sleep = 1
        dot = "."
        await asyncio.sleep(2)
        while (sleep <= 3):
            await dyno.edit(text + f"`{dot}`")
            await asyncio.sleep(1)
            dot += "."
            sleep += 1
        await dyno.respond(
            "`[HEROKU - FALLBACK]`\n"
            f"Build: ⬢**{build_app_name}**  `Stopped...`")
        """ - Restart main if builds cancelled - """
        try:
            app.dynos()[0].restart()
        except IndexError:
            await dyno.edit("`Your dyno fallback app is not on...`")
            await asyncio.sleep(2.5)
        return await dyno.delete()
    elif exe == "get log":
        await dyno.edit("`Getting information...`")
        with open('logs.txt', 'w') as log:
            log.write(app.get_log())
        await dyno.client.send_file(
            dyno.chat_id,
            "logs.txt",
            reply_to=dyno.id,
            caption="`Fallback dyno logs...`",
        )
        await dyno.edit("`Information gets and sent back...`")
        await asyncio.sleep(5)
        await dyno.delete()
        return os.remove('logs.txt')

CMD_HELP.update({
    "fallback":
    ">`.dynofall on`"
    "\nUsage: Turn on your fallback dyno application."
    "\n\n>`.dynofall restart`"
    "\nUsage: Restart your fallback dyno application."
    "\n\n>`.dynofall off`"
    "\nUsage: Shutdown fallback dyno completly."
    "\n\n>`.dynofall cancel deploy` or >`.dynofall cancel build`"
    "\nUsage: Cancel deploy from fallback app "
    "give build.id to specify build to cancel."
    "\n\n>`.dynofall get log`"
    "\nUsage: Get your fallback dyno recent logs."
})