from disnake import Embed
from src.Config import *


def get_projects():
    return list(json_read("projects").keys())


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
                value = f"{value}- {k}: {D[key][k]}"

        elif type(D[key]) is str and D[key].strip() == "":
            continue

        else:
            name = key
            value = D[key]
        
        if type(value) is str and len(value) > 1024:
            value = value[-1024:-1] + value[-1]

        embed.add_field(
            name=name.replace("@", ""),
            value=value,
            inline=False
        )

    return embed