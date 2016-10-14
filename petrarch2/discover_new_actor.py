import json
import pprint
import re
import sys
import os
from petrarch2 import PETRglobals
from ActorDictionaryCopy import ActorDictionary
reload(sys)
sys.setdefaultencoding('utf8')

pp = pprint.PrettyPrinter(indent=2)

discard_words_set = set(['THE', 'A', 'AN', 'OF', 'IN', 'AT', 'OUT', '', ' '])


from EventCoder import EventCoder

coder = EventCoder(petrGlobal={})

another_coder = EventCoder(petrGlobal=coder.get_PETRGlobals())
N = 10
new_actor_over_time = dict()



#input_file = open('/root/Desktop/core_nlp_out_large.txt') #open('/root/test_pet')
#input_file = open('/root/test_pet2')

from StringIO import StringIO


#folder_name = '/root/Desktop/files/'
#folder_name = '/root/Desktop/dataset/'
folder_name = '/root/Desktop/test1/'

actor_dict = ActorDictionary()


for input_file_name in sorted(os.listdir(folder_name)):
    print ('reading file: ' + input_file_name)

    input_file = open(folder_name + input_file_name)

    total_new_actor_list = []
    word_dic = dict()

    for line in input_file:

        print line
        print '==================='

        if not line.startswith('{'): #skip the null entries
            print 'Not a useful line'
            continue
        #pp.pprint(another_coder.encode(line))

        dict_event = another_coder.encode(line)
        if dict_event is None:
            continue

        new_actor_meta = dict()
        nouns = []


        for k in dict_event.keys():
            new_actor_meta['doc_id'] = k
            if 'sents' in dict_event[k]:
                if (dict_event[k]['sents'] is not None):
                    keys = dict_event[k]['sents'].keys()

                    if keys is not None:
                        for l in keys:
                            if 'meta' in dict_event[k]['sents'][l]:
                                nouns += dict_event[k]['sents'][l]['meta']['nouns_not_matched']

        new_actor_meta['new_actor'] = list(set(nouns))



        #print new_actor_meta

        new_actor_freq = dict()
        #new_actor_freq['doc_id'] = new_actor_meta['doc_id']


        total_count = 0
        for item in new_actor_meta['new_actor']:
            sentences = json.load(StringIO(line), encoding='utf-8')

            count = 0
            ner = set()
            for s in sentences['sentences']:
                #"(MONEY,$|48|million),(ORGANIZATION,United|Nations),(DATE,30|August|2016|today),(NUMBER,1.3|million),(LOCATION,Central|Africa|West|Central|Africa),(PERSON,WFP/Daouda|Guirou)"

                ner_text_list = ''

                if len(s['ner']) > 0:
                    for ner_item in s['ner'].replace('),(', ':').split(':'):
                        ner_item_list = ner_item.replace('(', '').replace(')', '').split(',')

                        if len(ner_item_list) != 2:
                            continue


                        if ner_item_list[0] == 'PERSON': # or ner_item_list[0] == 'MISC' or ner_item_list[0] == 'ORGANIZATION':
                            ner_text_list = ner_item_list[1]
                            ner = ner | set([x.strip().upper() for x in ner_text_list.split('|')])
                            ner = ner - discard_words_set




                            #ner = ner | set([x.strip().upper() for x in s['ner'].replace('ORGANIZATION', '').replace('LOCATION', '').replace('PERSON', '').replace('MISC', '').replace('DATE', '').replace('(', '').replace(')', '').replace('|', ',').split(',')])
                            #ner = ner | set([x.strip().upper() for x in ner_text_list.split('|')])
                            #ner = ner - discard_words_set

            #print ner

            for s in sentences['sentences']:
                #if item in ner:
                content = s['sentence']
                if item in ner:
                    count += len(re.findall(item, content.upper()))

                    if actor_dict.contains(item):
                        continue

                    #TO_DO: find NP from tree: findNP(NPParseTreeHashMap, item)
                    new_actor_freq[item] = count


        #print new_actor_freq

        new_actor = dict()
        new_actor['doc_id'] = new_actor_meta['doc_id']
        new_actor['new_actor'] = new_actor_freq

        #print  new_actor

        total_new_actor_list.append(new_actor)


    with open('/root/Desktop/new_actor.txt', 'w') as outfile:
        json.dump(total_new_actor_list, outfile)


    word_dict = dict()
    word_dict_count = dict()

    total_document = 0.0

    for item in total_new_actor_list:
        #{"new_actor": {"DHUBULIA": 2, "PRIMARY": 11, "NADIA\u00c2": 1}, "doc_id": "india_telegraph_bengal20160922.0001"}
        total_count = 0.0
        if 'new_actor' in item and 'doc_id' in item:
            total_document += 1
            for k in item['new_actor'].keys():
                total_count += item['new_actor'][k]

            for k in item['new_actor'].keys():
                tf = 1.00 * (item['new_actor'][k]/total_count)
                if k not in word_dic:
                    word_dic[k] = tf
                    word_dict_count[k] = 1
                else:
                    word_dic[k] += tf
                    word_dict_count[k] += 1



    for k in word_dic.keys():
        word_dic[k] = word_dic[k] * (word_dict_count[k]/total_document)


    word_dic_sorted = sorted(word_dic.items(), key=lambda x : (-x[1], x[0]))[:N]

    #with open('/root/Desktop/new_actor_td_df.txt', 'w') as outfile:
    #    json.dump(word_dic_sorted, outfile)

    for actor_item in  word_dic_sorted:
        actor_noun = actor_item[0]
        if actor_noun in new_actor_over_time:
            new_actor_over_time[actor_noun] += 1
        else:
            new_actor_over_time[actor_noun] = 1





    with open('/root/Desktop/new_actor_td_df.txt', 'w') as outfile:
        json.dump(sorted(new_actor_over_time.items(), key=lambda x : (-x[1], x[0])), outfile)







        # from dateutil import parser
        # from datetime import datetime
        #
        # dateObject = parser.parse("")
        #
        # article_date = datetime.strftime(dateObject, '%Y%m%d')
        #
        #
        # print article_date