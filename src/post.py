import logging
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired

logger = logging.getLogger("ReelsCloner")


class PostManager:
    def __init__(self, client: Client):
        self.client = client

    async def post_video(self, video_path: str, description: str) -> bool:
        try:
            self.client.clip_upload(
                video_path,
                caption=description,
                thumbnail=None,
                location=None,
                extra_data={}
            )
            logger.success(f"Видео загружено | Путь: {video_path}")
            return True

        except LoginRequired:
            logger.error("Ошибка: требуется повторная авторизация.")
            return False
        except ChallengeRequired:
            logger.error("Ошибка: требуется подтверждение аккаунта (например, через SMS).")
            return False
        except Exception as e:
            logger.error(f"Ошибка при публикации видео: {str(e)}")
            return False
