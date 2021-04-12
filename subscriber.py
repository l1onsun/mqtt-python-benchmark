import sys
import time

import paho.mqtt.client as mqttc

TOPIC = "benchmark/test"


class InputCounter:
    def __init__(self):
        self.counts = 0
        self.first_message_time = None

    def count(self):
        if not self.first_message_time:
            self.first_message_time = time.time()
        self.counts += 1

    def print_results(self):
        benchmark_duration = time.time() - self.first_message_time
        print(f"benchmark duration: {benchmark_duration} seconds")
        print(f"message received: {self.counts}")
        print(f"=> {self.counts / benchmark_duration} msgs per second")


def listen_mqtt():
    client = mqttc.Client(client_id="benchmark_subscriber",
                          clean_session=True,
                          transport="tcp")
    client.username_pw_set(username="SERVER_SUBSCRIBER", password='-')

    def on_connect(this_client: mqttc.Client, _userdata, _flags, rc: int):
        print(f"connected to broker (result code: {rc})")
        this_client.subscribe(TOPIC, qos=2)
        print(f"subscribed to {TOPIC}")

    client.on_connect = on_connect

    input_counter = InputCounter()

    def on_message(this_client: mqttc.Client, _userdata, msg: mqttc.MQTTMessage):
        print(f"message_received {msg.payload}")
        input_counter.count()
        if msg.payload.decode() == "benchmark_end":
            print("received benchmark_end, ending benchmark")
            input_counter.print_results()
            this_client.disconnect()
            sys.exit()

    client.on_message = on_message

    print("trying connect to broker")
    client.connect(host="127.0.0.1", port=2083)

    print("start loop")
    client.loop_forever()


if __name__ == '__main__':
    listen_mqtt()
