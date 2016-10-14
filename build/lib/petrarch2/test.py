  
from EventCoder import EventCoder
 
coder = EventCoder(petrGlobal={}) 
 
another_coder = EventCoder(petrGlobal=coder.get_PETRGlobals())
  
input_file = open('core_nlp_out.txt')
  

  
for line in input_file:
      
    print line      
    print '==================='
      
    print another_coder.encode(line)

# from dateutil import parser
# from datetime import datetime
# 
# dateObject = parser.parse("")
# 
# article_date = datetime.strftime(dateObject, '%Y%m%d') 
# 
# 
# print article_date 