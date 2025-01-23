import os
import sys
import uuid
import yaml
import random
import asyncio
import numpy as np
import json
import logging
from typing import List, TypedDict, Dict, Optional
from PIL import ImageEnhance, Image
from colorama import Fore, Style, init
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
from moviepy.editor import VideoFileClip

logging.SUCCESS = 25
logging.addLevelName(logging.SUCCESS, 'SUCCESS')


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(logging.SUCCESS):
        self._log(logging.SUCCESS, message, args, **kwargs)


logging.Logger.success = success

logger = logging.getLogger("ReelsCloner")
logger.setLevel(logging.INFO)


class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.INFO: Fore.CYAN + "[%(asctime)s] %(message)s" + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + "[%(asctime)s] ⚠️ %(message)s" + Style.RESET_ALL,
        logging.ERROR: Fore.RED + "[%(asctime)s] ❌ ОШИБКА: %(message)s" + Style.RESET_ALL,
        logging.SUCCESS: Fore.GREEN + "[%(asctime)s] ✅ %(message)s" + Style.RESET_ALL,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


handler = logging.StreamHandler()
handler.setFormatter(CustomFormatter())
logger.addHandler(handler)


class Config(TypedDict):
    username: str
    password: str
    target_usernames: List[str]
    download_folder: str
    check_interval: int
    proxy: Optional[Dict[str, str]]


def load_config(config_file: str = 'config.yaml') -> Config:
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config: Config = yaml.safe_load(file)
            logger.success(f"Конфигурация загружена из {config_file}")
            return config
    except FileNotFoundError:
        logger.error(f"Конфигурационный файл '{config_file}' не найден.")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Ошибка при чтении YAML-файла: {e}")
        sys.exit(1)


def load_usernames(usernames_file: str = 'usernames.txt') -> List[str]:
    usernames = []
    try:
        with open(usernames_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    usernames.append(line)
        if not len(usernames):
            logger.warning("Ключевые слова не найдены")
            sys.exit(1)
        logger.success(f"Загружено {len(usernames)} аккаунтов для мониторинга")
        return usernames
    except FileNotFoundError:
        logger.error(f"Файл {usernames_file} не найден")
        sys.exit(1)


class ReelsCloner:
    def __init__(self, config: Config):
        self.client = Client()
        self.config = config
        self.session_file = 'session.json'
        self.client.delay_range = [1, 3]
        self.last_processed_videos_file = 'last_processed_videos.json'

        if self.config.get('proxy'):
            proxy_url = self.config['proxy']
            self.client.set_proxy(proxy_url)
            logger.info(f"Прокси настроены: {proxy_url}")

        logger.success(
            f"Инициализация ReelsCloner завершена | Прокси: {'активен' if config.get('proxy') else 'отсутствует'}"
        )

    def load_session(self, client: Client, session_file: str = 'session.json') -> bool:
        try:
            if os.path.exists(session_file):
                session = client.load_settings(session_file)
                logger.info("Сессия успешно загружена из файла")
                return session
            logger.warning("Файл сессии не найден")
            return False
        except Exception as e:
            logger.error(f"Ошибка загрузки сессии: {str(e)}")
            return False

    def login(self, cl: Client, config: Config, session_path: str = 'session.json') -> bool:
        session = self.load_session(cl, session_path)
        login_via_session = False
        login_via_pw = False

        if session:
            try:
                cl.set_settings(session)
                cl.login(config['username'], config['password'])
                logger.success(f"Успешная авторизация: {config['username']}")
                try:
                    cl.get_timeline_feed()
                except LoginRequired:
                    old_session = cl.get_settings()
                    cl.set_settings({})
                    cl.set_uuids(old_session["uuids"])
                    cl.login(config['username'], config['password'])
                login_via_session = True
            except ChallengeRequired:
                logger.error("Нужно подтверждение аккаунта по смс")
                sys.exit(1)
            except Exception as e:
                if "Failed to parse" in str(e):
                    logger.error("Прокси не валидные")
                    sys.exit(1)
                elif "waif" in str(e):
                    logger.warning("Подождите несколько минут и попробуйте еще раз")
                    sys.exit(1)
                logger.error(f"Ошибка при авторизации: {e}")

        if not login_via_session:
            try:
                logger.info("Пробуем зайти через логин/пароль")
                if cl.login(config['username'], config['password']):
                    login_via_pw = True
                    cl.dump_settings(session_path)
            except Exception as e:
                logger.error(f"Ошибка при входе через логин и пароль: {e}")

        if not login_via_pw and not login_via_session:
            logger.error("Не удалось войти ни через сессию, ни через пароль")
            raise Exception("Couldn't login user with either password or session")

    def load_last_processed_videos(self) -> Dict[str, str]:
        if not os.path.exists(self.last_processed_videos_file):
            with open(self.last_processed_videos_file, 'w') as f:
                json.dump({}, f)
            return {}

        with open(self.last_processed_videos_file, 'r') as f:
            return json.load(f)

    def save_last_processed_video(self, username: str, media_pk: str):
        last_processed_videos = self.load_last_processed_videos()
        last_processed_videos[username] = media_pk
        with open(self.last_processed_videos_file, 'w') as f:
            json.dump(last_processed_videos, f, indent=4)

    def unique_video(self, video_path):
        if not os.path.exists(video_path):
            logger.error(f"Файл {video_path} не найден!")
            raise FileNotFoundError(f"Файл {video_path} не найден!")

        unique_filename = str(uuid.uuid4()) + '.mp4'
        output_path = os.path.join(self.config['download_folder'], unique_filename)
        clip = VideoFileClip(video_path)

        def adjust_contrast_exposure(frame):
            img = Image.fromarray(frame)
            img = ImageEnhance.Contrast(img).enhance(1.1)
            img = ImageEnhance.Brightness(img).enhance(1.05)
            return np.array(img)

        clip = clip.fl_image(adjust_contrast_exposure)
        clip.write_videofile(output_path, codec='libx264', logger=None)

        logger.info(f"Видео уникализировано: {output_path}")
        return output_path

    def unique_description(self, description: str) -> str:
        if not description:
            return "😊"

        description = description.title()
        emojis = ["😊", "🌟", "🔥", "🎉", "💡", "✨", "🚀", "💎"]
        description += f" {random.choice(emojis)}"

        logger.info(f"Описание уникализировано: {description}")
        return description

    def download_video(self, media_pk: str, folder: str, username: str) -> tuple[str | None, str | None]:
        try:
            media_info = self.client.media_info(media_pk)
            if media_info.media_type == 2:
                folder = f"{folder}/{username}"
                os.makedirs(folder, exist_ok=True)
                video_url = media_info.video_url
                video_path = os.path.join(folder, str(media_pk))
                self.client.video_download_by_url(video_url, video_path)
                video_path = video_path + ".mp4"
                if os.path.exists(video_path):
                    logger.success(f"Видео скачано | Пользователь: {username} | ID: {media_pk}")
                    return video_path, media_info.caption_text
                else:
                    logger.error(f"Ошибка: файл {video_path} не был создан!")
                    return None, None
            return None, None
        except Exception as e:
            logger.error(f"Ошибка загрузки видео: {str(e)}")
            return None, None

    def upload_to_reels(self, video_path: str, caption: str):
        try:
            self.client.clip_upload(
                video_path,
                caption=caption,
                thumbnail=None,
                location=None,
                extra_data={}
            )
            logger.success(f"Видео загружено | Путь: {video_path}")
        except Exception as e:
            logger.error(f"Ошибка загрузки в Reels: {str(e)}")

    async def post_video(self, video_path: str, original_description: str, target_username: str, latest_media: str):
        unique_video_path = self.unique_video(video_path)
        unique_desc = self.unique_description(original_description)
        self.upload_to_reels(unique_video_path, unique_desc)

    async def monitor_account(self, target_username: str, interval: int = 300):
        logger.info(f"Запуск мониторинга аккаунта: @{target_username}")
        last_processed_videos = self.load_last_processed_videos()
        last_processed_video = last_processed_videos.get(target_username)
        while True:
            try:
                user_info_dict = self.client.user_info_by_username_v1(target_username).model_dump()
                medias = self.client.user_medias(user_info_dict.get("pk"), amount=1)

                if medias and len(medias) > 0:
                    latest_media = medias[0]
                    if latest_media.media_type == 2 and latest_media.pk != last_processed_video:
                        logger.success(f"Обнаружен новый Reels: @{target_username} | ID: {latest_media.pk}")
                        self.save_last_processed_video(target_username, latest_media.pk)
                        last_processed_video = latest_media.pk

                        video_path, original_description = self.download_video(
                            latest_media.pk, self.config['download_folder'], target_username
                        )
                        if not video_path:
                            return
                        await self.post_video(video_path, original_description, target_username, latest_media)
            except LoginRequired:
                logger.warning("Сессия устарела. Требуется повторный вход.")
                self.login(self.client, self.config, self.session_file)
            except ChallengeRequired:
                logger.error("Нужно подтверждение аккаунта по смс")
                sys.exit(1)
            except Exception as e:
                if "429" in str(e):
                    logger.warning("Превышен лимит запросов. Увеличиваю задержку...")
                    await asyncio.sleep(60)
                else:
                    logger.error(f"Ошибка при мониторинге {target_username}: {e}")

            await asyncio.sleep(interval)

    def start(self):
        self.login(self.client, self.config, self.session_file)


async def main():
    config = load_config()
    cloner = ReelsCloner(config)
    cloner.start()

    usernames = load_usernames()

    tasks = [cloner.monitor_account(username, config['check_interval']) for username in usernames]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())
