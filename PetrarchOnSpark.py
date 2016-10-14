import sys

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
from petrarch2 import EventCoder
from _functools import partial
from datetime import datetime
#from CameoEventCoder import CameoEventCoder 

def map_articles(articleText):
    return articleText.encode('utf-8')
    

def code_articles(articleText, petrGlobals={}): 
    coder = EventCoder(petrGlobal = petrGlobals)
    events_map = coder.encode(articleText)
    return str(events_map)

def print_each(x):
    print x
    return x



if __name__ == "__main__":
    
  # create Spark context with Spark configuration
    conf = SparkConf().setAppName("Spark Petrarch2")
    sc = SparkContext(conf=conf)
    
    coder = EventCoder(petrGlobal={})
    
    bMap = sc.broadcast(coder.get_PETRGlobals())
    print(bMap.__class__)
    #sc.addPyFile("dist/petrarch2-1.0.0-py2.7.egg")
    #encoderBroadcast = sc.broadcast(CameoEventCoder())
    ssc = StreamingContext(sc, 120)
    kafkaStream = KafkaUtils.createStream(ssc=ssc,
                                        zkQuorum='dmlhdpc1',
                                        groupId='dmlhdpc1',
                                        topics={'petrarch':1})
  
 
    lines = kafkaStream.map(lambda x: x[1])
    events_rdd = lines.map(map_articles)
    events_rdd.pprint(1)
    events_rdd = events_rdd.map(partial(code_articles, petrGlobals = bMap.value))
    events_rdd.pprint(1)
    
    events_rdd.foreachRDD(lambda x: x.saveAsTextFile("hdfs://dmlhdpc10:9000/Events_SPEC"+ datetime.strftime(datetime.now(), "%Y%m%d_%I%M%S")))
    #events_rdd.saveAsTextFiles("hdfs://dmlhdpc10:9000/Events_SPEC", "OUT")

    ssc.start()
    ssc.awaitTermination()
  
  
