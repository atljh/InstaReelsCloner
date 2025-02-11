import yaml
import sys
from typing import List, Dict
from tools.console import console


def load_config(config_file: str = 'config.yaml') -> Dict:
    try:
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        console.print(f"[red]Конфигурационный файл '{config_file}' не найден.[/]")
        sys.exit(1)
    except yaml.YAMLError as e:
        console.print(f"[red]Ошибка при чтении YAML-файла: {e}[red]")
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
            console.print("[red]Аккаунты не найдены[/]")
            sys.exit(1)
        console.print(f"Загружено {len(usernames)} аккаунтов для мониторинга")
        return usernames
    except FileNotFoundError:
        console.print(f"[red]Файл {usernames_file} не найден[/]")
        sys.exit(1)
