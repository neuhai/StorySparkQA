from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

WNL = WordNetLemmatizer()

def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def lemmatize(word):
    #
    return WNL.lemmatize(word, get_wordnet_pos(pos_tag([word])[0][1]))