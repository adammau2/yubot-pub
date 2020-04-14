# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.
#
# Port to UserBot by @MoveAngel

from datetime import datetime
#from covid import Covid
from covid.api import CovId19Data
from userbot import CMD_HELP
from userbot.events import register

@register(outgoing=True, pattern="^.covid (.*)")
async def corona(event):
    await event.edit("`Processing...`")
    country = event.pattern_match.group(1)
    province = event.pattern_match.group(1)
    #covid = Covid()
    covid = CovId19Data(force=True)
    #country_data = covid.get_status_by_country_name(country)
    country_data = covid.get_history_by_province(province)
    if country_data:
        output_text =  f"`Confirmed   : {country_data['Confirmed']}`\n"
        output_text += f"`Active      : {country_data['Active']}`\n"
        output_text += f"`Deaths      : {country_data['Deaths']}`\n"
        output_text += f"`Recovered   : {country_data['Recovered']}`\n"
        output_text += (
            "`Last update : "
            f"{datetime.utcfromtimestamp(country_data['Last_Update'] // 1000).strftime('%Y-%m-%d %H:%M:%S')}`\n"
        )
        output_text += f"Data provided by [Johns Hopkins University](https://j.mp/2xf6oxF)"
    else:
        output_text = "No information yet about this country!"
    await event.edit(f"Corona Virus Info in {province}:\n\n{output_text}")


CMD_HELP.update({
        "covid": 
        ".covid <country>"
        "\nUsage: Get an information about data covid-19 in your country.\n"
    })
