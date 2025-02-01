import os
import asyncio
import random
from datetime import datetime
from typing import List
from src.auth import AuthManager
from src.post import PostManager
from console import console


class ReelsPoster:
    def __init__(self, config: dict):
        self.config = config
        self.auth_manager = AuthManager(config)
        self.post_manager = PostManager(self.auth_manager.client)
        self.folder_1 = config["folder_1"]["folder_name"]
        self.folder_2 = config["folder_2"]["folder_name"]
        self.folder_1_times = config["folder_1"]["times"]
        self.folder_2_times = config["folder_2"]["times"]
        self.folder_1_descriptions = config["folder_1"]["descriptions"]
        self.folder_2_descriptions = config["folder_2"]["descriptions"]

    async def _login(self) -> None:
        self.auth_manager.login()

    async def _logout(self) -> None:
        self.auth_manager.logout()

    async def post_video(self, video_path: str, description: str) -> None:
        console.print(f"[cyan]⌛ Загрузка видео {video_path}...[/cyan]")
        result = await self.post_manager.post_video(video_path, description)
        if result:
            console.print(f"[green]✅ Видео {video_path} успешно загружено![/green]")

    async def post_reels(self, folder: str, descriptions: List[str]) -> None:
        try:
            video_files = [f for f in os.listdir(folder) if f.endswith((".mp4", ".mov", ".avi"))]
        except FileNotFoundError:
            console.print(f"[red]❌ Папка {folder} не найдена[/red]", style="bold red")
            return

        if not video_files:
            console.print(f"[yellow]⚠️ Нет видеофайлов в папке {folder}[/yellow]", style="bold yellow")
            return

        if not descriptions:
            console.print(f"[yellow]⚠️ Нет описаний в папке {folder}, постинг без описания[/yellow]", style="bold yellow")
            description = ""

        video = video_files[0]
        description = random.choice(descriptions) if descriptions else ""
        video_path = os.path.join(folder, video)
        console.print(f"📢 Загружаем видео {video} с описанием: {description}")

        await self.post_video(video_path, description)

        try:
            os.remove(video_path)
            os.remove(f'{video_path}.mp4')
            console.print(f"[green]✅ Видео {video} удалено из папки {folder}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Ошибка при удалении видео {video}: {e}[/red]")

    async def handle_time(self) -> None:
        current_time = datetime.now().strftime("%H:%M")

        if current_time in self.folder_1_times:
            await self._login()
            await self.post_reels(self.folder_1, self.folder_1_descriptions)
            await self._logout()
        elif current_time in self.folder_2_times:
            await self._login()
            await self.post_reels(self.folder_2, self.folder_2_descriptions)
            await self._logout()
        else:
            console.print("[cyan]🕒 Ожидаем следующего времени для загрузки...[/cyan]")

    async def start(self) -> None:
        console.print("[green]🚀 Запуск планировщика загрузки видео...[/green]")
        current_time = datetime.now().strftime("%H:%M")

        console.print(f"[cyan]🕒 Текущее время: {current_time}[/cyan]")
        fold1_times = ' | '.join(self.folder_1_times)
        fold2_times = ' | '.join(self.folder_2_times)
        console.print(f"[cyan]⌛ Ожидаемое время для загрузки видео из {self.folder_1}: {fold1_times}[/cyan]")
        console.print(f"[cyan]⌛ Ожидаемое время для загрузки видео из {self.folder_2}: {fold2_times}[/cyan]")

        while True:
            await self.handle_time()
            await asyncio.sleep(60)
