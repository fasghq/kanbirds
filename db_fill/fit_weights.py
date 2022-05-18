import psycopg2
import json
import csv
import numpy as np
import datetime
from pytimeparse.timeparse import timeparse
from scipy.optimize import minimize, LinearConstraint

conn = psycopg2.connect(
   database="rmrk", user='postgres', password='1qazwer2', host='127.0.0.1', port='5432'
)

conn.autocommit = True
cursor = conn.cursor()

cursor.execute('''SELECT * from deals_train''')
pairwise_deals_train = cursor.fetchall();
pairwise_deals_train = [list(i) for i in pairwise_deals_train]

cursor.execute('''SELECT * from deals_test''')
pairwise_deals_test = cursor.fetchall();
pairwise_deals_test = [list(i) for i in pairwise_deals_test]

cursor.execute('''SELECT * from kanbirds_ranks''')
birds_dataset_with_ranks = cursor.fetchall();
birds_dataset_with_ranks = [list(i) for i in birds_dataset_with_ranks]

cursor.execute('''SELECT * from kanbirds''')
birds_dataset_strings = np.array(cursor.fetchall());

conn.commit()
conn.close()

days = 7
int_columns = [0, 1, 2, 3]
numeric_columns = [5, 6, 7]
time_columns = [4]

time_delta_seconds = days * 24 * 60 * 60

column_indexes = [10, 12, 14, 16]
scores = [[x[i] for i in column_indexes] for x in birds_dataset_with_ranks]
scores = np.array(scores)

def kernel_epanechnikov(time_deltas, days_width=7):
    time_delta_seconds = days_width * 24 * 60 * 60
    kernel_values = np.zeros(len(time_deltas))
    for index in range(len(time_deltas)):
        kernel_values[index] = max(1 - (abs(timeparse(time_deltas[index])) / time_delta_seconds) ** 2, 0)
    return kernel_values

time_deltas_train = [x[4] for x in pairwise_deals_train]

kernal_values_train = kernel_epanechnikov(time_deltas_train)
kernal_values_train = np.array(kernal_values_train)

time_deltas_test = [x[4] for x in pairwise_deals_test]

kernal_values_test = kernel_epanechnikov(time_deltas_test)
kernal_values_test = np.array(kernal_values_test)

relatile_log_price_train = [np.log(float(x[-2]) / float(x[-1])) for x in pairwise_deals_train]
relatile_log_price_train = np.array(relatile_log_price_train)

relatile_log_price_test = [np.log(float(x[-2]) / float(x[-1])) for x in pairwise_deals_test]
relatile_log_price_test = np.array(relatile_log_price_test)

pair_indexes_train = np.array([x[:2] for x in pairwise_deals_train])
pair_indexes_test = np.array([x[:2] for x in pairwise_deals_test])

def m(x, w):
    """Weighted Mean"""
    return np.sum(x * w) / np.sum(w)

def cov(x, y, w):
    """Weighted Covariance"""
    return np.sum(w * (x - m(x, w)) * (y - m(y, w))) / np.sum(w)

def corr(x, y, w):
    """Weighted Correlation"""
    return cov(x, y, w) / np.sqrt(cov(x, x, w) * cov(y, y, w))

def get_accuracy(scores_combination, 
                 pair_indexes=pair_indexes_train, 
                 relatile_log_price=relatile_log_price_train, 
                 kernal_values=kernal_values_train):
    return corr(np.log((1 + scores_combination[pair_indexes[:, 0]]) / 
                              (1 + scores_combination[pair_indexes[:, 1]])), relatile_log_price, kernal_values)

def objective(coefficients, scores=scores[:, :3]):
    coefficients = np.append(coefficients, (1 - coefficients[0] - coefficients[1]))
    return -get_accuracy(np.matmul(scores, coefficients))

def get_accuracy_test(scores_combination):
    return get_accuracy(scores_combination, pair_indexes_test, relatile_log_price_test, kernal_values_test)

def objective_test(coefficients, scores=scores[:, :3]):
    coefficients = np.append(coefficients, (1 - coefficients[0] - coefficients[1]))
    return -get_accuracy_test(np.matmul(scores, coefficients))

birds_trait_scores = np.array([float(x[-8]) for x in birds_dataset_with_ranks])
birds_set_scores = np.array([float(x[-6]) for x in birds_dataset_with_ranks])
birds_edition_scores = np.array([float(x[-4]) for x in birds_dataset_with_ranks])

birds_weighted_normalized_scores = (birds_trait_scores + birds_set_scores + birds_edition_scores) / 3

linear_constraint = LinearConstraint([[1, 0], [0, 1], [1, 1]], [0, 0, 0], [1, 1, 1])

x0 = [1/3, 1/3]
res = minimize(objective, x0, constraints=linear_constraint, options={'disp': True}) # method='nelder-mead',
coefficents = res.x
coefficents = np.append(coefficents, 1 - np.sum(res.x))

set_size = 10
x0_points = list()
x_points = list()
y_points = list()
for iteration in range(set_size):
    boundaries = sorted([np.random.rand(), np.random.rand()])
    x0 = [boundaries[0], boundaries[1] - boundaries[0]]
    x0_points.append(x0)
    res = minimize(objective, x0, constraints=linear_constraint, options={'disp': True})
    x_current = res.x
    y_current = res.fun
    x_points.append(x_current)
    y_points.append(y_current)

minimum_index = np.argmin(y_points)
optimal_weekly_x = x_points[minimum_index]

def score_from_coefficients(coefficients):
    return birds_trait_scores * coefficients[0] + birds_set_scores * coefficients[1] + birds_edition_scores * (1 - coefficients[0] - coefficients[1])

birds_weighted_normalized_scores = (birds_trait_scores / np.mean(birds_trait_scores)) + (
                                    birds_set_scores / np.mean(birds_set_scores)) + (
                                    birds_edition_scores / np.mean(birds_edition_scores))

week_trade_score = score_from_coefficients(optimal_weekly_x) 

nfts_number = len(birds_dataset_with_ranks)
birds_dataset_with_ranks = np.hstack((birds_dataset_with_ranks, 
                                      np.reshape(birds_weighted_normalized_scores, (nfts_number, 1)),
                                      np.reshape(week_trade_score, (nfts_number, 1))
                                     ))

schema_sql = f'''
CREATE TABLE IF NOT EXISTS kanbirds_fitted (bird_id int primary key, theme text, head text, eyes text, body text, tail text, wingLeft text, wingRight text, feet text, beak text, trait_score float8, trait_rank int, set_score float8, set_rank int, edition_score float8, edition_rank int, weighted_score float8, weighted_rank int, birds_weighted_normalized_scores float8, week_trade_score float8);
'''
kanbirds_fitted_sql = f"INSERT INTO kanbirds_fitted (bird_id, theme, head, eyes, body, tail, wingLeft, wingRight, feet, beak, trait_score, trait_rank, set_score, set_rank, edition_score, edition_rank, weighted_score, weighted_rank, birds_weighted_normalized_scores, week_trade_score) VALUES \n"
for bird in birds_dataset_with_ranks:
	kanbirds_fitted_sql += f"(\'{bird[0]}\', \'{bird[1]}\', \'{bird[2]}\', \'{bird[3]}\', \'{bird[4]}\', \'{bird[5]}\', \'{bird[6]}\', \'{bird[7]}\', \'{bird[8]}\', \'{bird[9]}\', \'{bird[10]}\', \'{bird[11]}\', \'{bird[12]}\', \'{bird[13]}\', \'{bird[14]}\', \'{bird[15]}\', \'{bird[16]}\', \'{bird[17]}\', \'{bird[18]}\', \'{bird[19]}\'),\n"
kanbirds_fitted_sql = kanbirds_fitted_sql[:-2] + \
	" ON CONFLICT (bird_id) DO UPDATE SET theme = excluded.theme, head = excluded.head, eyes = excluded.eyes, body = excluded.body, tail = excluded.tail, wingLeft = excluded.wingLeft, wingRight = excluded.wingRight, feet = excluded.feet, beak = excluded.beak, trait_score = excluded.trait_score, trait_rank = excluded.trait_rank, set_score = excluded.set_score, set_rank = excluded.set_rank, edition_score = excluded.edition_score, edition_rank = excluded.edition_rank, weighted_score = excluded.weighted_score, weighted_rank = excluded.weighted_rank, birds_weighted_normalized_scores = excluded.birds_weighted_normalized_scores, week_trade_score = excluded.week_trade_score;"

result_sql = '\n'.join([schema_sql, kanbirds_fitted_sql])

with open("res_fitted.sql", 'w') as output_file:
    output_file.write(result_sql)