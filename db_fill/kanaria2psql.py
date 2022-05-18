import json
import argparse, csv
from itertools import count
from collections import defaultdict

with open("rmrk.json", encoding="utf-8") as json_file:
    data = json.loads(
        (json.dumps(json.load(json_file)).replace("'", "''")))

collection_id = 'e0b9bdcc456a36497a-KANBIRD'
birds_number = 0
birds = list()
for nft_key in data['nfts'].keys():
    if collection_id in nft_key:
        birds.append(data['nfts'][nft_key])
        birds_number = birds_number + 1
tails = list()
tops = list()
bodies = list()

def get_row(bird):
    bird_id = int(bird["id"][-8:])
    theme = bird["resources"][0]["themeId"]
    parts_list = bird["resources"][0]["parts"]
    parts_list = [x.lower() for x in parts_list]
    for key_string in parts_list:
        if key_string.find('_head') != -1:
            head = key_string[:-5]
        if key_string.find('_eyes') != -1:
            eyes = key_string[:-5]
        if key_string.find('_body') != -1:
            body = key_string[:-5]
            bodies.append(body)
        has_tail = False
        if key_string.find('_tail') != -1:
            tail = key_string[:-5]
            has_tail = True
            tails.append(tail)
        has_top = False
        if key_string.find('_top_rare') != -1:
            tail = key_string[:-9]
            has_top = True
            tops.append(tail)
        if has_tail and has_top:
            print(bird_id)
        if key_string.find('_wingleft') != -1:
            wingLeft = key_string[:-9]
        if key_string.find('_handleft') != -1:
            handLeft = key_string[:-9]
        if key_string.find('_wingright') != -1:
            wingRight = key_string[:-10]
        if key_string.find('_handright') != -1:
            handRight = key_string[:-10]
        if key_string.find('_footleft') != -1:
            footLeft = key_string[:-9]
        if key_string.find('_footright') != -1:
            footRight = key_string[:-10]
        if key_string.find('_beak') != -1:
            beak = key_string[:-5]
    # print(bird_id, parts_list)
    assert footLeft == footRight, bird_id
    assert wingLeft == handLeft, bird_id
    assert wingRight == handRight, bird_id
    feet = footLeft
    return [bird_id, theme, head, eyes, body, tail, wingLeft, wingRight, feet, beak]

column_names = ['bird_id', 'theme', 'head', 'eyes', 'body', 'tail', 'wingLeft', 'wingRight', 'feet', 'beak']
birds_dataset = list()
for bird in birds:
    birds_dataset.append(get_row(bird))
    
with open('birds_dataset.csv', 'w', newline='') as birds_file:
    bird_writer = csv.writer(birds_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    bird_writer.writerow(column_names)
    for row_index in range(len(birds_dataset)):
        bird_writer.writerow(birds_dataset[row_index])

schema_sql = f'''
CREATE TABLE IF NOT EXISTS kanbirds (bird_id text primary key, theme text, head text, eyes text, body text, tail text, wingLeft text, wingRight text, feet text, beak text);
CREATE TABLE IF NOT EXISTS kanbirds_alias (bird_id text primary key, theme text, head text, eyes text, body text, tail text, wingLeft text, wingRight text, feet text, beak text);
'''
kanbirds_sql = f"INSERT INTO kanbirds (bird_id, theme, head, eyes, body, tail, wingLeft, wingRight, feet, beak) VALUES \n"
for bird in birds_dataset:
	kanbirds_sql += f"(\'{bird[0]}\', \'{bird[1]}\', \'{bird[2]}\', \'{bird[3]}\', \'{bird[4]}\', \'{bird[5]}\', \'{bird[6]}\', \'{bird[7]}\', \'{bird[8]}\', \'{bird[9]}\'),\n"
kanbirds_sql = kanbirds_sql[:-2] + \
	" ON CONFLICT (bird_id) DO UPDATE SET theme = excluded.theme, head = excluded.head, eyes = excluded.eyes, body = excluded.body, tail = excluded.tail, wingLeft = excluded.wingLeft, wingRight = excluded.wingRight, feet = excluded.feet, beak = excluded.beak;"

rows_number = len(birds_dataset)
columns_number = len(birds_dataset[0])
birds_traits_list = list()
for row_index in range(rows_number):
    for column_index in range(1, columns_number):
        birds_traits_list.append(birds_dataset[row_index][column_index])

mapping = defaultdict(count().__next__)
result = list()
for element in birds_traits_list:
    result.append(mapping[element])

birds_dataset_alias = list()
for row_index in range(rows_number):
    current_row = [birds_dataset[row_index][0]]
    current_row.extend(result[row_index * (columns_number - 1): (row_index + 1) * (columns_number - 1)])
    birds_dataset_alias.append(current_row)

kanbirds_alias_sql = f"INSERT INTO kanbirds_alias (bird_id, theme, head, eyes, body, tail, wingLeft, wingRight, feet, beak) VALUES \n"
for bird in birds_dataset_alias:
	kanbirds_alias_sql += f"(\'{bird[0]}\', \'{bird[1]}\', \'{bird[2]}\', \'{bird[3]}\', \'{bird[4]}\', \'{bird[5]}\', \'{bird[6]}\', \'{bird[7]}\', \'{bird[8]}\', \'{bird[9]}\'),\n"
kanbirds_alias_sql = kanbirds_alias_sql[:-2] + \
	" ON CONFLICT (bird_id) DO UPDATE SET theme = excluded.theme, head = excluded.head, eyes = excluded.eyes, body = excluded.body, tail = excluded.tail, wingLeft = excluded.wingLeft, wingRight = excluded.wingRight, feet = excluded.feet, beak = excluded.beak;"

result_sql = '\n'.join([schema_sql, kanbirds_sql, kanbirds_alias_sql])

with open("res.sql", 'w') as output_file:
    output_file.write(result_sql)




