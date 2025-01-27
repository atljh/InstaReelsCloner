import os
from typing import Dict, List, Optional, Tuple
from instagrapi import Client
from instagrapi.exceptions import UserNotFound
from console import console


class DownloadManager:
    def __init__(self, client: Client, config: Dict):
        self.client = client
        self.config = config
        self.videos_to_download = self.config.get('videos_to_download', 10)

    async def _validate_user(self, username: str) -> Optional[Dict]:
        try:
            user_info = self.client.user_info_by_username_v1(username)
            user_info_dict = user_info.model_dump()

            if user_info_dict.get("media_count", 0) == 0:
                console.print(f"[bold red]У пользователя {username} нет публикаций[/bold red]")
                return None

            return user_info_dict

        except UserNotFound:
            console.print(f"[bold red]Пользователь {username} не найден[/bold red]")
            raise
        except Exception as e:
            console.print(f"[bold red]Ошибка при проверке пользователя {username}: {e}[/bold red]")
            raise

    async def get_last_videos(self, username: str) -> List:
        user_info_dict = await self._validate_user(username)
        if not user_info_dict:
            return []

        medias = self.client.user_medias(user_info_dict.get("pk"), amount=self.videos_to_download)

        videos = [media for media in medias if media.media_type == 2]
        if not videos:
            (f"[bold red]У пользователя {username} нет рилсов[/bold red]")
            return []

        return videos

    def download_video(self, media_pk: str, folder: str, username: str) -> Tuple[Optional[str], Optional[str]]:
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
                    console.print(f"Видео скачано | Пользователь: {username} | ID: {media_pk}")
                    return video_path, media_info.caption_text
                else:
                    console.print(f"Ошибка: файл {video_path} не был создан!")
                    return None, None
            return None, None
        except Exception as e:
            console.print(f"Ошибка загрузки видео: {str(e)}")
            return None, None
