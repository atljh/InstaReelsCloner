import asyncio
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

    async def _auth(self) -> None:
        self.auth_manager.login()

    async def _get_last_videos(self, username: str) -> None:
        videos = await self.download_manager.get_last_videos(username)
        return videos

    async def start(self) -> None:
        await self._auth()
        videos = await self._get_last_videos(self.username)
        if not videos:
            return
        console.print(videos)


class ReelsPoster:
    def __init__(self, config: Dict):
        self.config = config
        self.auth_manager = AuthManager(config)
        self.post_manager = PostManager(self.auth_manager.client)

    async def post_video(self, video_path: str, original_description: str) -> None:
        unique_desc = self.unique_manager.unique_description(original_description)
        await self.post_manager.post_video(video_path, unique_desc)


def display_welcome_message() -> None:
    console.print(Panel.fit("🎥 [bold cyan]Reels Cloner & Poster[/bold cyan] 🎬", border_style="green"))
    console.print("Добро пожаловать! Выберите действие:", style="bold yellow")


def display_menu() -> int:
    console.print("1. Скачать видео", style="bold blue")
    console.print("2. Загружать видео", style="bold blue")
    console.print("3. Выйти", style="bold red")

    choice = Prompt.ask("Введите номер действия", choices=["1", "2", "3"], default="3")
    return int(choice)


async def main() -> None:

    display_welcome_message()

    config = load_config()

    while True:
        action = display_menu()

        if action == 1:
            username = Prompt.ask("Введите юзернейм").replace(" ", "")
            console.print(f"\n[bold]Скачивание видео пользователя {username}[/bold]", style="green")
            cloner = ReelsCloner(config, username)
            await cloner.start()

        elif action == 2:
            console.print("\n[bold]Публикация видео[/bold]", style="green")
            poster = ReelsPoster(config)
            poster.auth_manager.login()

            # await poster.post_manager.post_video("path/to/video.mp4", "Описание")

        elif action == 3:
            console.print("\n[bold]Выход из программы...[/bold]", style="red")
            break

        else:
            console.print("\n[bold red]Неверный выбор действия.[/bold red]")


if __name__ == '__main__':
    asyncio.run(main())
