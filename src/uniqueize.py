import os
import uuid
import random
import numpy as np
from typing import Dict
from PIL import ImageEnhance, Image
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, vfx
from console import console


class UniqueManager:
    def __init__(self, config: Dict):
        self.config = config

    def unique_video(self, video_path: str) -> str:
        if not os.path.exists(video_path):
            console.print(f"[bold red]Файл {video_path} не найден![/bold red]")
            raise FileNotFoundError(f"Файл {video_path} не найден!")

        unique_filename = str(uuid.uuid4()) + '.mp4'
        output_path = os.path.join(self.config['download_folder'], unique_filename)
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

        console.print(f"Видео уникализировано: {output_path}")
        return output_path

    def unique_description(self, description: str) -> str:
        if not description:
            return "😊"

        description = description.title()
        emojis = ["😊", "🌟", "🔥", "🎉", "💡", "✨", "🚀", "💎"]
        description += f" {random.choice(emojis)}"

        console.print(f"Описание уникализировано: {description}")
        return description

    def uniqueize_all_videos(self) -> None:
        video_dir = self.config.get('download_folder', 'downloads/videos')
        if not os.path.exists(video_dir):
            console.print(f"[bold red]Директория {video_dir} не найдена![/bold red]")
            return

        for video_file in os.listdir(video_dir):
            video_path = os.path.join(video_dir, video_file)
            if os.path.isfile(video_path) and video_file.endswith('.mp4'):
                console.print(f"[yellow]Уникализация видео: {video_file}[/yellow]")
                self.unique_video(video_path)

        console.print("[green]Все видео в директории уникализированы.[/green]")

    def _main(self) -> None:
        self.uniqueize_all_videos()
