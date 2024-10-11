from allennlp.predictors.predictor import Predictor
import allennlp_models.tagging
import re
#from load_data import all_stories, all_titles
import nltk
import spacy
import json

spacy_en = spacy.load('en_core_web_sm')
stopwords = set(['``'])
predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/structured-prediction-srl-bert.2020.12.15.tar.gz")

def tokenize_en(text):
    #return [tok.text for tok in spacy_en.tokenizer(text)]
    return [tok for tok in nltk.word_tokenize(text)]

def filter_all_words(raw_data):
    global stopwords
    sentences = raw_data.split(". ")
    #predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/structured-prediction-srl-bert.2020.12.15.tar.gz")
    for s in sentences:
        s = s.replace("\n", ' ').replace("\r", '')
        #----filter1: using spacy pos----#
        spacy_stop_words = []
        doc = spacy_en(raw_data)
        for token in doc:
            if(token.is_stop == True or token.pos_ in ['AUX', 'ADP', 'DET', 'PART', 'PUNCT', 'SYM', 'X']):
                spacy_stop_words.append(token.text.lower())
        stopwords = set(spacy_stop_words) | stopwords

        words = set(tokenize_en(s))
        word_list = set([])
        # get all words
        #for i, w in enumerate(words):
        #    word_list[words[i]] = 0
        #----filter2: semantic role labeling----#
        tree = predictor.predict(sentence=s)
        verb_list = tree["verbs"]
        # Count labeled words
        for l in verb_list:
            labeled_sentence = l["description"]
            tag = re.findall("\[(.*?)\]", labeled_sentence)
            #print(tag)
            for t in tag:
                if re.findall(".*: (.*)", t) != []:
                    labeled_words = re.findall(".*: (.*)", t)[0].split(" ")
                else:
                    labeled_words = t.split(" ")
                #words_tag = re.findall("(.*):", t)
                #print(labeled_words, words_tag)
                for labeled_word in labeled_words:
                    if labeled_word not in word_list:
                        word_list.add(labeled_word)
        #print(word_list)
    stopwords = words - word_list | stopwords
    return stopwords

def preprocess_text(word_list, stop_words):
    words = []
    for i, w in enumerate(word_list):
        word = {}
        word['id'] = i
        word['word'] = w
        word['marked'] = 0
        if w.lower() in list(stop_words):
            word['stop'] = 1
        else:
            word['stop'] = 0
        words.append(word)
    return words

 


        


