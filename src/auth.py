import os
import sys
from typing import Dict
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
from console import console


class AuthManager:
    def __init__(self, config: Dict):
        self.client = Client()
        self.config = config
        self.session_file = 'session.json'
        self.client.delay_range = [3, 5]

        if self.config.get('proxy'):
            proxy_url = self.config['proxy']
            self.client.set_proxy(proxy_url)

        console.print(
            f"Прокси: {'активен' if self.config.get('proxy') else 'отсутствует'}"
        )

    def load_session(self, session_file: str = 'session.json') -> bool:
        try:
            if os.path.exists(session_file):
                session = self.client.load_settings(session_file)
                console.print("[green]Сессия успешно загружена из файла[/]")
                return session
            console.print("[yellow]Файл сессии не найден. Попробуем авторизацию через логин/пароль.[/]")
            return False
        except Exception as e:
            console.print(f"[red]Ошибка при загрузке сессии:[/] {str(e)}")
            return False

    def login(self) -> bool:
        session = self.load_session(self.session_file)
        login_via_session = False
        login_via_pw = False

        if session:
            try:
                self.client.set_settings(session)
                self.client.login(self.config['username'], self.config['password'])
                console.print(f"Авторизация прошла успешно: {self.config['username']}", style="bold blue")
                try:
                    self.client.get_timeline_feed()
                except LoginRequired:
                    old_session = self.client.get_settings()
                    self.client.set_settings({})
                    self.client.set_uuids(old_session["uuids"])
                    self.client.login(self.config['username'], self.config['password'])
                login_via_session = True

            except ChallengeRequired:
                console.print("[red]Необходимо подтверждение через СМС для аккаунта[/]")
                sys.exit(1)
                return
            except ConnectionError:
                console.print("[red]Прокси не валидные[/]")
                sys.exit(1)
                return
            except Exception as e:
                if "Failed to parse" in str(e):
                    console.print("[red]Прокси не валидные. Пожалуйста, проверьте настройки[/]")
                    sys.exit(1)
                elif "waif" in str(e):
                    console.print("[yellow]Подождите несколько минут и попробуйте снова[/]")
                    sys.exit(1)
                elif "submit_phone" in str(e):
                    console.print("[red]Нужно подтверждение по смс[/]")
                    sys.exit(1)
                console.print(f"[red]Ошибка при авторизации:{e}[/]")
                return False

        if not login_via_session:
            try:
                console.print("[yellow]Попытка входа через логин и пароль...[/]")
                if self.client.login(self.config['username'], self.config['password']):
                    login_via_pw = True
                    self.client.dump_settings(self.session_file)
                    console.print(f"[green]Успешный вход через логин/пароль:[/] {self.config['username']}")
            except ConnectionError:
                console.print("[red]Прокси не валидные[/]")
                sys.exit(1)
                return
            except Exception as e:
                if "ConnectionError" in str(e):
                    console.print("[red]Прокси не валидные[/]")
                    sys.exit(1)
                    return
                console.print(f"[red]Ошибка при входе через логин и пароль:[/] {e}")

        if not login_via_pw and not login_via_session:
            console.print("[red]Не удалось авторизоваться ни через сессию, ни через логин/пароль[/]")
            raise Exception("Couldn't login user with either password or session")

        return True

    def logout(self) -> None:
        try:
            self.client.logout()
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            console.print("[green]Выход из аккаунта выполнен успешно и файл сессии удален.[/]")
        except Exception as e:
            console.print(f"[red]Ошибка при выходе из аккаунта:[/] {e}")
