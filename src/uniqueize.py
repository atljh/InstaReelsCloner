import os
import random
import numpy as np
from typing import Dict
from concurrent.futures import ProcessPoolExecutor
from PIL import ImageEnhance, Image
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, vfx
from console import console


class UniqueManager:
    def __init__(self, config: Dict):
        self.config = config
        self.video_dir = config.get('download_folder')
        self.output_dir = config.get('output_folder', 'downloads/unique_videos')

        os.makedirs(self.output_dir, exist_ok=True)

    def unique_video(self, video_path: str) -> str:
        if not os.path.exists(video_path):
            console.print(f"[bold red]Файл {video_path} не найден![/bold red]")
            raise FileNotFoundError(f"Файл {video_path} не найден!")
        unique_filename = video_path.split('/')[-1]
        output_path = os.path.join(self.output_dir, unique_filename)
        try:
            clip = VideoFileClip(video_path)

            def adjust_contrast_exposure(frame):
                img = Image.fromarray(frame)
                img = ImageEnhance.Contrast(img).enhance(1.1)
                img = ImageEnhance.Brightness(img).enhance(1.05)
                return np.array(img)

            clip = clip.fl_image(adjust_contrast_exposure).fx(vfx.speedx, 1.1)

            def adjust_color(frame):
                img = Image.fromarray(frame)
                img = ImageEnhance.Color(img).enhance(1.2)
                return np.array(img)

            clip = clip.fl_image(adjust_color)

            image = (
                ImageClip("image.png")
                .set_duration(clip.duration)
                .resize(height=100)
                .set_pos(("right", "bottom"))
            )
            final_clip = CompositeVideoClip([clip, image])
            final_clip.write_videofile(output_path, codec='libx264', logger=None)

            console.print(f"[green]Видео уникализировано: {output_path}[/green]")
            return output_path
        except Exception as e:
            console.print(f"[bold red]Ошибка обработки {video_path}: {e}[/bold red]")
            return None

    def unique_description(self, description: str) -> str:
        if not description:
            return "😊"

        description = description.title()
        emojis = ["😊", "🌟", "🔥", "🎉", "💡", "✨", "🚀", "💎"]
        description += f" {random.choice(emojis)}"

        console.print(f"Описание уникализировано: {description}")
        return description

    def uniqueize_all_videos(self):
        if not os.path.exists(self.video_dir):
            console.print(f"[bold red]Директория {self.video_dir} не найдена![/bold red]")
            return

        video_files = [os.path.join(self.video_dir, f) for f in os.listdir(self.video_dir) if f.endswith('.mp4')]

        if not video_files:
            console.print("[yellow]Нет видео для обработки.[/yellow]")
            return

        console.print(f"[yellow]Начинаем обработку {len(video_files)} видео...[/yellow]")

        with ProcessPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(self.unique_video, video_files))

        console.print(f"[green]Обработка завершена. Уникализировано {sum(1 for r in results if r)} видео.[/green]")

    def _main(self) -> None:
        self.uniqueize_all_videos()
