import asyncio
from typing import Dict, List
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from src.auth import AuthManager
from src.post import PostManager
from src.download import DownloadManager
from src.uniqueize import UniqueManager
from config import load_config, load_usernames
from logger import setup_logger

logger = setup_logger()

console = Console()


class ReelsCloner:
    def __init__(self, config: Dict):
        self.config = config
        self.auth_manager = AuthManager(config)
        self.download_manager = DownloadManager(self.auth_manager.client, config)
        self.unique_manager = UniqueManager(config)

    def _auth(self) -> None:
        self.auth_manager.login()

    async def _get_last_videos(self, usernames: List[str]) -> None:
        videos = []
        for username in usernames:
            video = await self.download_manager.get_last_videos(username)
            videos.append(video)
        return videos

    def start(self) -> None:
        self._auth()


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
    console.print("\n[bold]Меню:[/bold]")
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
            console.print("\n[bold]Скачивание видео[/bold]", style="green")
            cloner = ReelsCloner(config)
            cloner.start()

            usernames = load_usernames()

            # await cloner.download_manager.download_reels(usernames)

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
