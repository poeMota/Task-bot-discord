from os import listdir

from disnake import Embed
from src.Config import *


def get_projects():
    return list(json_read("projects").keys())


# DONT READ THIS FUCKING SHIT
# THIS IS HELL, KILL WITH FIRE
# TODO: rework this with recursive methods
def embed_from_dict(title: str, description: str, color: int, D: dict, showHidden: bool):
    embed = Embed(
        title=title,
        type="rich",
        description=description,
        color=color
    )

    for key in D:
        # Skip hidden items
        if "@" in key and not showHidden: continue

        value = ""
        if type(D[key]) is list or type(D[key]) is tuple:
            if len(D[key]) == 0: continue
            name = f"{key} ({len(D[key])}):"
            for i in D[key]:
                char = '╠︎'
                if i == D[key][-1]: char = '╚'
                value = f"{value}{char} {i}\n"

        elif type(D[key]) is dict:
            if len(D[key]) == 0: continue
            name = f"{key} ({len(D[key])}):"
            for k in D[key]:
                if type(D[key][k]) is list:
                    if not D[key][k]: continue
                    value = f"{value}**{k}** {list_to_text(D[key][k])}"
                else:
                    value = f"{value}- {k}: {D[key][k]}"

        elif type(D[key]) is str and D[key].strip() == "":
            continue

        else:
            name = key
            value = D[key]

        if type(value) is str and len(value) > 1024:
            value = value[:1021:] + "..."

        if not value:
            continue

        embed.add_field(
            name=name.replace("@", ""),
            value=value,
            inline=False
        )

    return embed

def list_to_text(l: list):
    text = f"**({len(l)}):**"
    for i in l:
        if type(i) is list:
            text = f"{text}\n - {list_to_text(i)}"
        else:
            text = f"{text}\n - {i}"
    return text

