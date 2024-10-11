from flask import Flask, redirect, render_template, request, jsonify
import random
import csv
import json
import os, stat
from lemmatize import lemmatize

app = Flask(__name__, static_folder = './static')

def load_json(file_path):
    assert file_path.split('.')[-1] == 'json'
    with open(file_path,'r') as file:
        data = json.load(file)
    return data

def save_json(save_path,data):
    assert save_path.split('.')[-1] == 'json'
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(data, file)
    file.close()

#all_stories = load_json('./preprocess/all_stories.json')
#all_titles = load_json('./preprocess/all_titles.json')
#all_section_counter = load_json('./preprocess/all_section_counter.json')
#triples = load_json('./preprocess/triples.json')
#anntation_history = load_json('./preprocess/annotation_history.json')

def pick_a_paragraph(section_id_list, username):
    #pick a random paragraph from sections that haven't been annotated yet
    all_section_counter = load_json('./preprocess/all_section_counter.json')
    all_titles = load_json('./preprocess/all_titles.json')
    u_dict = load_json('./user_data/' + username + '.json')
    remain_sections = list(set(all_section_counter)-set(section_id_list))
    print("remain_sections:", remain_sections)
    if remain_sections == []:
        return 0
    else:
        rand_section = random.choice(remain_sections)
        story_id = int(rand_section.split('_')[0])
        section_id = int(rand_section.split('_')[1])
        print("selected_section:",)
        title = all_titles[story_id]
        return load_json('./preprocess/data/' + title + '.json')[str(section_id)]

@app.route('/new_paragraph', methods=["GET"])
def get_paragraph():
    if request.method == 'GET':
        story_title = str(request.args.get('title'))
        story_id = str(request.args.get('s_id'))
        para_id = str(request.args.get('id'))
        username = str(request.args.get('username'))
        print(story_title, para_id)
        ###########!!!!!!!!##########
        u_dict = load_json('./user_data/' + username + '.json')
        all_section_counter = load_json('./preprocess/all_section_counter.json')
        all_stories = load_json('./preprocess/all_stories.json')
        all_titles = load_json('./preprocess/all_titles.json')
        anntation_history = load_json('./preprocess/annotation_history.json')
        if (u_dict['labeled_flag'] == 1):
            if story_title in all_titles:
                all_stories[story_title][int(para_id)-1]["label_time"] += 1
                anntation_history[story_title][int(para_id)-1]["label_time"] += 1
                if anntation_history[story_title][int(para_id)-1]["label_time"] == 1:
                    anntation_history[story_title][int(para_id)-1]["user1"] = username
                elif anntation_history[story_title][int(para_id)-1]["label_time"] == 2:
                    anntation_history[story_title][int(para_id)-1]["user2"] = username
                    all_section_counter.remove(str(story_id) + '_' + str(para_id))
                #u_dict['section_id'].append(str(story_id) + '_' + str(para_id))
                #u_dict['section_num'] += 1
        #pick a new paragraph
        new_para_res = pick_a_paragraph(u_dict['section_id'], username)
        if new_para_res == 0:
            return "No more New Paragraphs"
        else:
            u_dict['para_dict'] = new_para_res
            u_dict['labeled_flag'] = 0
            save_json('./user_data/' + username + '.json', u_dict)
            save_json('./preprocess/annotation_history.json', anntation_history)
            return json.dumps(u_dict['para_dict'])

@app.route('/')
def load():
    return render_template("index.html")

@app.route('/search', methods=["GET"])
def search_form():
    if request.method == 'GET':
        word = request.args.get('word')
        username = str(request.args.get('username'))
        u_dict = load_json('./user_data/' + username + '.json')
        u_dict['word'] = word.replace('"','').replace("'",'').replace('.','').replace(',','').lower()
        print("before:", u_dict['word'])
        #----lemmanization----#
        u_dict['word'] = lemmatize(u_dict['word'])
        print("after:", u_dict['word'])
        triples = load_json('./preprocess/triples.json')
        u_dict['retrieval'] = triples[u_dict['word']]
        save_json('./user_data/' + username + '.json', u_dict)
        return json.dumps(u_dict['retrieval'])

@app.route('/submit', methods=["GET"])
def submit_qa():
    if request.method == 'GET':
        question = str(request.args.get('question'))
        answer = str(request.args.get('answer'))
        concept = int(str(request.args.get('concept')))
        word_id = str(request.args.get('word_id'))
        title = str(request.args.get('title'))
        section = int(str(request.args.get('section')))
        username = str(request.args.get('username'))
        
        u_dict = load_json('./user_data/' + username + '.json')
        retireved_triplets = u_dict['retrieval']['triples']
        triple = retireved_triplets[concept]
        sub = triple[0]
        rel = triple[1]
        obj = triple[2]
        weight = triple[3]
        if not os.path.isdir('./QA dataset'):
            os.makedirs("./QA dataset")
        if not os.path.isdir('./QA dataset/' + username):
            os.makedirs('./QA dataset/' + username)  
        if not os.path.isfile("./QA dataset/" + username + '/' + title + "-QAC_test.csv"):
            f =  open("./QA dataset/" + username + '/' + title + "-QAC_test.csv", 'w', encoding='utf8', newline='')
            header = ['section_id', 'word_id', 'concept(sub)', 'relation', 'obj', 'question', 'answer']
            writer = csv.writer(f)
            writer.writerow(header)
            f.close()
        os.chmod("./QA dataset/" + username + '/' + title + "-QAC_test.csv", stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
        with open("./QA dataset/" + username + '/' + title + "-QAC_test.csv", 'a', encoding='utf8', newline='') as f:
            writer = csv.writer(f)
            r = [section, word_id, sub, rel, obj, question, answer]
            writer.writerow(r)
        u_dict['labeled_flag'] = 1
        all_titles = load_json('./preprocess/all_titles.json')
        section_id = str(all_titles.index(title)) + '_' + str(section)
        if (section_id not in u_dict['section_id']):
            u_dict['section_id'].append(section_id)
            u_dict['section_num'] += 1
            print("Sections updated, added" + section_id + ", now have" + str(u_dict['section_num']) + "sections.")
        save_json('./user_data/' + username + '.json', u_dict)
        return "done"

@app.route('/init', methods=["GET"])
def init():
    if request.method == 'GET':
        username = str(request.args.get('username')).lower()
        if not os.path.isdir('./user_data'):
            os.makedirs("./user_data")
        if not os.path.isfile('./user_data/' + username + '.json'):
            f = open('./user_data/' + username + '.json', 'w', encoding='utf8')
            u_dict = {}
            u_dict['labeled_flag'] = 0
            u_dict['word'] = ''
            u_dict['retrieval'] = {}
            u_dict['para_dict'] = {}
            u_dict['section_id'] = []
            u_dict['section_num'] = 0
            save_json('./user_data/' + username + '.json', u_dict)
        return "done"

if __name__ == '__main__':     
    app.run(debug = True, host = "0.0.0.0")

