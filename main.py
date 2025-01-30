import os
import asyncio
import random
from datetime import datetime
from typing import Dict
from rich.prompt import Prompt
from rich.panel import Panel
from src.auth import AuthManager
from src.post import PostManager
from src.download import DownloadManager
from src.uniqueize import UniqueManager
from config import load_config
from console import console


def log(message: str, is_background: bool = False) -> None:
    prefix = "\n[BG] " if is_background else ""
    console.print(f"{prefix}{message}")


class ReelsCloner:
    def __init__(self, config: Dict, username: str):
        self.config = config
        self.username = username
        self.auth_manager = AuthManager(config)
        self.download_manager = DownloadManager(self.auth_manager.client, config)
        self.unique_manager = UniqueManager(config)

    async def _login(self) -> bool:
        return self.auth_manager.login()

    async def _logout(self) -> None:
        self.auth_manager.logout()

    async def download_videos(self) -> bool:
        download_res = await self.download_manager._main(self.username)
        if not download_res:
            return False
        console.print("[blue]Скачивание завершено[/]")
        return True

    async def uniqueize_videos(self) -> None:
        self.unique_manager._main()

    async def start(self) -> None:
        login_res = await self._login()
        if not login_res:
            return
        result = await self.download_videos()
        await self._logout()
        if not result:
            return
        if not self.config.get("uniqueize", False):
            return
        console.print("[green]Уникализация видео...[/]")
        await self.uniqueize_videos()


class ReelsPoster:
    def __init__(self, config: Dict):
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
        log("Пост видео", is_background=True)
        # await self.post_manager.post_video(video_path)

    async def post_reels(self, folder: str) -> None:
        video_files = [f for f in os.listdir(folder) if f.endswith((".mp4", ".mov", ".avi"))]
        description_files = [f for f in os.listdir(folder) if f.endswith(".txt")]

        if not video_files:
            print(f"Нет видеофайлов в папке {folder}")
            return

        if not description_files:
            print(f"Нет описаний в папке {folder}, постинг без описания")
            description = ""
        else:
            random_description_file = random.choice(description_files)
            with open(os.path.join(folder, random_description_file), "r", encoding="utf-8") as f:
                description = f.read().strip()

        random_video = random.choice(video_files)
        video_path = os.path.join(folder, random_video)

        print(f"📢 Загружаем видео {random_video} с описанием: {description}")
        await self.post_video(video_path, description)

    async def handle_time(self) -> None:
        current_time = datetime.now().strftime("%H:%M")
        if current_time in self.folder_1_times:
            await self.post_reels(self.folder_1)
        elif current_time in self.folder_2_times:
            await self.post_reels(self.folder_2)

    async def start(self) -> None:
        while True:
            await self.handle_time()
            await asyncio.sleep(60)


def display_welcome_message() -> None:
    console.print(Panel.fit("🎥 [bold cyan]Reels Cloner & Poster[/bold cyan] 🎬", border_style="green"))
    console.print("Добро пожаловать! Выберите действие:", style="bold yellow")


async def display_menu() -> int:
    console.print("1. Скачать видео", style="bold blue")
    console.print("2. Загружать видео", style="bold blue")
    console.print("3. Выйти", style="bold red")
    choice = await asyncio.to_thread(Prompt.ask, "Введите номер действия", choices=["1", "2", "3"], default="3")
    return int(choice)


async def main() -> None:
    display_welcome_message()
    config = load_config()

    background_task = None

    while True:
        action = await display_menu()

        if action == 1:
            username = Prompt.ask("Введите юзернейм").replace(" ", "")
            cloner = ReelsCloner(config, username)
            await cloner.start()

        elif action == 2:
            if background_task and not background_task.done():
                console.print("\n[bold yellow]Публикация уже запущена в фоне.[/bold yellow]")
            else:
                console.print("\n[bold green]Запуск публикации видео в фоне...[/bold green]")
                poster = ReelsPoster(config)
                background_task = asyncio.create_task(poster.start())
                console.print("[bold green]Публикация запущена в фоне.[/bold green]")
                await asyncio.sleep(1)

        elif action == 3:
            console.print("\n[bold red]Выход из программы...[/bold red]")
            if background_task and not background_task.done():
                background_task.cancel()
                try:
                    await background_task
                except asyncio.CancelledError:
                    console.print("[bold yellow]Фоновая задача публикации остановлена.[/bold yellow]")
            break

        else:
            console.print("\n[bold red]Неверный выбор действия.[/bold red]")


if __name__ == '__main__':
    asyncio.run(main())
