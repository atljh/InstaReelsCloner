import asyncio
from rich.prompt import Prompt
from rich.panel import Panel
from src import ReelsCloner, ReelsPoster, load_config, console


def display_welcome_message() -> None:
    console.print(Panel.fit("🎥 [bold cyan]Reels Cloner & Poster[/bold cyan] 🎬", border_style="green"))
    console.print("Добро пожаловать! Выберите действие:", style="bold yellow")


async def display_menu() -> int:
    console.print("1. Скачать видео")
    console.print("2. Загружать видео")
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
                poster = ReelsPoster(config)
                background_task = asyncio.create_task(poster.start())
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
