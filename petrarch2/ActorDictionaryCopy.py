# import re
#
# from ClusterSImilarity import FuzzyClusterSimilarity
#
#
# class ActorDictionary:
#     actor_filenames= ['Phoenix.Countries.actors.txt',
#                       'Phoenix.International.actors.txt',
#                       'Phoenix.MilNonState.actors.txt']
#     folder = 'data/dictionaries'
#
#     actor_set = set()
#
#     fcs = FuzzyClusterSimilarity()
#
#     THERSHOLD = 0.80
#
#     def __init__(self):
#         for filename in self.actor_filenames:
#             fs = open(self.folder + "/" + filename)
#             for line in fs:
#                 line = line.strip()
#                 if line.startswith('#') or len(line) == 0:  # if it is a comment
#                     continue
#                 line = line.split('#')[0]
#
#                 line = re.sub(r'\[[^\]]*\]', '', line).replace('_', ' ').replace('+', '').strip()
#                 #print line
#                 for word in line.split(' '):
#                     if len(word) > 1:
#                         self.actor_set.add(word)
#
#             fs.close()
#
#     def contains(self, actorname):
#         test = actorname.replace('_',' ').strip()
#         return test in self.actor_set
#
#
#
