import asyncio
import os
import time
import random
from typing import List
from src.tools import console
from src.managers import VideoManager, AuthManager, Scheduler


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
            await self.post_reels(folder, descriptions)

    async def post_reels(self, folder: str, descriptions: List[str]) -> bool:
        video_files = self.video_manager.get_video_files(folder)
        if not video_files:
            console.print(f"Видео в папке {folder} не найдены")
            return

        video = video_files[0]
        video_path = os.path.join(folder, video)
        description = random.choice(descriptions) if descriptions else ""
        console.print(f"📢 Загружаем видео {video} с описанием: {description}")

        self.auth_manager.login(logs=False)
        post_result = await self.video_manager.post_video(video_path, description)
        self.auth_manager.logout(logs=False)
        console.print("Удаляем видео, очищаем кеш...")
        self.video_manager.delete_video(video_path, video, folder)
        if post_result:
            return True
        result = await self.post_reels(folder, descriptions)
        return result
