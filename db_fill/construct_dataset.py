import psycopg2
import json
import csv
import datetime
import numpy as np
import matplotlib.pyplot as plt


conn = psycopg2.connect(
   database="rmrk", user='postgres', password='1qazwer2', host='127.0.0.1', port='5432'
)

conn.autocommit = True
cursor = conn.cursor()

cursor.execute('''SELECT * from birds_tradedata''')
trade_events = cursor.fetchall();
trade_events = [list(i) for i in trade_events]

cursor.execute('''SELECT * from kanbirds_alias''')
birds_dataset = np.array(cursor.fetchall());

cursor.execute('''SELECT * from kanbirds''')
birds_dataset_strings = np.array(cursor.fetchall());

conn.commit()
conn.close()

for x in trade_events:
    if x[4][4] == '-':
        x[4] = x[4][:10] + ' ' + x[4][11:19]
        x[4] = datetime.datetime.strptime(x[4], '%Y-%m-%d %H:%M:%S')
    else:
        x[4] = datetime.datetime.strptime(
        	datetime.datetime.utcfromtimestamp(int(x[4][:10])).strftime('%Y-%m-%d %H:%M:%S'),
            '%Y-%m-%d %H:%M:%S')
    assert type(x[4]) != 'str'
    assert type(x[4]) != 'numpy.str_'
trade_events = [[int(x[0]), int(x[1]), float(x[2]), int(x[3]),  x[4]] for x in trade_events]
assert all([type(x[4]) != 'str' for x in trade_events])

for x in trade_events:
    if x[2] < 1:
        print(x)
print('-'*50)
for x in trade_events:
    if x[0] == 6762:
        print(x)

trade_events.remove([6762, 7723, 0.01, 9104828, datetime.datetime(2021, 9, 6, 8, 46, 42)])
trade_events.remove([6762, 7723, 0.01, 9104851, datetime.datetime(2021, 9, 6, 8, 49)])

print(datetime.date.fromisoformat('2021-11-01'))
boundary_date = datetime.datetime.fromisoformat('2021-11-01')
print(np.sum([x[4] >= boundary_date for x in trade_events]))

boundary_date = datetime.datetime.fromisoformat('2021-11-01')
test_indexes = list()
train_indexes = list()
for trade_event_index in range(len(trade_events)):
    if (trade_events[trade_event_index][4] < boundary_date):
        train_indexes.append(trade_event_index)
    else:
        test_indexes.append(trade_event_index)
print(len(train_indexes), len(test_indexes))

collection_size = len(birds_dataset)
train_events_count = len(train_indexes)
test_events_count = len(test_indexes)
pairwise_deals_train = list()
pairwise_deals_test = list()
days = 7
maximum_time_delta = datetime.timedelta(days=days)
for event_index_1 in range(train_events_count):
    event_1 = train_indexes[event_index_1]
    bird_index_1 = trade_events[event_1][0]
    bird_id_1 = trade_events[event_1][1]
    for event_index_2 in range(event_index_1 + 1, train_events_count):
        event_2 = train_indexes[event_index_2]
        bird_index_2 = trade_events[event_2][0]
        bird_id_2 = trade_events[event_2][1]
        if bird_index_1 != bird_index_2:
            time_between_deals = trade_events[event_2][4] - trade_events[event_1][4]
            if abs(time_between_deals) <= maximum_time_delta:
                prices = [trade_events[event_1][2], trade_events[event_2][2]]
                log_price_ratio = np.log10(trade_events[event_2][2] / trade_events[event_1][2])
                pairwise_deals_train.append([bird_index_1, bird_index_2, bird_id_1, bird_id_2, time_between_deals, log_price_ratio, trade_events[event_1][2], trade_events[event_2][2]])
                
for event_index_1 in range(test_events_count):
    event_1 = test_indexes[event_index_1]
    bird_index_1 = trade_events[event_1][0]
    bird_id_1 = trade_events[event_1][1]
    for event_index_2 in range(event_index_1 + 1, test_events_count):
        event_2 = test_indexes[event_index_2]
        bird_index_2 = trade_events[event_2][0]
        bird_id_2 = trade_events[event_2][1]
        if bird_index_1 != bird_index_2:
            time_between_deals = trade_events[event_2][4] - trade_events[event_1][4]
            if abs(time_between_deals) <= maximum_time_delta:
                prices = [trade_events[event_1][2], trade_events[event_2][2]]
                log_price_ratio = np.log10(trade_events[event_2][2] / trade_events[event_1][2])
                pairwise_deals_test.append([bird_index_1, bird_index_2, bird_id_1, bird_id_2, time_between_deals, log_price_ratio, trade_events[event_1][2], trade_events[event_2][2]])
        
schema_sql = f'''
CREATE TABLE IF NOT EXISTS deals_train (bird_index_1 int, bird_index_2 int, bird_id_1 int, bird_id_2 int, time_between_deals text, log_price_ratio float8, price_1 float8, price_2 float8);
CREATE UNIQUE INDEX IF NOT EXISTS idx_deals_train ON deals_train (bird_id_1, bird_id_2, time_between_deals);
CREATE TABLE IF NOT EXISTS deals_test (bird_index_1 int, bird_index_2 int, bird_id_1 int, bird_id_2 int, time_between_deals text, log_price_ratio float8, price_1 float8, price_2 float8);
CREATE UNIQUE INDEX IF NOT EXISTS idx_deals_test ON deals_test (bird_id_1, bird_id_2, time_between_deals);
'''

deals_train_sql = f"INSERT INTO deals_train (bird_index_1, bird_index_2, bird_id_1, bird_id_2, time_between_deals, log_price_ratio, price_1, price_2) VALUES \n"
for deal in pairwise_deals_train:
	deals_train_sql += f"(\'{deal[0]}\', \'{deal[1]}\', \'{deal[2]}\', \'{deal[3]}\', \'{deal[4]}\', \'{deal[5]}\', \'{deal[6]}\', \'{deal[7]}\'),\n"
deals_train_sql = deals_train_sql[:-2] + \
	" ON CONFLICT (bird_id_1, bird_id_2, time_between_deals) DO UPDATE SET bird_index_1 = excluded.bird_index_1, bird_index_2 = excluded.bird_index_2, log_price_ratio = excluded.log_price_ratio, price_1 = excluded.price_1, price_2 = excluded.price_2;"

deals_test_sql = f"INSERT INTO deals_test (bird_index_1, bird_index_2, bird_id_1, bird_id_2, time_between_deals, log_price_ratio, price_1, price_2) VALUES \n"
for deal in pairwise_deals_test:
	deals_test_sql += f"(\'{deal[0]}\', \'{deal[1]}\', \'{deal[2]}\', \'{deal[3]}\', \'{deal[4]}\', \'{deal[5]}\', \'{deal[6]}\', \'{deal[7]}\'),\n"
deals_test_sql = deals_test_sql[:-2] + \
	" ON CONFLICT (bird_id_1, bird_id_2, time_between_deals) DO UPDATE SET bird_index_1 = excluded.bird_index_1, bird_index_2 = excluded.bird_index_2, log_price_ratio = excluded.log_price_ratio, price_1 = excluded.price_1, price_2 = excluded.price_2;"

result_sql = '\n'.join([schema_sql, deals_train_sql, deals_test_sql])

with open("res_dataset.sql", 'w') as output_file:
    output_file.write(result_sql)
