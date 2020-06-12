import re
from pdf_extractor import extract_pdf_content
import pandas as pd

import words_read as wr
import upload as up
import unicodedata
import rule



import ecdict.anayly as analy

def get_meaning_from_dict_one_origi(word, word_dic):
    t = word_dic.loc[word_dic['word'] == word]
    meaning = ''
    if len(t['meaning'].values) > 0:
        meaning = t['meaning'].values[0]
    return meaning

def get_meaning_from_dict_one_multi(w, word_dic):
    t = word_dic.loc[word_dic['word'] == w]
    if t.shape[0] > 0:
        return t['word'].values[0], t['meaning'].values[0]
    return None, None
def get_meaning_from_dict(word, word_dic):
    meaning = ''
    word=unicodedata.normalize("NFKC", word)
    split_words = word.split(' ')
    if len(split_words) == 1:
        meaning = get_meaning_from_dict_one_origi(word, word_dic)
        if meaning == '':
            origin = analy.get_origin(word)
            if origin != word:
               meaning =  get_meaning_from_dict_one_origi(origin, word_dic)
               if meaning != '':
                   meaning = origin + '   ' + meaning


    else:
        result = ''
        for w in split_words:
            word,meaning= get_meaning_from_dict_one_multi(w, word_dic)
            if word is None:
                ow = analy.get_origin(w)
                if ow != w:
                    word, meaning = get_meaning_from_dict_one_multi(ow, word_dic)
            if word is not None:
                result += word + '  ' + meaning + ';   '
        meaning =result
    return meaning

def save_all_sections():
    content = extract_pdf_content('pdf/tc.pdf', 6, False)
    text = content.replace('GRE填空机经1200题', '').replace('\n' * 3, '\n').replace('\n' * 2, '\n').replace('\n\d*\n','')
    # text = unicodedata.normalize("NFKC", text)
    m = re.finditer('section\s*\d+\s*((easy)|(median)|(hard)|\s*)', text)
    sections =[]
    for s in m:
        item = dict()
        start = s.start()
        end = s.end()
        stext = text[start:end]
        sstext = stext.replace('section','').strip()
        section_text = sstext.split(' ')
        if len(section_text) >0:
            item['id'] = int(section_text[0])
            item['level'] = 'unknown'
            if len(section_text) == 2:
                item['level']=section_text[1]
        sections.append(item)
    up.save_sections(sections)

def read_problems():
    content = extract_pdf_content('pdf/tc.pdf', 6)
    content= re.sub('\n+\d+\n+', '', content)
    text = content.replace('GRE填空机经1200题','').replace('\n'*3,'\n').replace('\n'*2,'\n')
    print(text)
    sections,_ = rule.find_all('section\s*\d+\s*((easy)|(medium)|(hard)|\s*)', text)
    return sections

def read_answers():
    content = extract_pdf_content('pdf/answers.pdf', 0)
    text = content.replace('GRE填空机经1200题', '').replace('\n' * 3, '\n').replace('\n' * 2, '\n').replace('\n\d*\n','')
    sections, _ = rule.find_all('\nSection\s*\d+', text)
    answers =[]
    for section in sections:
        section = section.replace('Section','')
        section_answers = rule.find_all_words('[A-Z]{1,3}',section)

        first_five = section_answers[5:]
        second_five=section_answers[:5]

        answers=[*answers, *first_five, *second_five]
    return answers

def get_problems_count(problem):
    m = re.finditer('\(i{1,3}\)____', problem)
    count = 0
    for s in m:
        count +=1
    if count < 2:
        count =1
    return count


def get_data():
    sections = read_problems()
    data_db = []
    section_count = 1
    for section in sections:
        problems, _ = rule.find_all('\n[\d]{1,2}\.', section)
        problem_count = 1
        for problem in problems:
            doc = dict()
            words, issue = rule.find_all('\n[A-I]\.', problem)
            issue = rule.remove_index_from_problem(issue)
            doc['problem'] = issue
            doc['problem_count'] = get_problems_count(problem)
            doc['section'] = section_count
            doc['problem_index'] = problem_count
            doc['selections'] = []
            words=sorted(words)
            for word in words:
                word = word.replace('A.', '').replace('B.', '').replace('C.', '').replace('D.', '').replace('E.','').replace('F.', '').replace('G.', '').replace('H.', '').replace('I.', '').strip()
                word = word.lower()
                doc['selections'].append(word)
            data_db.append(doc)
            problem_count += 1
        section_count += 1
    return data_db

def save_firebase():
    data_db = get_data()
    answers = read_answers()
    for i in range(len(answers)):
        data_db[i]['answer']=answers[i]
    up.save(data_db)

def get_words():
    words_keyking=wr.read_words()
    dictwords = words_keyking.to_dict()
    count = len(dictwords['problem'])
    words = []
    for i in range(count):
        word = dict()
        word['section'] = dictwords['section'][i]
        word['problem_index'] = dictwords['problem'][i]
        word['word'] = dictwords['word'][i]
        word['meaning'] = dictwords['meaning'][i]
        words.append(word)

    up.save_alert(words)

def save_csv():
    saved_words = []
    meaning_np = []
    words_3000 = wr.read_3000()
    words_red = wr.read_red()
    words_fojiao = wr.read_fojiao()
    data_bd = get_data()
    sections_np=[]
    problems_np =[]
    for item in data_bd:
        words_from_text = rule.find_all_words('(([A-Za-z]+\-[A-Za-z]+)|([A-Za-z]+))', item['problem'])
        words_from_text = set(words_from_text)
        words_from_text = list(words_from_text)
        words =[*words_from_text, *item['selections']]
        for word in words:
            word = word.lower()
            meaning = get_meaning_from_dict(word, words_fojiao)
            if meaning == '':
               meaning = get_meaning_from_dict(word, words_red)
            if meaning == '':
                meaning = get_meaning_from_dict(word, words_3000)
            if meaning != '':
                saved_words.append(word)
                meaning_np.append(meaning)
                sections_np.append(item['section'])
                problems_np.append(item['problem_index'])


    df = pd.DataFrame({'section':sections_np,
                  'problem': problems_np,
                  'word':saved_words,
                  'meaning':meaning_np})

    df.to_csv('words.csv',encoding='utf_8_sig')

get_words()
# save_all_sections()
# get_data()
# save_firebase()
# save_csv()
# words_fojiao=wr.read_fojiao()
# get_meaning_from_dict('an honorific', words_fojiao)
# save_all_sections()
# get_problems_count('The (i)_____ of molecular oxygen on Earth-sized planets around other stars in the universe would not be (ii)_____ sign of life: molecular oxygen can be a signature of photosynthesis')