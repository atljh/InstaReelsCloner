import os
import numpy as np
from typing import Dict
from concurrent.futures import ProcessPoolExecutor
from PIL import ImageEnhance, Image
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, vfx
from console import console


class UniqueManager:
    def __init__(self, config: Dict):
        self.config = config
        self.video_dir = config.get('download_folder', 'downloads/videos')
        self.output_dir = config.get('output_folder', 'downloads/unique_videos')

        self.contrast_factor = config.get('contrast_factor', 1.1)
        self.brightness_factor = config.get('brightness_factor', 1.05)
        self.speed_factor = config.get('speed_factor', 1.1)
        self.color_factor = config.get('color_factor', 1.2)
        self.image_name = config.get('image_name', 'image.png')

        os.makedirs(self.output_dir, exist_ok=True)

    def unique_video(self, video_path: str) -> str:
        if not os.path.exists(video_path):
            console.print(f"[bold red]Файл {video_path} не найден![/bold red]")
            return None

        file_name = os.path.basename(video_path)
        output_path = os.path.join(self.output_dir, file_name)

        try:
            # Trying to get first frame
            with VideoFileClip(video_path) as test_clip:
                test_clip.get_frame(0)

            clip = VideoFileClip(video_path)

            def adjust_contrast_exposure(frame):
                img = Image.fromarray(frame)
                img = ImageEnhance.Contrast(img).enhance(self.contrast_factor)
                img = ImageEnhance.Brightness(img).enhance(self.brightness_factor)
                return np.array(img)

            clip = clip.fl_image(adjust_contrast_exposure).fx(vfx.speedx, self.speed_factor)

            def adjust_color(frame):
                img = Image.fromarray(frame)
                img = ImageEnhance.Color(img).enhance(self.color_factor)
                return np.array(img)

            clip = clip.fl_image(adjust_color)

            if os.path.exists(self.image_name):
                image = (
                    ImageClip(self.image_name)
                    .set_duration(clip.duration)
                    .resize(width=clip.w, height=clip.h)
                    .set_pos("center")
                )
                final_clip = CompositeVideoClip([clip, image])
            else:
                console.print(f"[yellow]Изображение для наложения {self.image_name} не найдено. Наложение пропущено.[/yellow]")
                final_clip = clip

            final_clip.write_videofile(output_path, codec='libx264', logger=None)

            console.print(f"Видео уникализировано: {output_path}")
            return output_path

        except IndexError:
            console.print(f"[bold red]Ошибка: видео {video_path} повреждено или пустое.[/bold red]")
        except OSError:
            console.print(f"[bold red]Видео повреждено: {video_path}. [/bold red]")
        except Exception as e:
            if "error" in str(e):
                console.print(f"[bold red]Ошибка: видео {video_path} повреждено или пустое.[/bold red]")
            console.print(f"[bold red]Ошибка: видео {video_path} повреждено или пустое.[/bold red]")
        return None

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

    def _main(self):
        self.uniqueize_all_videos()
