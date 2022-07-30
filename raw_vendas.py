from fileinput import filename
from google.cloud import bigquery
from google.cloud import storage
import pandas
from google.oauth2 import service_account

import logging
from sys import stdout
from datetime import datetime
import os

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

bucket = client.get_bucket(BUCKET_NAME)
raw_table_name = 'raw.tb_vendas'
raw_field_name = 'MARCA'
prefix_files_bucket = 'files/Base'


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
	

def read_source(prefix_files_bucket):
    list_temp_raw = []
    filename = list(bucket.list_blobs(prefix= prefix_files_bucket))

    for name in filename:
        filename = name.name
        temp = pandas.read_excel('gs://'+BUCKET_NAME+'/'+filename)
        list_temp_raw.append(temp)

    df = pandas.concat(list_temp_raw)
    return df
	
	
def save_bq(df,table_id,field_name):
    client = bigquery.Client()
    job_config = bigquery.LoadJobConfig(schema=[
                 bigquery.SchemaField(field_name, "STRING"),
				 ], write_disposition="WRITE_TRUNCATE")
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
	

def main():
    log = config_log()
    log.info('reading source - xlsx')
    df_raw = read_source(prefix_files_bucket)
    log.info('saving raw.tb_vendas')
    try:
       save_bq(df_raw, raw_table_name, raw_field_name)
    except Exception as e:   
        raise (f'Erro ao gravar dados no BigQuery: {e}') 
		
    log.info('finalizando ingestão raw.tb_vendas')
   
if __name__ == '__main__':
    main()
