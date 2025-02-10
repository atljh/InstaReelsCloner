from src.managers import AuthManager, DownloadManager, UniqueManager
from console import console


class ReelsCloner:
    def __init__(self, config: dict, username: str):
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
        download_res = await self.download_manager._main(self.username)
        if not download_res:
            return False
        console.print("Скачивание завершено")
        return True

    async def uniqueize_videos(self) -> None:
        self.unique_manager._main()

    async def start(self) -> None:
        login_res = await self._login()
        if not login_res:
            return
        result = await self.download_videos()
        await self._logout()
        if not result:
            return
        if not self.config.get("uniqueize", False):
            return
        console.print("[green]Уникализация видео...[/]")
        await self.uniqueize_videos()
