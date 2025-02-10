import asyncio
import os
import random
from typing import List
from console import console
from src.video_manager import VideoManager
from src.auth import AuthManager
from src.scheduler import Scheduler


class ReelsPoster:
    def __init__(self, config: dict):
        self.config = config
        self.auth_manager = AuthManager(config)
        self.video_manager = VideoManager(self.auth_manager.client)
        self.scheduler = Scheduler(self.config)

    async def start(self) -> None:
        console.print("[green]🚀 Запуск планировщика загрузки видео...[/green]")
        while True:
            await self.handle_time()
            await asyncio.sleep(60)

    async def handle_time(self) -> None:
        folder, descriptions = self.scheduler.get_scheduled_folder()
        if folder:
            console.print(f"[green]🚀 Начинаем загрузку видео из {folder}...[/green]")
            await self.auth_manager.login()
            await self.post_reels(folder, descriptions)
            await self.auth_manager.logout()

    async def post_reels(self, folder: str, descriptions: List[str]) -> None:
        video_files = self.video_manager.get_video_files(folder)
        if not video_files:
            return

        video = video_files[0]
        description = random.choice(descriptions) if descriptions else ""
        console.print(f"📢 Загружаем видео {video} с описанием: {description}")

        video_path = os.path.join(folder, video)
        result = self.video_manager.post_video(video_path, description)

        if result:
            await asyncio.sleep(5)
            await self.video_manager.delete_video(video_path, video, folder)
