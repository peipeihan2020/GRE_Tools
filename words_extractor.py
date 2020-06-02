import glob
import re
import os
pdf_path = "pdf/"
pdfs = glob.glob("{}/*.pdf".format(pdf_path))
pdfs
from pdf_extractor import extract_pdf_content
import pandas as pd
import numpy as np
import words_read as wr

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

def find_all_words(text):
    m = re.finditer('(([A-Za-z]+\-[A-Za-z]+)|([A-Za-z]+))', text)
    words = []
    for s in m:
       words.append(text[s.start(): s.end()])
    s = set(words)
    return list(s)

def find_word_from_dict(word, word_dic):
    meaning = ''

    split_words = word.split(' ')
    if len(split_words) == 1:
        t = word_dic.loc[word_dic['word'] == word]
        meaning = ''
        if len(t['meaning'].values) > 0:
            meaning = t['meaning'].values[0]
    else:
        t = word_dic.loc[word_dic['word'].isin(split_words)]
        if t.shape[0] > 0:
            for i in range(t.shape[0]):
                meaning += t['word'].values[i] + '  ' + t['meaning'].values[i] + ';   '
    return meaning

words_fojiao = wr.read_fojiao()

content = extract_pdf_content(pdfs[0])
text = content.replace('GRE填空机经1200题','').replace('\n'*3,'\n').replace('\n'*2,'\n')
print(text)
sections,_ = find_all('section\s*\d+\s*((easy)|(medium)|(hard)|\s*)', text)
words_3000 = wr.read_3000()
words_red = wr.read_red()

saved_words=[]
section_count = 1

section_np=[]
problem_np=[]
meaning_np=[]
words_np=[]
for section in sections:
    problems,_ = find_all('\n[\d]{1,2}\.', section)
    problem_count = 1
    for problem in problems:
        words, issue = find_all('\n[A-I]\.', problem)
        words_from_text = find_all_words(issue)
        words =[*words_from_text, *words]
        for word in words:
            word = word.replace('A.', '').replace('B.', '').replace('C.', '').replace('D.', '').replace('E.', '').replace('F.', '').replace('G.', '').replace('H.', '').replace('I.', '').strip()
            word = word.lower()
            meaning = find_word_from_dict(word, words_3000)
            if meaning == '':
               meaning = find_word_from_dict(word, words_red)
            if meaning == '':
                meaning = find_word_from_dict(word, words_fojiao)
            if meaning != '':
                saved_words.append(word)
                meaning_np.append(meaning)
                section_np.append(section_count)
                problem_np.append(problem_count)
        problem_count += 1
    section_count +=1
df = pd.DataFrame({'section':section_np,
              'problem':problem_np,
              'word':saved_words,
              'meaning':meaning_np})

df.to_csv('words.csv',encoding='utf_8_sig')

