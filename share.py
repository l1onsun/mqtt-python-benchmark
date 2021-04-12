import time
import paho.mqtt.client as mqttc
import colorlog

TOPIC = "benchmark"
BENCHMARK_END_WORD = "benchmark_end"


def get_client(username: str):
    client = mqttc.Client(client_id=username,
                          clean_session=True,
                          transport="tcp")
    client.username_pw_set(username=username, password='-')
    return client


def get_logger(name: str):
    logger = colorlog.getLogger(name)
    logger.setLevel("DEBUG")

    handler = colorlog.StreamHandler()
    handler.setFormatter(
        colorlog.ColoredFormatter(
            "%(purple)s%(asctime)s[%(process)d] %(log_color)s%(levelname)s %(blue)s%(name)s: %(log_color)s%(message)s"
        )
    )
    logger.addHandler(handler)
    return logger


class Counter:
    def __init__(self):
        self.counts = 0
        self.first_count_time = None

    def count(self):
        if not self.first_count_time:
            self.first_count_time = time.time()
        self.counts += 1

    def get_counts_per_second(self):
        duration = time.time() - self.first_count_time
        return self.counts / duration
