import logging
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired

logger = logging.getLogger("ReelsCloner")


class PostManager:
    def __init__(self, client: Client):
        """
        Инициализация менеджера для публикации видео.

        Args:
            client (Client): Клиент instagrapi для взаимодействия с Instagram API.
        """
        self.client = client

    async def post_video(self, video_path: str, original_description: str, target_username: str) -> bool:
        """
        Публикует уникализированное видео в Instagram.

        Args:
            video_path (str): Путь к уникализированному видео.
            original_description (str): Оригинальное описание видео.
            target_username (str): Имя пользователя, для которого публикуется видео.

        Returns:
            bool: True, если публикация прошла успешно, иначе False.
        """
        try:
            unique_desc = self.unique_description(original_description)

            self.client.clip_upload(
                video_path,
                caption=unique_desc,
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
