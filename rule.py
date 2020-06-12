import re

def find_all(pattern, text):
   m= re.finditer(pattern, text)
   start = 0
   sub_text =[]
   title=''
   for s in m:
       end = s.start()
       t = text[start:end]
       if start > 0:
           sub_text.append(t)
       else:
           title = t
       print(t)
       start = end
   sub_text.append(text[start:])
   return sub_text,title

def find_all_words(pattern, text):
    m = re.finditer(pattern, text)
    words = []
    for s in m:
       words.append(text[s.start(): s.end()])
    return words

def remove_index_from_problem(text):
    m = re.search('\n[\d]{1,2}\.', text)
    return text[m.end():]