import logging
import sys
import os


class CustomFormatter(logging.Formatter):
    
    grey = "\x1b[38;20m"
    green = "\x1b[32;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format_str + reset,
        logging.INFO: green + format_str + reset,
        logging.WARNING: yellow + format_str + reset,
        logging.ERROR: red + format_str + reset,
        logging.CRITICAL: bold_red + format_str + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logger():
    #log klasoru yoksa olustur
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger('discord_bot')
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(CustomFormatter())
    fh = logging.FileHandler('logs/bot.log', encoding='utf-8')
    fh.setLevel(logging.INFO)
    fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(ch)
    logger.addHandler(fh)
    
    return logger

#global log degiskeni
log = setup_logger()

#yardimci fonksiyonlar
def calculate_xp_for_level(level):
    
    #bunlar degisebilir çünkü ne kadar xp doğru olur iblmiyorum
    if level < 0: return 0
    return 5 * (level ** 2) + 50 * level + 100

def parse_duration(time_str):
    
    if not time_str: return -1
    
    unit = time_str[-1].lower()
    value = time_str[:-1]

    if not value.isdigit():
        return -1
    
    value = int(value)

    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400
    else:
        #eger birim yoksa ve hepsi sayiysa saniye kabul edelim
        if time_str.isdigit():
            return int(time_str)
        return -1
