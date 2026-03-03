import json
import logging

def log_dict(logger: logging.Logger, d: dict, level="info"):
    #Выводит словарь в лог по строчкам
    text = json.dumps(d, indent=2, ensure_ascii=False)
    getattr(logger, level)(f"\n{text}")