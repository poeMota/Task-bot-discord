import requests
from bs4 import BeautifulSoup

from src.Config import get_data_path, env, from_toml

def unload(url: str, folder="", write=True):
    url = url.removeprefix("/").replace("//", '/').replace(' ', "%C2%A0")
    if ".." in url.split("/"): return
    url = url.removeprefix(folder)

    data = ""
    if env("NEEDAUTH"):
        data = requests.get(f'{env("URL")}/{folder}/{url}', auth=(env("LOGIN"), env("PASSWORD"))).content
    else:
        data = requests.get(f'{env("URL")}/{folder}/{url}').content

    if write:
        with open(str(get_data_path()) + f'/{url.split("/")[-1]}', "wb") as f:
            f.write(data)
    else: return data


def isValidUrl(url: str, folder: str = ""):
    errors = ["404 Not Found"]
    data = str(unload(url, folder, False))
    for e in errors:
        if e in data:
            return False
    return True


def fileDates(url: str) -> dict[str: str]:
    data = unload(url, write=False)
    return {qoute.text: qoute.next_sibling.strip().split("  ")[0] for qoute in BeautifulSoup(data, "html.parser").find_all('a')}


def getDirs(path: str) -> list[str]:
    HTMLdata = unload(url=path, write=False)
    soup = BeautifulSoup(HTMLdata, 'html.parser')
    return [qoute.text for qoute in soup.find_all('a')]


def getUserid(name: str):
    data = str(requests.get(f'{from_toml("config", "userid_api_url")}name={name}').content).replace('{', '').replace('}', '').replace('"', '').split(',')
    for i in data:
        if "userId" in i: return i.split(':')[-1]
    return "Not found"

