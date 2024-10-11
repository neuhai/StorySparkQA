import json
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from scipy.linalg import norm

relation_text = ['is a', 'is at location of', 'is located near', 'is capable of', 'causes', 
'causes desire of', 'is motivated by goal of', 'is created by', 'desires', 'is the antonym of', 
'is distinct from', 'has context of', 'has property', 'has subevent', 'has prerequisite', 'entails',  
'instance of', 'is defined as', 'is made of', 
'is part of', 'has a', 'is similar to', 'is used for']

merged_text = ['isa', 'atlocation', 'locatednear', 'capableof', 'causes', 
'causesdesire', 'motivatedbygoal', 'createdby', 'desires', 'antonym', 
'distinctfrom', 'hascontext', 'hasproperty', 'hassubevent', 'hasprerequisite', 'entails',  
'instanceof', 'definedas', 'madeof', 
'partof', 'hasa', 'similarto', 'usedfor']

class TripleFinder:
    def __init__(self, cpnet_path, weight_lb = 1.0, target_relations = None):
        self.weight_lb = weight_lb
        self.cpnet = json.load(open(cpnet_path, encoding = 'utf-8'))
        self.nlp = spacy.load('en_core_web_sm')
        self.all_concepts = set(self.cpnet.keys())

        for c in self.cpnet:
            self.all_concepts.update(self.cpnet[c].keys())
        for w in self.nlp.Defaults.stop_words:
            if w in self.all_concepts:
                self.all_concepts.remove(w)
        self.all_concepts_list = list(self.all_concepts)
        self.target_relations = target_relations

    def process_word(self, word):
        word = word.lower()
        concept = word.replace(' ', '_')
        concept = concept.replace('-', '_')
        concept = self.nlp(concept).text
        return concept
    
    def find_triplet(self, word):
        retrieved_triplets = []
        word = self.process_word(word)
        if(word in self.cpnet):
            for obj in self.cpnet[word].keys():
                for rel, weight in self.cpnet[word][obj].items():
                    if weight >= self.weight_lb:
                        rel = relation_text[merged_text.index(rel)]
                        retrieved_triplets.append([str(word), str(rel), str(obj), weight])
            if len(retrieved_triplets) == 0:
                for obj in self.cpnet[word].keys():
                    for rel, weight in self.cpnet[word][obj].items():
                        if weight > self.weight_lb:
                            rel = relation_text[merged_text.index(rel)]
                            retrieved_triplets.append([str(word), str(rel), str(obj), weight])
        #print(retrieved_triplets)
        if(len(retrieved_triplets) <= 6):
            return retrieved_triplets
        return self.pick_diff_triple(self.rank_triples(retrieved_triplets))
        #return self.rank_triples(retrieved_triplets)[:6]

    def tfidf_similarity(self, s1, s2):
        # 转化为TF矩阵
        cv = TfidfVectorizer(tokenizer=lambda s: s.split())
        corpus = [s1, s2]
        vectors = cv.fit_transform(corpus).toarray()
        # 计算TF系数
        return np.dot(vectors[0], vectors[1]) / (norm(vectors[0]) * norm(vectors[1]))


    def rank_triples(self, triplets):
        t_list = triplets
        t_len = len(t_list)
        #sim_array = [[1 for j in range(t_len)] for i in range(t_len)]
        #avg_array = {}
        avg_array = [0 for i in range(t_len)]
        #for i in range(t_len):
        #    avg_array[str(i)] = 0
        for i in range(t_len):
            t_str1 = t_list[i][1] + ' <sep> ' + t_list[i][2]
            for j in range(i, t_len):
                t_str2 = t_list[j][1] + ' <sep> ' + t_list[j][2]
                #sim_array[i][j] = self.tfidf_similarity(t_str1, t_str2)
                #sim_array[j][i] = sim_array[i][j]
                #avg_array[str(i)] += sim_array[i][j]
                #avg_array[str(j)] += sim_array[i][j]
                sim = self.tfidf_similarity(t_str1, t_str2)
                avg_array[i] += sim
                avg_array[j] += sim
        for i in range(t_len):
            #avg_array[str(i)] /= t_len
            avg_array[i] /= t_len
            #print(avg_array[i])
            t_list[i][3] += 1 - avg_array[i]
        t_list.sort(key=lambda x:x[3], reverse=True)
        return t_list

    def pick_diff_triple(self, triplets):
        t_list = triplets
        res = []
        prev_rel = ""
        one_round = 0
        while len(res) < 6:
            if (one_round == 1):
                res += t_list[:6-len(res)]
                break
            for i in t_list:
                if(len(res) >= 6):
                    break
                if (i[1] != prev_rel):
                    res.append(i)
                    t_list.remove(i)
                    prev_rel = i[1]
            one_round =1
        return res
        
class MeaningResolver:
    def __init__(self, wikdict_fn = None):
        self.nlp=spacy.load('en_core_web_sm')        
        self.wik_dict = json.load(open(wikdict_fn, encoding='utf-8'))
        self.call_history = set()
    
    def process_word(self, word):
        word = word.lower()
        concept = word.replace(' ', '_')
        concept = concept.replace('-', '_')
        concept = self.nlp(concept).text
        return concept

    def resolve_meaning(self, word):
        concept = self.process_word(word)
        if concept == '':
            return ''
        if concept in self.wik_dict:
            for meaning in self.wik_dict[concept]:
                if 'senses' in meaning:
                    for sense in meaning['senses']:
                        if 'form_of' in sense or 'alt_of' in sense: # try to follow these links
                            form_str = 'form_of' if 'form_of' in sense else 'alt_of'
                            concept_new = sense[form_str][0]
                            if concept.lower() == concept_new.lower():
                                continue
                            if len(concept_new.split(' ')) <= 4:
                                return self.resolve_meaning(concept_new)
                        elif 'heads' in meaning and meaning['heads'][0].get('2', '') == 'verb form':
                            try_str = sense['glosses'][0].split(' of ')
                            if len(try_str) == 2:
                                concept_new = try_str[-1]
                                return self.resolve_meaning(concept_new)
                            else:
                                print('verb form failed:', meaning)             
                        if 'glosses' in sense:
                            mstr = '{}: {}'.format(concept, sense['glosses'][0])
                            return mstr


t_finder = TripleFinder("../assets/most_edges_allweights.json")
m_resolver = MeaningResolver("../assets/wik_dict.json")