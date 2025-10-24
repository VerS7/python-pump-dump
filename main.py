# PUMP AND DUMP LISTENER

import asyncio
from typing import Any, Coroutine
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

from pyrogram import Client

# Доступ к Telegram API telegram
# Подробнее https://developers.google.com/workspace/sheets/api/quickstart/python?hl=ru
API_ID: int = 0
API_HASH: str = "..."

# Искомый канал https://t.me/pump_scr
CHANNEL: str = "@pump_scr"

# Файл с ключами от Google API
# Подробнее https://console.cloud.google.com/
CREDENTIALS_FILE = "credentials.json"

# Ссылка на Google Sheets таблицу
SPREADSHEET_URL = "..."

# Настройки авторизации Google API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Задержка прослушивания канала (в секундах)
LISTEN_DELAY: int = 5
# Задержка перед удалением данных в таблице (в секундах)
CLEANUP_DELAY: int = 10

# Метка искомого сообщения (пример: "🟢 CUDIS Bybit...")
MARK: str = "🟢"

# Суффикс для вставки в таблицу (пример: "CUDISUSDT.P")
SUFFIX: str = "USDT.P"

# Включить/выключить логгер
LOGGING: bool = True

# Telegram API client
telegram = Client(
    "PUMP_DUMP_LISTENER",
    api_id=API_ID,
    api_hash=API_HASH,
)

# Google API client
google = gspread.authorize(
    Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
)

# Таблица
spreadsheet = google.open_by_url(SPREADSHEET_URL)
# Лист
worksheet = spreadsheet.sheet1


def log(*message: Any) -> None:
    """Логгирует если включен логгер"""
    if not LOGGING:
        return

    dt = datetime.now()

    print(f"[{dt.strftime('%H:%M:%S %d.%m')}] ", *message)


def format_message(message: str) -> str:
    """Форматирует сообщение с суффиксом"""
    parts = message.split("\n")
    name = parts[0].split()[1]

    return name + SUFFIX


async def write_to_table(data: str):
    """Записывает данные в ячейку A1 в таблице"""
    loop = telegram.loop

    await loop.run_in_executor(None, worksheet.update, "A1", [[data]])


class TaskManager:
    def __init__(self):
        self._task: asyncio.Task | None = None
        self.scheduled: bool = False

    async def schedule(self, task: Coroutine):
        self._task = asyncio.create_task(task)
        self.scheduled = True

        try:
            await self._task
        except asyncio.CancelledError:
            pass

        self.scheduled = False
        self._task = None

    def cancel(self):
        if self._task:
            self._task.cancel()
            self.scheduled = False


async def main():
    log("Запуск скрипта...")

    last_message: str | None = None

    task_manager = TaskManager()

    async def write_with_delayed_remove(data: str):
        await write_to_table(data)
        await asyncio.sleep(CLEANUP_DELAY)
        await write_to_table("")

    async with telegram:
        while True:
            try:
                # Слушаем канал
                async for message in telegram.get_chat_history(CHANNEL, limit=1):
                    text = message.text

                    # Если метки нет в сообщении - пропускаем
                    if MARK not in text:
                        continue

                    # Если сообщение не новое - пропускаем
                    if last_message == text:
                        continue

                    last_message = text

                    match_text = text.replace("\n", " ")[0:15]
                    log(f'Найдено в "{match_text}..."!')

                    formatted_message = format_message(text)

                    if task_manager.scheduled:
                        log("Запланирована запись. Отменяем...")
                        task_manager.cancel()

                    log("Записываем в google-таблицу...")
                    await task_manager.schedule(
                        write_with_delayed_remove(formatted_message)
                    )

            except Exception as e:
                log(e)

            await asyncio.sleep(LISTEN_DELAY)


if __name__ == "__main__":
    telegram.run(main())
