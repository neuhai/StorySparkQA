import json
from filter_words import filter_all_words, tokenize_en
from extract_triple import t_finder, m_resolver
from lemmatize import lemmatize

def save_json(save_path,data):
    assert save_path.split('.')[-1] == 'json'
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(data,file)
    file.close()
 
def load_json(file_path):
    assert file_path.split('.')[-1] == 'json'
    with open(file_path,'r') as file:
        data = json.load(file)
    return data


all_stories = load_json('./all_stories1.json')
all_titles = load_json('./all_titles1.json')


triples_dict = load_json('./triples.json')

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
            retrieval_triples(w)
        words.append(word)
    return words

def retrieval_triples(word):
    word = word.replace('"','').lower()
        
        #----lemmanization----#
    word = lemmatize(word) 
    if word not in triples_dict:
        triples = t_finder.find_triplet(word)
        meaning = m_resolver.resolve_meaning(word)
        triples_dict[word] = {"meaning": meaning, "triples": triples}

def preprocess_all_stories():
    for i, t in enumerate(all_titles):
        t_list = all_stories[t]
        story_dict = {}
        for t_dict in t_list:
            id = t_dict['id']
            text = t_dict['text']
            label_time = t_dict['label_time']
            stop_words = filter_all_words(text)
            p_text = tokenize_en(text)
            p_words = preprocess_text(p_text, stop_words)
            para_dict = {"title": t, "s_id": i, "id": id, "words": p_words}
            story_dict[id] = para_dict
        save_json(t +'.json', story_dict)

preprocess_all_stories()   
save_json("triples.json", triples_dict)