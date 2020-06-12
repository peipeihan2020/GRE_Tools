from ecdict.stardict import LemmaDB

lemma = LemmaDB()
lemma.load('.\ecdict\lemma.en.txt')

def get_origin(w):
    l = lemma.word_stem(w.lower())
    if l:
        return l[0]
    else:
        return w