import sys
import time
import uuid
from multiprocessing import Process

from share import BENCHMARK_END_WORD, TOPIC, Counter, get_client, get_logger


class Publisher(Process):
    def __init__(self, index: int, number: int):
        super().__init__()
        self.name = f"benchmark_publisher_{index}"
        self.number = number
        self.logger = get_logger(self.name)
        self.client = get_client(self.name)
        self.client.on_publish = lambda c, u, m: self.on_publish()
        self.send_counter = Counter()
        self.approved_counter = Counter()

    def run(self) -> None:
        self.logger.info(f"starting publisher ({self.name})")
        self.client.connect(host="127.0.0.1", port=2083)
        self.logger.info(f"loop started ({self.number})")
        self.client.loop_start()
        for _ in range(self.number - 1):
            payload = str(uuid.uuid4())
            self.publish(payload)
            time.sleep(0.01)
        self.publish(BENCHMARK_END_WORD)
        time.sleep(3)
        self.client.loop_stop()

    def complete(self):
        cps = self.approved_counter.get_counts_per_second()
        self.logger.info("benchmark complete")
        self.logger.info(f"send {cps} msgs per second")
        self.client.disconnect()

    def on_publish(self):
        self.approved_counter.count()
        self.logger.info(f"msg send approve {self.approved_counter.counts}/{self.number}")
        if self.approved_counter.counts >= self.number:
            self.complete()

    def publish(self, payload: str):
        self.send_counter.count()
        status = self.client.publish(TOPIC, payload=payload, qos=2)[0]
        if status != 0:
            self.logger.error(f"publish field (status: {status})")


def parse_args_and_run():
    assert len(sys.argv) in (2, 3), "Usage: python publisher.py <PUBLICATIONS_NUM> [PROCESS_NUM]"
    assert sys.argv[1].isdigit(), "PUBLICATIONS_NUM should be digit"
    num = int(sys.argv[1])
    process_num = 1
    if len(sys.argv) >= 3:
        assert sys.argv[2].isdigit(), "PROCESS_NUM should be digit"
        process_num = int(sys.argv[2])

    processes = [Publisher(i, num) for i in range(process_num)]
    [p.start() for p in processes]
    [p.join() for p in processes]


if __name__ == '__main__':
    parse_args_and_run()
