import requests

from src.Config import script_dir, env

def unload(url: str, folder=""):
    url = url.removeprefix("/")
    if ".." in url.split("/"): return
    if folder in url.split("/"):
        url = url.removeprefix(folder)

    with open(script_dir + f'/data/{url.split("/")[-1]}', "wb") as f:
        f.write(requests.get(f'{env("URL")}/{folder}/{url}', auth=(env("LOGIN"), env("PASSWORD"))).content)