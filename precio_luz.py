import os
import logging
from datetime import datetime, date
from abc import ABC, abstractmethod

import holidays
import telebot


# ==========================================
# Domain Layer
# ==========================================

class HolidayProvider(ABC):
    """Abstract holiday provider (D - Dependency Inversion)"""

    @abstractmethod
    def is_holiday(self, day: date) -> bool:
        pass


class SpainHolidayProvider(HolidayProvider):
    """Concrete Spain holiday implementation"""

    def __init__(self):
        self._holidays = holidays.Spain()

    def is_holiday(self, day: date) -> bool:
        return day in self._holidays


class ElectricityPeriodCalculator:
    """Single responsibility: determine electricity period"""

    VALLE = "Hora Valle (la más barata)"
    LLANO = "Hora Llano (precio intermedio)"
    PUNTA = "Hora Punta (la más cara)"

    def __init__(self, holiday_provider: HolidayProvider):
        self._holiday_provider = holiday_provider

    def calculate(self, now: datetime) -> str:
        hour = now.hour
        weekday = now.weekday()

        # Weekend or holiday → always VALLE
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
    """Single responsibility: build Spanish output message"""

    @staticmethod
    def format(period: str) -> str:
        return (
            f"⚡ Estás en {period}."
        )


# ==========================================
# Infrastructure Layer
# ==========================================

class Notifier(ABC):
    """Abstract notification service (O + D)"""

    @abstractmethod
    def send(self, message: str) -> None:
        pass


class TelegramNotifier(Notifier):
    """Telegram implementation"""

    def __init__(self):
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self._chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self._bot = telebot.TeleBot(bot_token)

    def send(self, message: str) -> None:
        if not message:
            return
        try:
            self._bot.send_message(self._chat_id, message)
            logging.info("Telegram message sent successfully.")
        except Exception as e:
            logging.error(f"Failed to send Telegram message: {e}")


# ==========================================
# Application Layer
# ==========================================

class ElectricityNotificationService:
    """Orchestrates the process (SRP: coordination only)"""

    def __init__(
        self,
        calculator: ElectricityPeriodCalculator,
        notifier: Notifier,
        formatter: MessageFormatter,
    ):
        self._calculator = calculator
        self._notifier = notifier
        self._formatter = formatter

    def run(self) -> None:
        now = datetime.now()
        period = self._calculator.calculate(now)
        message = self._formatter.format(period)

        print(message)
        self._notifier.send(message)


# ==========================================
# Entry Point
# ==========================================

def main():
    holiday_provider = SpainHolidayProvider()
    calculator = ElectricityPeriodCalculator(holiday_provider)
    notifier = TelegramNotifier()
    formatter = MessageFormatter()

    service = ElectricityNotificationService(
        calculator=calculator,
        notifier=notifier,
        formatter=formatter,
    )

    service.run()


if __name__ == "__main__":
    main()
