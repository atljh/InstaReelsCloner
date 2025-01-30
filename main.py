import asyncio
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
        result = await self._login()
        print(result)
        if not result:
            return False
        await self.download_manager._main(self.username)
        console.print("[blue]Скачивание завершено[/]")
        await self._logout()
        return True

    async def uniqueize_videos(self) -> None:
        self.unique_manager._main()

    async def start(self) -> None:
        result = await self.download_videos()
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

    async def _login(self) -> None:
        self.auth_manager.login()

    async def _logout(self) -> None:
        self.auth_manager.logout()

    async def post_video(self, video_path: str) -> None:
        await self.post_manager.post_video(video_path)

    async def handle_time(self) -> None:
        ...

    async def start(self) -> None:
        console.print("[bold green]Фоновая задача запущена[/bold green]")
        while True:
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
