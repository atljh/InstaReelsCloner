import asyncio
from typing import Dict
from src.auth import AuthManager
from src.download import DownloadManager
from src.uniqueize import UniqueManager
from src.post import PostManager
from config import load_config, load_usernames
from logger import setup_logger

logger = setup_logger()


class ReelsCloner:
    def __init__(self, config: Dict):
        self.config = config
        self.auth_manager = AuthManager(config)
        self.download_manager = DownloadManager(self.auth_manager.client, config)
        self.unique_manager = UniqueManager(config)
        self.post_manager = PostManager(self.auth_manager.client)

    async def post_video(self, video_path: str, original_description: str):
        unique_desc = self.unique_manager.unique_description(original_description)
        await self.post_manager.post_video(video_path, unique_desc)

    def start(self):
        self.auth_manager.login()


async def main():
    config = load_config()
    cloner = ReelsCloner(config)
    cloner.start()

    usernames = load_usernames()


if __name__ == '__main__':
    asyncio.run(main())