import time
import uuid
from timeit import timeit
import sys

import paho.mqtt.client as mqttc

TOPIC = "benchmark/test"


def get_mqtt_client():
    client = mqttc.Client(client_id="benchmark_publisher",
                          clean_session=True,
                          transport="tcp")
    client.username_pw_set(username="SERVER_PUBLISHER", password='-')

    def on_publish(this_client: mqttc.Client, userdata, mid):
        print(f"mid: {mid}")

    client.on_publish = on_publish

    print("connecting to broker")
    client.connect(host="127.0.0.1", port=2083)
    client.loop_start()

    return client


def payload_factory(number: int):
    def payload():
        payload.remained -= 1
        if payload.remained == 0:
            return "benchmark_end"
        return str(uuid.uuid4())

    payload.remained = number
    return payload


def publish(client: mqttc.Client, payload_gen):
    payload = payload_gen()
    result = client.publish(TOPIC, payload=payload, qos=2)
    status = result[0]
    if status == 0:
        print(f"send `{payload}` to topic `{TOPIC}`")
    else:
        print("something failed while send")


def publish_x_times(number: int):
    client = get_mqtt_client()
    payload_gen = payload_factory(number)
    result_time = timeit(
        lambda: publish(client, payload_gen),
        number=number
    )
    # for i in range(number):
    #     publish(client, payload_gen)
    # result_time = 1
    time.sleep(5)
    client.disconnect()
    return result_time


def main():
    assert len(sys.argv) == 2, "Usage: python publisher.py <PUBLICATIONS_NUM>"
    assert (num := sys.argv[1]).isdigit(), "PUBLICATIONS_NUM should be digit"
    num = int(num)

    print(f"starting publisher (PUBLICATIONS_NUM = {num})")
    result_time = publish_x_times(num)
    print(f"{num}x publications were done in {result_time} seconds")
    print(f"=> {num / result_time} pubs per second")


if __name__ == '__main__':
    main()
