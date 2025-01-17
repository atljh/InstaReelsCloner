import os
import sys
import uuid
import time
import yaml
import random
import asyncio
import numpy as np
from typing import List, TypedDict
from PIL import ImageEnhance, Image

from instagrapi import Client
from instagrapi.types import Usertag, UserShort
from instagrapi.exceptions import LoginRequired
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


def session_exist(
        session_file: str = 'session.json'
) -> bool:
    if os.path.exists(session_file):
        return True
    return False


class ReelsCloner():
    def __init__(
        self,
        config: Config
    ):
        self.client = Client()
        self.config = config
        self.session_file = 'session.json'
        self.client.delay_range = [1, 3]

    def load_session(
        self,
        client: Client,
        session_file: str = 'session.json'
    ) -> bool:
        if session_exist():
            client.load_settings(session_file)
            print("Сессия загружена")
            return True
        print("Файл сесси не найден")
        return False

    def login(
        self,
        cl: Client,
        config: Config,
        session_path: str = 'session.json'
    ) -> bool:
        session = cl.load_settings(session_path)
        login_via_session = False
        login_via_pw = False

        if session:
            try:
                cl.set_settings(session)
                cl.login(config['username'], config['password'])
                print("Авторизация успешна")
                try:
                    cl.get_timeline_feed()
                except LoginRequired:
                    print("Сессия не валидная")
                    old_session = cl.get_settings()

                    cl.set_settings({})
                    cl.set_uuids(old_session["uuids"])

                    cl.login(config['username'], config['password'])
                login_via_session = True
            except Exception as e:
                print(f"Ошибка при авторизации: {e}")

        if not login_via_session:
            try:
                print("Пробуем зайти через логин/пароль")
                if cl.login(config['username'], config['password']):
                    login_via_pw = True
            except Exception as e:
                print(f"Ошибка при входе через логин и пароль {e}")

        if not login_via_pw and not login_via_session:
            raise Exception("Couldn't login user with either password or session")

    def start(self):
        self.login(self.client, self.config, self.session_file)
        print(self.client.account_info().dict())

async def main():
    config = load_config()
    cloner = ReelsCloner(config)
    cloner.start()
    usernames = load_usernames()

# os.makedirs(config["download_folder"], exist_ok=True)

if __name__ == '__main__':
    asyncio.run(main())
