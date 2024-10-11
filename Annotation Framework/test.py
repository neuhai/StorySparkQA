
'''
t = [['look', 'has subevent', 'see', 2],
    ['look', 'is a', 'sensing', 1],
    ['look', 'is a', 'appearance', 3.2],
    ['look', 'has subevent', 'convey', 1.8],
    ['look', 'has subevent', 'match', 1]]

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from scipy.linalg import norm


def tfidf_similarity(s1, s2):
    # 转化为TF矩阵
    cv = TfidfVectorizer(tokenizer=lambda s: s.split())
    corpus = [s1, s2]
    vectors = cv.fit_transform(corpus).toarray()
    # 计算TF系数
    return np.dot(vectors[0], vectors[1]) / (norm(vectors[0]) * norm(vectors[1]))


def rank_triples(triplets):
    t_len = len(triplets)
    sim_array = [[1 for j in range(t_len)] for i in range(t_len)]
    #avg_array = {}
    avg_array = [0 for i in range(t_len)]
    #for i in range(t_len):
    #    avg_array[str(i)] = 0
    for i in range(t_len):
        t_str1 = triplets[i][1] + ' <sep> ' + triplets[i][2]
        for j in range(i, t_len):
            t_str2 = triplets[j][1] + ' <sep> ' + triplets[j][2]
            sim_array[i][j] = tfidf_similarity(t_str1, t_str2)
            sim_array[j][i] = sim_array[i][j]
            #avg_array[str(i)] += sim_array[i][j]
            #avg_array[str(j)] += sim_array[i][j]
            avg_array[i] += sim_array[i][j]
            avg_array[j] += sim_array[i][j]
    for i in range(t_len):
        #avg_array[str(i)] /= t_len
        avg_array[i] /= t_len
        print(avg_array[i])
        triplets[i][3] += avg_array[i]
    triplets.sort(key=lambda x:x[3], reverse=True)
    return triplets

def pick_diff_triple(triplets):
    t_list = triplets
    res = []
    prev_rel = ""
    one_round = 0
    while len(res) < 6:
        if (one_round == 1):
            res += t_list[:6-len(res)]
        for i in t_list:
            if (i[1] != prev_rel):
                res.append(i)
                t_list.remove(i)
                prev_rel = i[1]
        one_round =1
        
    return res

print(rank_triples(t))
'''

import json

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


a1 = load_json('./user_data/annalise.json')
a2 = load_json('./user_data/annalise .json')

all_sec = list(set(a1["section_id"]) | set(a2["section_id"]))
a1["section_id"] = all_sec
a1["section_num"] = 699
save_json('./user_data/annalise.json', a1)