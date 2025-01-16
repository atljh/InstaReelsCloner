import os
import sys
import uuid
import time
import yaml
import random
import numpy as np
from typing import List, TypedDict
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


def load_config(
    config_file: str = 'config.yaml'
) -> Config:
    try:
        with open(
            config_file, 'r',
            encoding='utf-8'
        ) as file:
            config: Config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Конфигурационный файл '{config_file}' не найден.")
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Ошибка при чтении YAML-файла: {e}")


def load_usernames(
    usernames_file: str = 'usernames.txt'
) -> List[str] | None:
    usernames = []
    try:
        with open(
            usernames_file, 'r',
            encoding='utf-8'
        ) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    usernames.append(line)
        if not len(usernames):
            print("Ключевые слова не найдены")
            sys.exit(1)
        return usernames
    except FileNotFoundError:
        print(f"Файл {usernames_file} не найден")
        sys.exit(1)


def load_session(
        client: Client,
        session_file: str = 'session.json'
) -> bool:
    if os.path.exists(session_file):
        try:
            client.load_settings(session_file)
            print("Сессия загружена.")
            return True
        except Exception as e:
            print(f"Ошибка при загрузке сессии: {e}")
            sys.exit(1)
            return False
    else:
        print("Сессия не найдена. Требуется вход в аккаунт.")
        sys.exit(1)
        return False


config = load_config()
usernames = load_usernames()
os.makedirs(config["download_folder"], exist_ok=True)
