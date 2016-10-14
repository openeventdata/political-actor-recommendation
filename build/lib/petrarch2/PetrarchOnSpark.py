import sys

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import EventCoder
#from EventCoder import EventCoder 

def code_articles(articleText):
    
    coder = EventCoder()
    print articleText.encode('utf-8')
    events_map = coder.encode(articleText.encode('utf-8'))
    print events_map
    return str(events_map)

if __name__ == "__main__":
    
  # create Spark context with Spark configuration
    conf = SparkConf().setAppName("Spark Petrarch2")
    sc = SparkContext(conf=conf)
    
    #sc.addPyFile("dist/petrarch2-1.0.0-py2.7.egg")
    #encoderBroadcast = sc.broadcast(EventCoder())
    ssc = StreamingContext(sc, 120)
    kafkaStream = KafkaUtils.createStream(ssc=ssc,
                                        zkQuorum='dmlhdpc1',
                                        groupId='dmlhdpc1',
                                        topics={'petrarch':1})
  
 
    lines = kafkaStream.map(lambda x: x[1])
    events_rdd = lines.map(code_articles)
    
    events_rdd.saveAsTextFiles("TEST", "OUT")

    ssc.start()
    ssc.awaitTermination()
  
  
