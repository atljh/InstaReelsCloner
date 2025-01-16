import os
import uuid
import time
import yaml
import random
import numpy as np
from typing import Dict, Any, TypedDict
from PIL import ImageEnhance, Image

from instagrapi import Client
from instagrapi.types import Usertag, UserShort
from moviepy.editor import VideoFileClip


class Config(TypedDict):
    username: str
    password: str
    target_username: str
    download_folder: str
    check_interval: int


def load_config(config_file: str = 'config.yaml') -> Config:
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config: Config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Конфигурационный файл '{config_file}' не найден.")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Ошибка при чтении YAML-файла: {e}")


print(load_config())
