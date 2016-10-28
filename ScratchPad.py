from datasketch import MinHash
import operator
data1 = ['TURGOV']
data2 = ['TURGOV']

m1, m2 = MinHash(), MinHash()
for d in data1:
    m1.update(d.encode('utf8'))
for d in data2:
    m2.update(d.encode('utf8'))
print("Estimated Jaccard for data1 and data2 is", m1.jaccard(m2))

s1 = set(data1)
s2 = set(data2)
actual_jaccard = float(len(s1.intersection(s2)))/float(len(s1.union(s2)))
print("Actual Jaccard for data1 and data2 is", actual_jaccard)

suggested_roles = {'Hello':1, 'World':5, 'How':3}
sorted_list = sorted(suggested_roles, key=operator.itemgetter(1))[-5:]
print sorted_list