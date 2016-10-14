import sys

from pyspark import SparkContext, SparkConf
from petrarch2 import EventCoder
from _functools import partial
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
    
    
    
    
    lines = ['{ "type" : "story", "doc_id" : "nytasiapacific20160622.0002", "head_line" : "Lightning Ridge Journal: An Amateur Undertaking in Australian Mining Town With No Funeral Home", "date_line" : "Tue, 21 Jun 2016 03:52:15 GMT", "sentences" : {"array":[ { "sentence_id" : 1, "sentence" : "A Tunisian court has jailed a Nigerian student for two years for helping young militants join an armed Islamic group in Lebanon, his lawyer said Wednesday.", "parse_sentence" : "(ROOT (S (S (NP (DT A) (NNP Tunisian) (NN court)) (VP (VBZ has) (VP (VBN jailed) (NP (DT a) (NNP Nigerian) (NN student)) (PP (IN for) (NP (NP (CD two) (NNS years)) (PP (IN for) (S (VP (VBG helping) (S (NP (JJ young) (NNS militants)) (VP (VB join) (NP (DT an) (JJ armed) (JJ Islamic) (NN group)) (PP (IN in) (NP (NNP Lebanon))))))))))))) (, ,) (NP (PRP$ his) (NN lawyer)) (VP (VBD said) (NP (NNP Wednesday))) (. .)))" } ]}, "corref" : "" }']
        
    linesRDD = sc.parallelize(lines)
 
    events_rdd = linesRDD.map(map_articles)
    
    events_rdd = events_rdd.map(print_each)
    
    events_rdd = events_rdd.map(partial(code_articles, petrGlobals=bMap.value))
    
    events_rdd = events_rdd.map(print_each)
    
    result = events_rdd.collect()
    
    print(result)
    
    
  
  
