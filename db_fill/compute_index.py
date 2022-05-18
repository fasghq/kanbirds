import psycopg2
import numpy as np
from collections import Counter
import scipy.stats as ss

#establishing the connection
conn = psycopg2.connect(
   database="rmrk", user='postgres', password='1qazwer2', host='127.0.0.1', port='5432'
)

#Setting auto commit false
conn.autocommit = True

#Creating a cursor object using the cursor() method
cursor = conn.cursor()

#Retrieving data
cursor.execute('''SELECT * from kanbirds_alias''')
birds_dataset = cursor.fetchall();

cursor.execute('''SELECT * from kanbirds''')
birds_dataset_strings = cursor.fetchall();

#Commit your changes in the database
conn.commit()

#Closing the connection
conn.close()

birds_dataset = np.array(birds_dataset, dtype='int32')
birds_dataset_strings = np.array(birds_dataset_strings)

def get_scores(birds_dataset, normalize=True):
    nfts_number = len(birds_dataset)
    columns_number = len(birds_dataset[0])
    birds_scores = np.zeros((nfts_number,))
    for column_index in range(columns_number):
        bird_traits = birds_dataset[:, column_index]
        entries = Counter(bird_traits)
        bird_group_sizes = np.array([entries[x] for x in bird_traits]).reshape((nfts_number, 1))
        keys = entries.keys()
        values = np.array(list(entries.values()))
        groups_number = len(values)
        values = values.reshape((1, len(values)))
        current_trait_score = (np.sum(np.divide((values + np.zeros((nfts_number, 1))), (bird_group_sizes + values)), 1) - 1/2) / (groups_number - 1)
        if normalize:
            current_trait_score = current_trait_score / np.sum(current_trait_score) * nfts_number
        birds_scores = birds_scores + current_trait_score  
    return birds_scores / columns_number

birds_scores = get_scores(birds_dataset[:, 1:])
birds_trait_scores = birds_scores

def get_set_scores(birds_dataset, normalize=True):
    nfts_number = len(birds_dataset)
    columns_number = len(birds_dataset[0])
    # get biggest subset
    bigest_subsets = list()
    for bird_index in range(len(birds_dataset)):
            current_list = list(birds_dataset_strings[bird_index, (1, 2, 3, 4, 5, 6, 7, 8, 9)])
            entries = Counter(current_list)
            current_set_strings = list()
            current_set_sizes = list()
            for set_string in list(entries.keys()):
                if (set_string.find('var') == -1):
                    current_set_strings.append(set_string)
                    string_enrty_counts = 0
                    for trait_index in [2, 4, 5, 6, 7, 8]:
                        if birds_dataset_strings[bird_index, trait_index] == set_string:
                            string_enrty_counts = string_enrty_counts + 1
                    current_set_sizes.append(string_enrty_counts)
            bigest_subsets.append(sorted(current_set_sizes, key=lambda x:-x)[0])
    bigest_subset_sizes = list()
    for subset_size in range(7):
        bigest_subset_sizes.append(np.sum([x == subset_size for x in bigest_subsets]))
    bigest_subset_sizes = np.array(bigest_subset_sizes)

    # get enhancement subset and its cardinality
    set_enhancement_sizes = np.zeros((nfts_number,))
    set_enhancement_cardinality = np.zeros((nfts_number,))
    for subset_size in range(7):
        indexes = list()
        for bird_index in range(len(birds_dataset)):
            if bigest_subsets[bird_index] == subset_size:
                indexes.append(bird_index)
        for bird_index in indexes:
            current_list = list(birds_dataset_strings[bird_index, (1, 2, 3, 4, 5, 6, 7, 8, 9)])
            entries = Counter(current_list)
            current_set_strings = list()
            current_set_sizes = list()
            current_set_sizes.append(0)
            for set_string in list(entries.keys()):
                if (set_string.find('var') == -1):
                    current_set_strings.append(set_string)
                    string_enrty_counts = 0
                    for trait_index in [2, 4, 5, 6, 7, 8]:
                        if birds_dataset_strings[bird_index, trait_index] == set_string:
                            string_enrty_counts = string_enrty_counts + 1       
                    if string_enrty_counts == bigest_subsets[bird_index]:
                        string_enrty_counts = 0
                        for trait_index in [3, 9]:
                            if birds_dataset_strings[bird_index, trait_index] == set_string:
                                string_enrty_counts = string_enrty_counts + 1
                        for trait_index in [1]:
                            if birds_dataset_strings[bird_index, trait_index] == set_string:
                                string_enrty_counts = string_enrty_counts + 10
                                # print(bigest_subsets[bird_index], birds_dataset_strings[bird_index, 0], birds_dataset_strings[bird_index, 1])
                        current_set_sizes.append(string_enrty_counts)
            set_enhancement_sizes[bird_index] = max(current_set_sizes)
        entries = Counter(set_enhancement_sizes[indexes])
        for bird_index in indexes:
            set_enhancement_cardinality[bird_index] = entries[set_enhancement_sizes[bird_index]]
    # compute scores (make matrices to speed up)
    birds_scores = np.zeros((nfts_number,))    
    for bird_index_1 in range(len(birds_dataset)):
        for bird_index_2 in range(bird_index_1):
            if bigest_subsets[bird_index_1] > bigest_subsets[bird_index_2]:
                birds_scores[bird_index_1] = birds_scores[bird_index_1] + 1
            elif bigest_subsets[bird_index_1] < bigest_subsets[bird_index_2]:
                birds_scores[bird_index_2] = birds_scores[bird_index_2] + 1
            else: # ==
                birds_scores[bird_index_1] = birds_scores[bird_index_1] + set_enhancement_cardinality[bird_index_2]/(
                    set_enhancement_cardinality[bird_index_1] + set_enhancement_cardinality[bird_index_2])
                birds_scores[bird_index_2] = birds_scores[bird_index_2] + set_enhancement_cardinality[bird_index_1]/(
                    set_enhancement_cardinality[bird_index_1] + set_enhancement_cardinality[bird_index_2])
    birds_scores = birds_scores / (nfts_number - 1)
    if normalize:
        birds_scores = birds_scores / np.sum(birds_scores) * nfts_number
    return birds_scores

birds_set_scores = get_set_scores(birds_dataset)

def get_edition_scores(birds_dataset, normalize=True):
    nfts_number = len(birds_dataset)
    borders = [10, 100, 1000]
    
    birds_scores = np.zeros((nfts_number,))
    edition_trait = np.zeros((nfts_number,))
    for current_border in borders:
        edition_trait = edition_trait + (birds_dataset[:, 0] < current_border)
    entries = Counter(edition_trait)
    bird_group_sizes = np.array([entries[x] for x in edition_trait]).reshape((nfts_number, 1))
    keys = entries.keys()
    values = np.array(list(entries.values()))
    groups_number = len(values)
    values = values.reshape((1, len(values)))
    birds_scores = birds_scores + (np.sum(np.divide((values + np.zeros((nfts_number, 1))), (bird_group_sizes + values)), 1) - 1/2) / (groups_number - 1)
    if normalize:
        birds_scores = birds_scores / np.sum(birds_scores) * nfts_number
    return birds_scores

birds_edition_scores = get_edition_scores(birds_dataset)

nfts_number = len(birds_dataset)

birds_trait_ranks = (nfts_number + 1) - ss.rankdata(birds_trait_scores, method='max')
birds_trait_ranks = [int(x) for x in birds_trait_ranks]

birds_set_ranks = (nfts_number + 1) - ss.rankdata(birds_set_scores, method='max')
birds_set_ranks = [int(x) for x in birds_set_ranks]

birds_edition_ranks = (nfts_number + 1) - ss.rankdata(birds_edition_scores, method='max')
birds_edition_ranks = [int(x) for x in birds_edition_ranks]

birds_weighted_scores = (birds_trait_scores + birds_set_scores + birds_edition_scores) / 3
birds_weighted_ranks = (nfts_number + 1) - ss.rankdata(birds_weighted_scores, method='max')
birds_weighted_ranks = [int(x) for x in birds_weighted_ranks]

birds_dataset_with_ranks = np.hstack((birds_dataset_strings, 
                                      np.reshape(birds_trait_scores, (nfts_number, 1)),
                                      np.reshape(birds_trait_ranks, (nfts_number, 1)),
                                      np.reshape(birds_set_scores, (nfts_number, 1)),
                                      np.reshape(birds_set_ranks, (nfts_number, 1)),
                                      np.reshape(birds_edition_scores, (nfts_number, 1)),
                                      np.reshape(birds_edition_ranks, (nfts_number, 1)),
                                      np.reshape(birds_weighted_scores, (nfts_number, 1)),
                                      np.reshape(birds_weighted_ranks, (nfts_number, 1))
                                     ))

schema_sql = f'''
CREATE TABLE IF NOT EXISTS kanbirds_ranks (bird_id int primary key, theme text, head text, eyes text, body text, tail text, wingLeft text, wingRight text, feet text, beak text, trait_score float8, trait_rank int, set_score float8, set_rank int, edition_score float8, edition_rank int, weighted_score float8, weighted_rank int);
'''
kanbirds_ranks_sql = f"INSERT INTO kanbirds_ranks (bird_id, theme, head, eyes, body, tail, wingLeft, wingRight, feet, beak, trait_score, trait_rank, set_score, set_rank, edition_score, edition_rank, weighted_score, weighted_rank) VALUES \n"
for bird in birds_dataset_with_ranks:
	kanbirds_ranks_sql += f"(\'{bird[0]}\', \'{bird[1]}\', \'{bird[2]}\', \'{bird[3]}\', \'{bird[4]}\', \'{bird[5]}\', \'{bird[6]}\', \'{bird[7]}\', \'{bird[8]}\', \'{bird[9]}\', \'{bird[10]}\', \'{bird[11]}\', \'{bird[12]}\', \'{bird[13]}\', \'{bird[14]}\', \'{bird[15]}\', \'{bird[16]}\', \'{bird[17]}\'),\n"
kanbirds_ranks_sql = kanbirds_ranks_sql[:-2] + \
	" ON CONFLICT (bird_id) DO UPDATE SET theme = excluded.theme, head = excluded.head, eyes = excluded.eyes, body = excluded.body, tail = excluded.tail, wingLeft = excluded.wingLeft, wingRight = excluded.wingRight, feet = excluded.feet, beak = excluded.beak, trait_score = excluded.trait_score, trait_rank = excluded.trait_rank, set_score = excluded.set_score, set_rank = excluded.set_rank, edition_score = excluded.edition_score, edition_rank = excluded.edition_rank, weighted_score = excluded.weighted_score, weighted_rank = excluded.weighted_rank;"

result_sql = '\n'.join([schema_sql, kanbirds_ranks_sql])

with open("res_ranks.sql", 'w') as output_file:
    output_file.write(result_sql)