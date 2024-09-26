import json
import toml
import yaml
import os
import io
import sys

from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))


# region JSON
def json_read(file):
    try:
        with io.open(get_data_path() + f"{file}.json", "r", encoding="utf8") as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        with io.open(get_data_path() + f"{file}.json", "w", encoding="utf8") as json_file:
            return {}


def from_json(file, tag):
    json_data = json_read(file)
    if tag in json_data:
        return json_data[tag]
    return None


def json_write(file, content):
    with io.open(get_data_path() + f"{file}.json", "w", encoding="utf8") as json_file:
        json.dump(content, json_file, indent=2)
# endregion


# region TOML
def toml_read(file):
    try:
        with io.open(get_data_path() + f"{file}.toml", "r", encoding="utf8") as toml_file:
            return toml.load(toml_file)
    except FileNotFoundError:
        with io.open(get_data_path() + f"{file}.toml", "w", encoding="utf8") as toml_file:
            return {}


def from_toml(file, tag):
    toml_data = toml_read(file)
    if tag in toml_data:
        return toml_data[tag]
    return None


def toml_write(file, content):
    with io.open(get_data_path() + f"{file}.toml", "w", encoding="utf8") as toml_file:
        toml.dump(content, toml_file)
# endregion


# region YAML
def yaml_read(file):
    try:
        with io.open(get_data_path() + f"{file}.yml", "r", encoding="utf8") as yaml_file:
            return yaml.load(yaml_file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        with io.open(get_data_path() + f"{file}.yml", "w", encoding="utf8") as yaml_file:
            return {}


def from_yaml(file, tag):
    yaml_data = yaml_read(file)
    if tag in yaml_data:
        return yaml_data[tag]
    return None


def yaml_write(file, content):
    with io.open(get_data_path() + f"{file}.yml", "w", encoding="utf8") as yaml_file:
        yaml.dump(content, yaml_file, indent=2)
# endregion


def env(key):
    load_dotenv(dotenv_path=get_data_path() + ".env")
    return os.getenv(key)


def get_data_path():
    return script_dir + '/data/'

