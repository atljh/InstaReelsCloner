import os
import uuid
import random
import numpy as np
from typing import Dict
from PIL import ImageEnhance, Image
from moviepy.editor import VideoFileClip
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

        clip = clip.fl_image(adjust_contrast_exposure)
        clip.write_videofile(output_path, codec='libx264', logger=None)

        logger.info(f"Видео уникализировано: {output_path}")
        return output_path

    def unique_description(self, description: str) -> str:
        if not description:
            return "😊"

        description = description.title()
        emojis = ["😊", "🌟", "🔥", "🎉", "💡", "✨", "🚀", "💎"]
        description += f" {random.choice(emojis)}"

        logger.info(f"Описание уникализировано: {description}")
        return description
