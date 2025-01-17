import os
import sys
import uuid
import time
import yaml
import random
import asyncio
import numpy as np
import json
from typing import List, TypedDict, Dict
from PIL import ImageEnhance, Image

from instagrapi import Client
from instagrapi.types import Usertag, UserShort
from instagrapi.exceptions import LoginRequired
from moviepy.editor import VideoFileClip


class Config(TypedDict):
    username: str
    password: str
    target_usernames: List[str]
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
) -> List[str]:
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


class ReelsCloner:
    def __init__(
        self,
        config: Config
    ):
        self.client = Client()
        self.config = config
        self.session_file = 'session.json'
        self.client.delay_range = [1, 3]
        self.last_processed_videos_file = 'last_processed_videos.json'

    def load_session(
        self,
        client: Client,
        session_file: str = 'session.json'
    ) -> bool:
        if os.path.exists(session_file):
            client.load_settings(session_file)
            print("Сессия загружена")
            return True
        print("Файл сессии не найден")
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

    def load_last_processed_videos(self) -> Dict[str, str]:
        if os.path.exists(self.last_processed_videos_file):
            with open(self.last_processed_videos_file, 'r') as f:
                return json.load(f)
        return {}

    def save_last_processed_video(self, username: str, media_pk: str):
        last_processed_videos = self.load_last_processed_videos()
        last_processed_videos[username] = media_pk
        with open(self.last_processed_videos_file, 'w') as f:
            json.dump(last_processed_videos, f, indent=4)

    def unique_video(self, video_path: str) -> str:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Файл {video_path} не найден!")

        unique_filename = str(uuid.uuid4())
        output_path = os.path.join(self.config['download_folder'], unique_filename)

        clip = VideoFileClip(video_path)

        def adjust_contrast_exposure(frame):
            img = Image.fromarray(frame)
            img = ImageEnhance.Contrast(img).enhance(1.1)
            img = ImageEnhance.Brightness(img).enhance(1.05)
            return np.array(img)

        clip = clip.fl_image(adjust_contrast_exposure)
        clip.write_videofile(output_path, codec='libx264')

        return output_path

    def unique_description(self, description: str) -> str:
        if not description:
            return "😊"

        description = description.title()

        emojis = ["😊", "🌟", "🔥", "🎉", "💡", "✨", "🚀", "💎"]
        description += f" {random.choice(emojis)}"

        return description

    def download_video(self, media_pk: str, folder: str) -> tuple[str | None, str | None]:
        media_info = self.client.media_info(media_pk)
        if media_info.media_type == 2:
            video_url = media_info.video_url
            video_name = f"{media_pk}"
            video_path = os.path.join(folder, video_name)
            print(video_path)
            self.client.video_download_by_url(video_url, video_path)
            video_path = video_path + ".mp4"
            if os.path.exists(video_path):
                # if os.path.exists(video_path):
                    # os.remove(video_path)
                # os.rename(video_path, video_path)
                return video_path, media_info.caption_text
            else:
                print(f"Ошибка: файл {video_path} не был создан!")
                return None, None
        return None, None

    def upload_to_reels(self, video_path: str, caption: str, user_short: UserShort):
        try:
            self.client.clip_upload(
                video_path,
                caption=caption,
                thumbnail=None,
                usertags=[Usertag(user=user_short, x=0.5, y=0.5)],
                location=None,
                extra_data={}
            )
            print(f"Видео {video_path} успешно загружено в Instagram Reels!")
        except Exception as e:
            print(f"Ошибка при загрузке видео: {e}")

    async def post_video(self, video_path: str, original_description: str, target_username: str, latest_media: str):
        print(f"Reels скачан: {video_path}")

        unique_video_path = self.unique_video(video_path)
        print(f"Reels уникализирован: {unique_video_path}")

        unique_desc = self.unique_description(original_description)
        print(f"Уникализированное описание: {unique_desc}")

        user_info = self.client.user_info_by_username(self.config['username'])
        user_short = UserShort(
            pk=user_info.pk,
            username=user_info.username,
            full_name=user_info.full_name,
            profile_pic_url=user_info.profile_pic_url
        )

        self.upload_to_reels(unique_video_path, unique_desc, user_short)
        self.save_last_processed_video(target_username, latest_media.pk)

    async def monitor_account(self, target_username: str, interval: int = 300):
        print(f"Начинаем следить за аккаунтом {target_username}...")
        last_processed_videos = self.load_last_processed_videos()
        last_processed_video = last_processed_videos.get(target_username)

        while True:
            try:
                user_info_dict = self.client.user_info_by_username_v1(target_username).dict()
                medias = self.client.user_medias(user_info_dict.get("pk"), amount=1)

                if medias:
                    latest_media = medias[0]
                    if latest_media.media_type == 2 and latest_media.pk != last_processed_video:
                        print(f"Обнаружен новый Reels от {target_username}: {latest_media.pk}")
                        last_processed_video = latest_media.pk

                        video_path, original_description = self.download_video(
                            latest_media.pk, self.config['download_folder']
                        )
                        if video_path:
                            self.post_video(video_path, original_description)


            except Exception as e:
                print(f"Ошибка при мониторинге {target_username}: {e}")
                retry_delay = random.randint(300, 600)
                print(f"Повторная попытка через {retry_delay // 60} минут...")
                await asyncio.sleep(retry_delay)
                continue

            await asyncio.sleep(interval)

    def start(self):
        self.load_session(self.client, self.session_file)
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
