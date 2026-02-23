import os
import logging
from datetime import datetime, date
from abc import ABC, abstractmethod
from pathlib import Path

import holidays
import telebot


# ==========================================
# Domain Layer
# ==========================================

class HolidayProvider(ABC):
    @abstractmethod
    def is_holiday(self, day: date) -> bool:
        pass


class SpainHolidayProvider(HolidayProvider):
    def __init__(self):
        self._holidays = holidays.Spain()

    def is_holiday(self, day: date) -> bool:
        return day in self._holidays


class ElectricityPeriodCalculator:
    VALLE = "Hora Valle (la más barata)"
    LLANO = "Hora Llano (precio intermedio)"
    PUNTA = "Hora Punta (la más cara)"

    def __init__(self, holiday_provider: HolidayProvider):
        self._holiday_provider = holiday_provider

    def calculate(self, now: datetime) -> str:
        hour = now.hour
        weekday = now.weekday()

        if weekday >= 5 or self._holiday_provider.is_holiday(now.date()):
            return self.VALLE

        if 0 <= hour < 8:
            return self.VALLE
        elif 8 <= hour < 10 or 14 <= hour < 18 or 22 <= hour < 24:
            return self.LLANO
        elif 10 <= hour < 14 or 18 <= hour < 22:
            return self.PUNTA

        return "Periodo desconocido"


class MessageFormatter:
    @staticmethod
    def format(now: datetime, period: str) -> str:
        return (
            f"Estás en {period}."
        )


# ==========================================
# Infrastructure Layer
# ==========================================

class Notifier(ABC):
    @abstractmethod
    def send(self, message: str) -> None:
        pass


class TelegramNotifier(Notifier):
    def __init__(self):
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self._chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self._bot = telebot.TeleBot(bot_token)

    def send(self, message: str) -> None:
        if not message:
            return
        try:
            self._bot.send_message(self._chat_id, message)
            logging.info("Telegram message sent.")
        except Exception as e:
            logging.error(f"Telegram error: {e}")


class OutputStateRepository:
    """
    Responsible only for persisting last output.
    """

    def __init__(self, file_path: str = "last_output.txt"):
        self._file = Path(file_path)

    def get_last_output(self) -> str | None:
        if not self._file.exists():
            return None
        return self._file.read_text().strip()

    def save_output(self, message: str) -> None:
        self._file.write_text(message)


# ==========================================
# Application Layer
# ==========================================

class ElectricityNotificationService:
    def __init__(
        self,
        calculator: ElectricityPeriodCalculator,
        notifier: Notifier,
        formatter: MessageFormatter,
        state_repository: OutputStateRepository,
    ):
        self._calculator = calculator
        self._notifier = notifier
        self._formatter = formatter
        self._state_repository = state_repository

    def run(self) -> None:
        now = datetime.now()
        period = self._calculator.calculate(now)
        message = self._formatter.format(now, period)

        print(message)

        last_message = self._state_repository.get_last_output()

        if message != last_message:
            self._notifier.send(message)
            self._state_repository.save_output(message)
        else:
            logging.info("Message unchanged. Telegram not sent.")


# ==========================================
# Entry Point
# ==========================================

def main():
    holiday_provider = SpainHolidayProvider()
    calculator = ElectricityPeriodCalculator(holiday_provider)
    notifier = TelegramNotifier()
    formatter = MessageFormatter()
    state_repository = OutputStateRepository()

    service = ElectricityNotificationService(
        calculator,
        notifier,
        formatter,
        state_repository,
    )

    service.run()


if __name__ == "__main__":
    main()
