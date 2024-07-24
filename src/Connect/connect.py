import requests
from bs4 import BeautifulSoup

from src.Config import script_dir, env
from ast import literal_eval

def unload(url: str, folder="", write=True):
    url = url.removeprefix("/").replace("//", '/')
    if ".." in url.split("/"): return
    if folder in url.split("/"):
        url = url.removeprefix(folder)

    data = requests.get(f'{env("URL")}/{folder}/{url}', auth=(env("LOGIN"), env("PASSWORD"))).content
    if write:
        with open(script_dir + f'/data/{url.split("/")[-1]}', "wb") as f:
            f.write(data)
    else: return data


def getDirs(path: str) -> list[str]:
    HTMLdata = unload(url=path, write=False)
    soup = BeautifulSoup(HTMLdata, 'html.parser')
    return [qoute.text for qoute in soup.find_all('a')]


def getHWID(name: str):
    data = str(requests.get(f'{env("HWIDURL")}name={name}').content).replace('{', '').replace('}', '').replace('"', '').split(',')
    for i in data: 
        if "userId" in i: return i.split(':')[-1]
    return "Not found"