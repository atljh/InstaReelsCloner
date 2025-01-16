from instagrapi import Client
from instagrapi.types import Usertag, UserShort
from moviepy.editor import VideoFileClip
from PIL import ImageEnhance, Image
import numpy as np
import os
import uuid
import time
import random
import json

client = Client()

session_path = "session.json"

if os.path.exists(session_path):
    try:
        client.load_settings(session_path)
        print("Сессия загружена.")
    except Exception as e:
        print(f"Ошибка при загрузке сессии: {e}")
else:
    print("Сессия не найдена. Требуется вход в аккаунт.")

if not client.user_id:
    username = ''
    password = ''
    try:
        client.login(username, password)
        print("Успешный вход в аккаунт!")
        client.dump_settings(session_path)
    except Exception as e:
        print(f"Ошибка при входе: {e}")
        exit()

download_folder = ''
os.makedirs(download_folder, exist_ok=True)

last_processed_video_file = 'last_processed_video.txt'

def load_last_processed_video():
    if os.path.exists(last_processed_video_file):
        with open(last_processed_video_file, 'r') as f:
            return f.read().strip()
    return None

def save_last_processed_video(media_pk):
    with open(last_processed_video_file, 'w') as f:
        f.write(str(media_pk))

def unique_video(video_path):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Файл {video_path} не найден!")

    unique_filename = str(uuid.uuid4()) + '.mp4'
    output_path = os.path.join(download_folder, unique_filename)

    clip = VideoFileClip(video_path)

    def adjust_contrast_exposure(frame):
        img = Image.fromarray(frame)
        img = ImageEnhance.Contrast(img).enhance(1.1)
        img = ImageEnhance.Brightness(img).enhance(1.05)
        return np.array(img)

    clip = clip.fl_image(adjust_contrast_exposure)
    clip.write_videofile(output_path, codec='libx264')

    return output_path

def unique_description(description):
    if not description:
        return "😊"

    description = description.title()

    emojis = ["😊", "🌟", "🔥", "🎉", "💡", "✨", "🚀", "💎"]
    description += f" {random.choice(emojis)}"

    return description

def download_video(media_pk, folder):
    media_info = client.media_info(media_pk)
    if media_info.media_type == 2:
        video_url = media_info.video_url

        video_name = f"{media_pk}.mp4"
        video_path = os.path.join(folder, video_name)

        client.video_download_by_url(video_url, video_path)

        if os.path.exists(video_path + ".mp4"):
            if os.path.exists(video_path):
                os.remove(video_path)
            os.rename(video_path + ".mp4", video_path)
            return video_path, media_info.caption_text
        else:
            print(f"Ошибка: файл {video_path} не был создан!")
            return None, None
    return None, None

def upload_to_reels(video_path, caption, user_short):
    try:
        client.clip_upload(
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

def monitor_account(target_username, interval=300):
    print(f"Начинаем следить за аккаунтом {target_username}...")
    last_processed_video = load_last_processed_video()

    while True:
        try:
            user_id = client.user_id_from_username(target_username)
            medias = client.user_medias(user_id, amount=1)

            if medias:
                latest_media = medias[0]
                if latest_media.pk != last_processed_video and latest_media.media_type == 2:
                    print(f"Обнаружено новое видео: {latest_media.pk}")
                    last_processed_video = latest_media.pk

                    video_path, original_description = download_video(latest_media.pk, download_folder)
                    if video_path:
                        print(f"Видео скачано: {video_path}")

                        if os.path.exists(video_path):
                            unique_video_path = unique_video(video_path)
                            print(f"Видео уникализировано: {unique_video_path}")

                            unique_desc = unique_description(original_description)
                            print(f"Уникализированное описание: {unique_desc}")

                            user_info = client.user_info_by_username(username)
                            user_short = UserShort(
                                pk=user_info.pk,
                                username=user_info.username,
                                full_name=user_info.full_name,
                                profile_pic_url=user_info.profile_pic_url
                            )

                            upload_to_reels(unique_video_path, unique_desc, user_short)
                            save_last_processed_video(latest_media.pk)
                        else:
                            print(f"Ошибка: файл {video_path} не найден!")
        except Exception as e:
            print(f"Ошибка: {e}")
            retry_delay = random.randint(300, 600)
            print(f"Повторная попытка через {retry_delay // 60} минут...")
            time.sleep(retry_delay)
            continue

        time.sleep(interval)

target_username = ''

monitor_account(target_username)
