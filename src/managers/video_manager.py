import os
from src.tools import console
from src.managers import PostManager


class VideoManager:
    def __init__(self, client):
        self.post_manager = PostManager(client)

    def get_video_files(self, folder):
        try:
            return [f for f in os.listdir(folder) if f.endswith((".mp4", ".mov", ".avi"))]
        except FileNotFoundError:
            console.print(f"[red]❌ Папка {folder} не найдена[/red]")
            return []

    async def post_video(self, video_path: str, description: str) -> bool:
        for attempt in range(3):
            console.print(f"[cyan]⌛ Загрузка видео {video_path}, попытка {attempt + 1}...[/cyan]")
            post_result = await self.post_manager.post_video(video_path, description)
            if post_result:
                console.print(f"[green]✅ Видео {video_path} успешно загружено![/green]")
                return True
            console.print(f"[red]❌ Не удалось загрузить видео {video_path}. Пробуем снова...[/red]")

        console.print(f"[red]⚠️ Видео {video_path} не загружено. Удаляем файл, пробуем загрузить следующее видео[/red]")
        return False

    async def delete_video(self, video_path: str, video: str, folder: str):
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
            image_name = f'{video_path}.jpg'
            if os.path.exists(image_name):
                os.remove(image_name)
            console.print(f"\n[green]✅ Видео {video} удалено из {folder}[/green]")
        except Exception as e:
            console.print(f"\n[red]❌ Ошибка при удалении видео {video}: {e}[/red]")
