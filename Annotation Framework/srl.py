from allennlp.predictors.predictor import Predictor
import allennlp_models.tagging
import re
from load_data import all_stories
import nltk
import spacy

stopwords = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn', 'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn', '!', ',' ,'.' ,'?' ,'-s' ,'-ly' ,'</s> ', 's']
predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/structured-prediction-srl-bert.2020.12.15.tar.gz")

def tokenize_en(text):
    #return [tok.text for tok in spacy_en.tokenizer(text)]
    return [tok for tok in nltk.word_tokenize(text)]

def semantic_role_labeling(raw_data):
    sentences = raw_data.split(".")
    unused_words = []
    #predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/structured-prediction-srl-bert.2020.12.15.tar.gz")
    for s in sentences:
        s = s.replace("\n", ' ').replace("\r", '')
        words = tokenize_en(s)
        word_list = {}
        # get all words
        for i, w in enumerate(words):
            if w!="" and not w[len(w)-1].isalpha():
                words[i] = w[:len(w)-1]
            word_list[words[i]] = 0
        # semantic role labeling
        tree = predictor.predict(sentence=s)
        verb_list = tree["verbs"]
        # Count labeled words
        for l in verb_list:
            labeled_sentence = l["description"]
            tag = re.findall("\[(.*?)\]", labeled_sentence)
            #print(tag)
            for t in tag:
                if re.findall(".*: (.*)", t) != []:
                    #print(re.findall(".*: (.*)", t))
                    labeled_words = re.findall(".*: (.*)", t)[0].split(" ")
                else:
                    labeled_words = t.split(" ")
                words_tag = re.findall("(.*):", t)
                #print(labeled_words, words_tag)
                for labeled_word in labeled_words:
                    if labeled_word in word_list:
                        word_list[labeled_word] += 1
        #print(word_list)
        for key, value in word_list.items():
            if value == 0 and key != '' and not '-' in key:
                unused_words.append(key.lower())
    global stopwords
    stopwords = list(set(unused_words + stopwords))
            
if __name__ == '__main__':
    for key, value in all_stories.items():
        for dict in value:
            para = dict["text"]
            semantic_role_labeling(para)
    print(stopwords)