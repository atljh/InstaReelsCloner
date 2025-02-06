import os
import asyncio
import random
from datetime import datetime, timedelta
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

    def post_video(self, video_path: str, description: str) -> None:
        console.print(f"[cyan]⌛ Загрузка видео {video_path}...[/cyan]")
        result = self.post_manager.post_video(video_path, description)
        if result:
            console.print(f"[green]✅ Видео {video_path} успешно загружено![/green]")
        return result

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

        result = self.post_video(video_path, description)
        if not result:
            return
        await asyncio.sleep(5)
        import shutil
        import gc
        gc.collect()
        try:
            shutil.move(video_path, "temp_deleted.mp4")
            os.remove("temp_deleted.mp4")
            image_name = f'{video_path}.jpg'
            if os.path.exists(image_name):
                os.remove(image_name)
            console.print(f"\n[green]✅ Видео {video} удалено из папки {folder}[/green]")
        except Exception as e:
            console.print(f"\n[red]❌ Ошибка при удалении видео {video}: {e}[/red]")

    async def handle_time(self) -> None:
        current_time = datetime.now().strftime("%H:%M")

        if current_time in self.folder_1_times:
            console.print(f"\n[cyan]🕒 Текущее время: {current_time}[/cyan]")
            console.print(f"[green]🚀 Начинаем загрузку видео из {self.folder_1}...[/green]")
            await self._login()
            await self.post_reels(self.folder_1, self.folder_1_descriptions)
            await self._logout()
        elif current_time in self.folder_2_times:
            console.print(f"\n[cyan]🕒 Текущее время: {current_time}[/cyan]")
            console.print(f"[green]🚀 Начинаем загрузку видео из {self.folder_2}...[/green]")
            await self._login()
            await self.post_reels(self.folder_2, self.folder_2_descriptions)
            await self._logout()
        else:
            nearest_time_folder_1 = self._get_nearest_time(self.folder_1_times, current_time)
            nearest_time_folder_2 = self._get_nearest_time(self.folder_2_times, current_time)

            time_until_folder_1 = self._get_time_difference(current_time, nearest_time_folder_1)
            time_until_folder_2 = self._get_time_difference(current_time, nearest_time_folder_2)

            console.print(f"\n[cyan]🕒 Текущее время: {current_time}[/cyan]")
            console.print(f"[yellow]⏳ Ближайшее время для загрузки видео из {self.folder_1}: {nearest_time_folder_1} (через {time_until_folder_1})...[/yellow]")
            console.print(f"[yellow]⏳ Ближайшее время для загрузки видео из {self.folder_2}: {nearest_time_folder_2} (через {time_until_folder_2})...[/yellow]")

    def _get_nearest_time(self, times: List[str], current_time: str) -> str:
        current = datetime.strptime(current_time, "%H:%M")
        nearest_time = None
        min_difference = timedelta.max

        for time in times:
            target = datetime.strptime(time, "%H:%M")
            if target < current:
                target += timedelta(days=1)

            difference = target - current
            if difference < min_difference:
                min_difference = difference
                nearest_time = time
        return nearest_time

    def _get_time_difference(self, current_time: str, target_time: str) -> str:
        current = datetime.strptime(current_time, "%H:%M")
        target = datetime.strptime(target_time, "%H:%M")

        if target < current:
            target += timedelta(days=1)

        difference = target - current
        hours, remainder = divmod(difference.seconds, 3600)
        minutes = remainder // 60

        if hours > 0:
            return f"{hours} ч {minutes} мин"
        return f"{minutes} мин"

    async def start(self) -> None:
        console.print("[green]🚀 Запуск планировщика загрузки видео...[/green]")

        while True:
            await self.handle_time()
            await asyncio.sleep(60)
