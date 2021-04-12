import sys

import paho.mqtt.client as mqtt

from share import BENCHMARK_END_WORD, TOPIC, Counter, get_client, get_logger

logger = get_logger("benchmark_subscriber")


class Subscriber:
    def __init__(self):
        self.client = get_client("benchmark_subscriber")
        self.counter = Counter()
        self.client.on_connect = lambda c, u, f, r: Subscriber.on_connect(self, r)
        self.client.on_message = lambda c, u, m: Subscriber.on_message(self, m)

    def start(self):
        logger.info("connecting to broker")
        self.client.connect(host="127.0.0.1", port=2083)

        logger.info("start loop")
        self.client.loop_forever()

    def complete(self):
        cps = self.counter.get_counts_per_second()
        logger.info("benchmark complete")
        logger.info(f"received {cps} msgs per second")
        self.client.disconnect()

    def on_connect(self, rc: int):
        if rc == 0:
            logger.info(f"successfully connected to broker (result code: {rc})")
            self.client.subscribe(TOPIC, qos=2)
            logger.info(f"subscribed to {TOPIC}")
        else:
            logger.error(f"connection failed (result code: {rc})")
            self.client.disconnect()
            sys.exit()

    def on_message(self, msg: mqtt.MQTTMessage):
        logger.info(f"received message: {msg.payload}")
        self.counter.count()
        if msg.payload.decode() == BENCHMARK_END_WORD:
            self.complete()


if __name__ == '__main__':
    Subscriber().start()
