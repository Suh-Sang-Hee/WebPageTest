from kafka import KafkaConsumer
import json
 
consumer = KafkaConsumer('syntheticTest',   # Topic 이름
    bootstrap_servers = 'localhost:9092',   # <Zookeeper-Host> : <port>
    group_id = 'mygroup',
    auto_offset_reset = 'earliest',
    consumer_timeout_ms = 1000,
    value_deserializer = json.loads)	# msg 불러올 형식 지정
 
for msg in consumer:
    print(msg.value)
