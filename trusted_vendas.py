from fileinput import filename
from google.cloud import bigquery
from google.cloud import storage
import pandas
from google.oauth2 import service_account

import logging
from sys import stdout
from datetime import datetime
import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as f


credentials_dict = {
  "type": "service_account",
  "project_id": "teste-gcp-2022",
  "private_key_id": "xxxxxxxxxdae8a1978c4c9182ddd4f28xxxxxxx",
  "private_key": "-----BEGIN PRIVATE KEY-----\nxxxxxxDANBgkqhkio/d5g8xxxxxxxxxxxxxxx==\n-----END PRIVATE KEY-----\n",
  "client_email": "account-service@teste-gcp-2022.iam.gserviceaccount.com",
  "client_id": "xxxxxx6422137808xxxxx",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/account-service%40teste-gcp-2022.iam.gserviceaccount.com"
}

BUCKET_NAME = 'gcp_gb'
credentials = service_account.Credentials.from_service_account_info(credentials_dict)
client = storage.Client(project = 'teste-gcp-2022',credentials=credentials)

trusted_table_name = 'trusted.tb_vendas'
trusted_field_name = 'marca'
raw_table_name = 'raw.tb_vendas'
bucket_temp = 'gs://gcp_gb/temp'

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

def save(df, bucket_temp, table_name):
     df.write\
       .format("bigquery")\
       .option("writeMethod", "direct")\
	   .option("temporaryGcsBucket",bucket_temp)\
	   .mode("overwrite")\
       .save(table_name)
	   
	   
	  
def read_table(table_name):
    df =  spark.read.format('bigquery')\
               .option('table', table_name)\
               .option("parentProject", "teste-gcp-2022")\
               .load()
    return df

def convert_columns_name_uppercase(df):
	df = df.select([f.col(x).alias(x.lower()) for x in df.columns])
	return df

def transform_vendas(df):
    df_vendas = df.withColumnRenamed('data_venda','data_venda_old')\
	              .withColumn('mes_venda', f.month(f.col('data_venda_old')))\
	              .withColumn('ano_venda', f.year(f.col('data_venda_old')))\
				  .withColumn('data_venda', f.date_format(f.col('data_venda_old'),"yyyy-MM-dd"))\
				  .drop(f.col('data_venda_old'))\
				  .distinct()
    return df_vendas

def orquestrador(df):
    df = convert_columns_name_uppercase(df)
    df_vendas = transform_vendas(df)
    del df
    return df_vendas
	
	
def is_empty_dataframe(df):
    total = df.select(f.col('id_marca')).count()
    return True if total == 0 else False
	
	
def main():
    log = config_log()
    log.info('reading table raw.tb_vendas')
    df_raw = read_table(raw_table_name)
    df_final = orquestrador(df_raw)
    empty_dataframe = is_empty_dataframe(df_final)
	
    if (empty_dataframe == False):
        log.info('saving trusted.tb_vendas')
        try:
            save(df_final, bucket_temp, trusted_table_name)
        except Exception as e:   
            raise (f'Erro ao gravar dados no BigQuery: {e}') 
    else:
        log.warning('Dataframe vazio!')
	
    log.info('finalizando ingestão trusted.tb_vendas')

if __name__ == '__main__':
    spark = SparkSession.Builder()\
                       .appName("Trusted - vendas")\
					   .getOrCreate() 
    main()
