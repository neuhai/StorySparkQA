import os
import pandas as pd
import json
filepath = './data/'

all_stories = {}
all_titles = []
all_section_counter = []
for i, j, k in os.walk(filepath):
    for c, n in enumerate(k):
        if '-story.csv' in n:
            story_title = n[:len(n)-10]
            all_stories[story_title] = []
            story = pd.read_csv(filepath + n)
            all_titles.append(story_title)
            for index, row in story.iterrows():
                if index == 0:
                    continue
                p_dict = {}
                paragraph = row["text"]
                p_dict["id"] = index
                p_dict["text"] = paragraph
                p_dict["label_time"] = 0
                all_stories[story_title].append(p_dict)
                all_section_counter.append(str(c+23) + '_' + str(index))



file = open('all_stories1.json', 'w')
json.dump(all_stories, file)

file = open('all_titles1.json', 'w')
json.dump(all_titles, file)

file = open('all_section_counter1.json', 'w')
json.dump(all_section_counter, file)



