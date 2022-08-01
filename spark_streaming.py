from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json
 
# local StreamingContext 생성
sc = SparkContext("local[*]", "spark_kafka_consumer_test")
ssc = StreamingContext(sc, 1)
 
brokers = "172.30.5.111:9092"   # kafka broker host : port
topics = "test" # topic_name
 
directKafkaStream = KafkaUtils.createDirectStream(ssc, [topics], {"metadata.broker.list": brokers}) 	# directKafkaStream --> kafka broker로 부터 데이터를 갖고오기 위해 생성 / receiver 존재X (return DStream)
 
values = directKafkaStream.map(lambda x: x[1])  	# dstream의 각각의 요소에 함수(lambda)를 적용하여 새로운 DStream을 생성 / type --> KafkaTransformedDStream
 
dstream = values.map(lambda value: value)       	# type --> TransformedDStream
 
dstream.pprint()
 
ssc.start()         	# Start the computation
ssc.awaitTermination()  # Wait for the computation to terminate
ssc.stop()
