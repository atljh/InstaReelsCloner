import yaml
import sys
import logging
from typing import List, Dict

logger = logging.getLogger("ReelsCloner")


def load_config(config_file: str = 'config.yaml') -> Dict:
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        logger.error(f"Конфигурационный файл '{config_file}' не найден.")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Ошибка при чтении YAML-файла: {e}")
        sys.exit(1)


def load_usernames(usernames_file: str = 'usernames.txt') -> List[str]:
    usernames = []
    try:
        with open(usernames_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    usernames.append(line)
        if not len(usernames):
            logger.warning("Ключевые слова не найдены")
            sys.exit(1)
        logger.success(f"Загружено {len(usernames)} аккаунтов для мониторинга")
        return usernames
    except FileNotFoundError:
        logger.error(f"Файл {usernames_file} не найден")
        sys.exit(1)
