from flask import Flask, request
from pykafka import KafkaClient
import json
 
app = Flask(__name__)
 
def get_kafka_client():
    return KafkaClient(hosts='localhost:9092')
 
@app.route('/v1/<topic>', methods=['POST'])
def write_to_topic(topic):
    data = request.get_json()
    client = get_kafka_client()
    topic = client.topics[topic.encode('ascii')]
    producer = topic.get_sync_producer()
    producer.produce(json.dumps(data).encode())
 
    return 'OK'
 
if __name__ == '__main__':
    app.run(debug=True, host='172.30.5.111', port=80)
