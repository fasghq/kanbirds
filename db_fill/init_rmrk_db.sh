#!/bin/bash
pg_login="postgres"
pg_pass="1qazwer2"
pg_db_name="rmrk"
pg_host="localhost"
pg_connect="postgresql://$pg_login:$pg_pass@$pg_host/$pg_db_name"
#home_dir="/home/ubuntu"
#cd $home_dir

# wget https://gateway.pinata.cloud/ipns/precon-rmrk2.rmrk.link -O $home_dir/dump_v2.dump

# python $rmrk2psql.py -i $dump_v2.dump -o $output_v2.sql -v

psql "$pg_connect" -f $output_v2.sql