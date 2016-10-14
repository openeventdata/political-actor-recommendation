import pprint

from ActorDictionary import ActorDictionary
from ClusterSImilarity import FuzzyClusterSimilarity
from UnionFind import UnionFind


class ActorResolver:


    stored_actor_dict = ActorDictionary()

    possible_actor_list = set()

    clsSimilarity = FuzzyClusterSimilarity()

    compressed_dict = {}

    def getFrequencyCount(self, freq_dict={}):

        updated_dict = {}

        for doc_key in freq_dict:
            doc_actor_dict = freq_dict[doc_key]

            compress_actor_dict = self.compress(doc_actor_dict)
            #compress_actor_dict = doc_actor_dict

            for actor_key in compress_actor_dict:
                if self.stored_actor_dict.contains(actor_key):
                    continue # already in the CAMEO Actor Dictionary
                else:
                    possible_actor, ratio = self.getClosestMatch(actor_key)

                    if possible_actor is not None:
                        tokens, freq = updated_dict[possible_actor]
                        if len(possible_actor) < len(actor_key):
                            self.possible_actor_list.remove(possible_actor)
                            self.possible_actor_list.add(actor_key)

                            updated_dict.pop(possible_actor, None)
                            updated_dict[actor_key] = (compress_actor_dict[actor_key][0].append(tokens), compress_actor_dict[actor_key][1]+freq)
                        else:
                            updated_dict[possible_actor] = (compress_actor_dict[actor_key][0].append(tokens), compress_actor_dict[actor_key][1]+freq)
                    else:
                        updated_dict[actor_key] = compress_actor_dict[actor_key]
                        self.possible_actor_list.add(actor_key)
        return updated_dict


    def rank(self, freq_dict={}):
        updated_dict = self.getFrequencyCount(freq_dict)




    def getClosestMatch(self, actor_name):
        max_ratio = 70
        possible_actor = None
        for name in self.possible_actor_list:
            if self.clsSimilarity.measure(name, actor_name) > max_ratio:
                max_ratio = self.clsSimilarity.measure(name, actor_name)
                possible_actor = name
        return (possible_actor, max_ratio)


    def getParent(self, parentDict={}, key=None):
        temp = key
        while parentDict[temp] != temp:
            temp = parentDict[temp]
        print temp
        return temp


    def compress(self, actor_freq_dict={}):
        compressed_dict = {}
        list_of_names = []

        for key in actor_freq_dict:
            list_of_names.append(key)

        uf = UnionFind(list_of_names)

        for i in range(0, len(list_of_names)):
            maxMatched = None
            maxRatio = 70
            for j in range(0, len(list_of_names)):
                if i == j:
                    continue
                ratio = self.clsSimilarity.measure(uf.find(list_of_names[i]), uf.find(list_of_names[j]))

                print ratio
                if ratio > maxRatio:
                    maxRatio = ratio
                    maxMatched = list_of_names[j]
            if maxMatched is not None:
                uf.union(maxMatched, list_of_names[i])
        print "TEST"

        for key in list_of_names:
            print key
            parent = uf.find(key)
            print parent
            if parent not in compressed_dict:
                print "Inserting"
                print actor_freq_dict[key][1]
                compressed_dict[parent]=([key], actor_freq_dict[key][1])
            else:
                print "Updating"
                compressed_dict[parent][0].append(key)
                maximum = max(compressed_dict[parent][1], actor_freq_dict[key][1])
                compressed_dict[parent]= (compressed_dict[parent][0], maximum)

        return compressed_dict



#===================================================================================================================
if __name__ == '__main__':

    actorResolver = ActorResolver()

    test_dict = {u'HENDRICKS': ([u'HENDRICKS'], 4), u'EBTEKAR': ([u'EBTEKAR'], 4), u'BARBARA_HENDRICKS': ([u'HENDRICKS', u'BARBARA'], 4), u'MASOUMEH_EBTEKAR': ([u'EBTEKAR', u'MASOUMEH'], 4)}

    pprint.pprint(actorResolver.compress(test_dict))