# anasegatelli
# anasegatelli

# Ingestão excel Vendas

## Raw Vendas

'''
gcloud dataproc jobs wait job-raw-vendas --project teste-gcp-2022 --region us-central1
'''

## Trusted Vendas

'''
gcloud dataproc jobs wait job-trusted_vendas --project teste-gcp-2022 --region us-central1
'''

## Agregação Vendas Ano/Mes

'''
gcloud dataproc jobs wait job-refined-vendas-ano-mes --project teste-gcp-2022 --region us-central1
'''

## Agregação Vendas marca/Ano/Mes

'''
gcloud dataproc jobs wait job-refined-vendas-marca-ano-mes --project teste-gcp-2022 --region us-central1
'''

## Agregação Vendas Linha/Ano/Mes

'''
gcloud dataproc jobs wait job-refined_vendas_linha_ano_mes --project teste-gcp-2022 --region us-central1
'''

## Agregação Vendas Marca/Linha

'''
gcloud dataproc jobs wait job-refined_vendas_marca_linha --project teste-gcp-2022 --region us-central1
'''

# Ingestão Twitter

## Busca por palavras
'''
gcloud dataproc jobs wait job-twitter-palavras --project teste-gcp-2022 --region us-central1
'''

## Busca por 50 recentes
'''
gcloud dataproc jobs wait job-twitter-50 --project teste-gcp-2022 --region us-central1
'''

## Busca por twitts em português
'''
gcloud dataproc jobs wait job-twitter-portugues --project teste-gcp-2022 --region us-central1
'''