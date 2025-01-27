import aiohttp
import aiofiles
from pathlib import Path
from typing import Dict, List, Optional
from instagrapi import Client
from instagrapi.exceptions import UserNotFound
from console import console


class DownloadManager:
    def __init__(self, client: Client, config: Dict):
        self.client = client
        self.config = config
        self.videos_to_download = self.config.get('videos_to_download', 10)

    async def _validate_user(self, username: str) -> Optional[Dict] | None:
        try:
            user_info = self.client.user_info_by_username_v1(username)
            user_info_dict = user_info.model_dump()

            if user_info_dict.get("media_count", 0) == 0:
                console.print(f"[bold red]У пользователя {username} нет публикаций[/bold red]")
                return None

            return user_info_dict

        except UserNotFound:
            console.print(f"[bold red]Пользователь {username} не найден[/bold red]")
            return None
        except Exception as e:
            console.print(f"[bold red]Ошибка при проверке пользователя {username}: {e}[/bold red]")
            return None

    async def get_last_videos(self, username: str) -> List:
        user_info_dict = await self._validate_user(username)
        if not user_info_dict:
            return []

        medias = self.client.user_medias(user_info_dict.get("pk"), amount=self.videos_to_download)

        videos = [video.video_url for video in medias if video.media_type == 2 and video.video_url]
        if not videos:
            (f"[bold red]У пользователя {username} нет рилсов[/bold red]")
            return []
        return videos

    async def download_video(url: str, save_path: str) -> bool:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                        async with aiofiles.open(save_path, "wb") as file:
                            await file.write(await response.read())
                        return True
                    else:
                        console.print(f"[red]Ошибка загрузки видео: {url} (Статус: {response.status})[/red]")
        except Exception as e:
            console.print(f"[red]Ошибка: {e} при загрузке видео: {url}[/red]")
        return False
