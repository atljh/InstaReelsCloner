import logging

logging.SUCCESS = 25
logging.addLevelName(logging.SUCCESS, 'SUCCESS')


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(logging.SUCCESS):
        self._log(logging.SUCCESS, message, args, **kwargs)


logging.Logger.success = success


class CustomFormatter(logging.Formatter):

    FORMATS = {
        logging.INFO: "[%(asctime)s] %(message)s",
        logging.WARNING: "[%(asctime)s] ⚠️ %(message)s",
        logging.ERROR: "[%(asctime)s] ❌ ОШИБКА: %(message)s",
        logging.SUCCESS: "[%(asctime)s] ✅ %(message)s",
    }

    def format(self, record):
        """Форматирует лог-запись в зависимости от уровня."""
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logger(name: str = "ReelsCloner", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())

    logger.addHandler(handler)

    return logger
