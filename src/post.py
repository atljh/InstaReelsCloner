from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
from console import console


class PostManager:
    def __init__(self, client: Client):
        self.client = client

    def post_video(self, video_path: str, description: str) -> bool:
        try:
            self.client.relogin()
            self.client.clip_upload(
                video_path,
                caption=description,
                thumbnail=None,
                location=None,
                extra_data={}
            )
            console.print(f"[green]Видео загружено | Путь: {video_path}[/]")
            return True

        except LoginRequired:
            console.print("[red]Ошибка: требуется повторная авторизация.[/]")
            return False
        except ChallengeRequired:
            console.print("[red]Ошибка: требуется подтверждение аккаунта (например, через SMS).[/]")
            return False
        except IndexError:
            return False
        except Exception as e:
            console.print(f"[red]Ошибка при публикации видео: {str(e)}[/]")
            if hasattr(e, 'response') and e.response is not None:
                console.print(f"[red]Ответ Instagram: {e.response.json()}[/]")
            return False
