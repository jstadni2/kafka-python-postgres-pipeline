from confluent_kafka import Consumer, cimpl
from typing import List

def consume_message(consumer_conf, new_topic, logger):
    consumer = Consumer(consumer_conf)

    def on_assignment_print(
        _consumer: cimpl.Consumer, _partitions: List[cimpl.TopicPartition]
    ):
        logger.info(f"Assignment: {_partitions}")

    consumer.subscribe(topics=[new_topic.topic], on_assign=on_assignment_print)
    consumed_message = consumer.poll()
    consumer.close()
    
    return consumed_message
    