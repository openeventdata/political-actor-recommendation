

class UnionFind:

    parents = {}

    def __init__(self, list=[]):
        for item in list:
            self.parents[item] = item



    def find(self, item):
        temp = item
        while self.parents[temp] != temp:
            temp = self.parents[temp]
        return temp


    def union(self, item1, item2):
        p1 = self.find(item1)
        p2 = self.find(item2)

        if len(p1) > len(p2):
            self.parents[p2] = p1
        else:
            self.parents[p1] = p2
