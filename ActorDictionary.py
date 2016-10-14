import re

from ClusterSImilarity import FuzzyClusterSimilarity


class ActorDictionary:
    actor_filenames= ['Phoenix.Countries.actors.txt',
                      'Phoenix.International.actors.txt',
                      'Phoenix.MilNonState.actors.txt']
    folder = 'data/dictionaries'

    actor_set = set()

    fcs = FuzzyClusterSimilarity()

    THERSHOLD = 0.75

    def __init__(self):
        for filename in self.actor_filenames:
            fs = open(self.folder + "/" + filename)
            for line in fs:
                line = line.strip()
                if line.startswith('#') or len(line) == 0:  # if it is a comment
                    continue
                line = line.split('#')[0]

                line = re.sub(r'\[[^\]]*\]', '', line).replace('_', ' ').replace('+', '').strip()
                #print line
                if len(line) > 1:
                    self.actor_set.add(line)

            fs.close()

    def contains(self, actorname):
        test = actorname.replace('_',' ').strip()
        if ('VLADIMIR' in  test) or ('PUTIN' in test):
            print 'Found'

        return test in self.actor_set
        # for name in self.actor_set:
        #     if self.fcs.measure(name, actorname) > self.THERSHOLD:
        #         return True
        # return False



