import asyncio
from pathlib import Path
from typing import Dict, List, Optional
from instagrapi import Client
from instagrapi.exceptions import UserNotFound
from console import console


class DownloadManager:
    def __init__(self, client: Client, config: Dict):
        self.client = client
        self.request_timeout = 30
        self.config = config
        self.retries = 3
        self.delay = 5
        self.videos_to_download = self.config.get('videos_to_download', 10)
        self.download_dir = Path("downloads/videos")

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

    async def download_video(self, url: str, save_path: str) -> bool:
        try:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            self.client.video_download_by_url(url, save_path)
            return True
        except Exception as e:
            console.print(f"[red]Ошибка при загрузке видео: {url}, {e}[/red]")
            return False

    async def handle_videos(self, video_urls: List) -> None:
        tasks = []
        for i, url in enumerate(video_urls):
            save_path = Path(self.download_dir) / f"video_{i + 1}.mp4"
            tasks.append(self.download_video(str(url), save_path))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                console.print(f"[red]Ошибка при загрузке видео {video_urls[idx]}: {result}[/red]")
            elif result:
                console.print(f"[green]Видео {idx + 1} успешно загружено.[/green]")
                self.overlay_image_on_video(save_path)
            else:
                console.print(f"[red]Не удалось загрузить видео {idx + 1}.[/red]")

    def overlay_image_on_video(self, video_path: Path) -> None:
        from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

        try:
            video = VideoFileClip(str(video_path))
            image = ImageClip("image.png").set_duration(video.duration).resize(height=100).set_pos(("right", "bottom"))
            final_video = CompositeVideoClip([video, image])
            final_video.write_videofile(str(video_path), codec="libx264")
            console.print(f"[green]Изображение наложено на видео: {video_path}[/green]")
        except Exception as e:
            console.print(f"[red]Ошибка при наложении изображения на видео {video_path}: {e}[/red]")

    async def _main(self, username: str) -> bool:
        console.print(f"\n[bold]Скачивание видео пользователя {username}[/bold]", style="green")
        video_urls = await self.get_last_videos(username)
        if not video_urls:
            return False
        await self.handle_videos(video_urls)
