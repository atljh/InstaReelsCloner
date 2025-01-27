import os
import logging
from typing import Dict, List, Optional, Tuple
from instagrapi import Client

logger = logging.getLogger("ReelsCloner")


class DownloadManager:
    def __init__(self, client: Client, config: Dict):
        self.client = client
        self.config = config
        self.videos_to_download = self.config.get('videos_to_download', 10)
        self.last_processed_videos_file = 'last_processed_videos.json'

    async def get_last_videos(self, username: str) -> List:
        user_info_dict = self.client.user_info_by_username_v1(username).model_dump()
        medias = self.client.user_medias(user_info_dict.get("pk"), amount=self.videos_to_download)
        return medias

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
                    logger.success(f"Видео скачано | Пользователь: {username} | ID: {media_pk}")
                    return video_path, media_info.caption_text
                else:
                    logger.error(f"Ошибка: файл {video_path} не был создан!")
                    return None, None
            return None, None
        except Exception as e:
            logger.error(f"Ошибка загрузки видео: {str(e)}")
            return None, None
