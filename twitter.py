import requests
import os
import json
import pandas as pd
import sys
from fileinput import filename
from google.cloud import bigquery

import logging
from sys import stdout
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as f

bearer_token = ''
search_url = "https://api.twitter.com/2/tweets/search/recent"
max_results = "?max_results="
qtd_results = "50"
search_url_50 = search_url + max_results + qtd_results

query_params_palavras = {'query': 'Boticário maquiagem','expansions':'author_id','user.fields':'username,description'}
query_params_twitts_50 = {'query': 'Boticário','expansions':'author_id','user.fields':'username,description'}
query_params_twitts_port = {'query': 'Boticário lang:pt','expansions':'author_id','user.fields':'username,description'}

table_words = 'raw.tb_twitter_words'
table_portugues = 'raw.tb_twitter_portugues'
table_50 = 'raw.tb_twitter_50_recentes'
field_name = 'author_id'

p_tipo = sys.argv[1]


def config_log(flag_stdout=True, flag_logfile=False):
    handler_list = list()
    LOGGER = logging.getLogger(__name__)

    [LOGGER.removeHandler(h) for h in LOGGER.handlers]

    if flag_logfile:
        path_log = './logs/{}_{:%Y%m%d}.log'.format('log', datetime.now())
        if not os.path.isdir('./logs'):
            os.makedirs('./logs')
        handler_list.append(logging.FileHandler(path_log))

    if flag_stdout:
        handler_list.append(logging.StreamHandler(stdout))
        
    logging.basicConfig(
        level=logging.INFO\
        ,format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'\
        ,handlers=handler_list)    
    return LOGGER

log = config_log()

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    if response.status_code != 200:
       raise Exception(response.status_code, response.text)
    return json.loads(response.text)


def save(df,table_id,field_name):
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(schema=[
                 bigquery.SchemaField(field_name, "STRING"),
				 ], write_disposition="WRITE_TRUNCATE")
    client.load_table_from_dataframe(df, table_id, job_config=job_config)

def trata_reponse(search_url,query_params_palavras):
    log.info('iniciando')
    response = connect_to_endpoint(search_url, query_params_palavras)
    data_norm = pd.json_normalize(response['data'])
    users_norm = pd.json_normalize(response['includes']['users'])
    
    df_data=pd.DataFrame(data_norm)
    del df_data['id']
    
    df_users=pd.DataFrame(users_norm)
    del df_users['description']
    del df_users['username']
    df_users = df_users.rename(columns={'id': 'author_id'})
    
    df_final = df_data.merge(df_users, how='left', on=['author_id'])
    
    return df_final

def orquestrador_portugues():
    df_final = trata_reponse(search_url,query_params_twitts_port)
    return df_final

def orquestrador_palavras():
    df_final = trata_reponse(search_url,query_params_palavras)
    return df_final

def orquestrador_50():
    df_final = trata_reponse(search_url_50,query_params_twitts_50)
    return df_final
    
def main():
    print(p_tipo)
    if p_tipo=='palavras':
        log.info('palavras')
        df_palavras=orquestrador_palavras()
        save(df_palavras,table_words,field_name)
    elif p_tipo == '50':
        log.info('50')
        df_50=orquestrador_50()
        save(df_50,table_50,field_name)
    elif p_tipo == 'portugues':
        log.info('PORTUGUES')
        df_portugues=orquestrador_portugues()
        save(df_portugues,table_portugues,field_name)
    else:
        log.warning(f'Paraâmetro inválido:{p_tipo}')

if __name__ == '__main__':
    spark = SparkSession.Builder()\
                       .appName("Twitter")\
					   .getOrCreate() 
    main()

