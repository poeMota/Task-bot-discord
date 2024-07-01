import json
import toml
import os
import io
import sys

from dotenv import load_dotenv


script_dir = os.path.dirname(sys.argv[0])


# region JSON
def json_read(file):
    with io.open(script_dir + f"/data/{file}.json", "r", encoding="utf8") as json_file:
        json_data = json.load(json_file)
    return json_data


def from_json(file, tag):
    json_data = json_read(file)
    return json_data[tag]


def json_write(file, content):
    with io.open(script_dir + f"/data/{file}.json", "w", encoding="utf8") as json_file:
        json.dump(content, json_file, indent=2)
# endregion


# region TOML
def toml_read(file):
    with io.open(script_dir + f"/data/{file}.toml", "r", encoding="utf8") as toml_file:
        toml_data = toml.load(toml_file)
    return toml_data


def from_toml(file, tag):
    toml_data = toml_read(file)
    return toml_data[tag]


def toml_write(file, content):
    with io.open(script_dir + f"/data/{file}.toml", "w", encoding="utf8") as toml_file:
        toml.dump(content, toml_file)
# endregion


def env(key):
    load_dotenv(dotenv_path=script_dir + "/data/.env")
    return os.getenv(key)


def get_data_path():
    return script_dir + '/data/'