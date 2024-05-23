#!/bin/bash

#Realizar o login dentro da Google Cloud Platform
gcloud auth login

#Visualiza a configuração ativa
gcloud config list

#Cria uma Service Account
gcloud iam service-accounts create virtual-assistant \
  --description="Service account that will be used in the Cloud Function to access BigQuery" \
  --display-name="Virtual Assistant"

#Estabelece uma role para essa service account
gcloud projects add-iam-policy-binding $DEVSHELL_PROJECT_ID \
  --member="serviceAccount:virtual-assistant@$DEVSHELL_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.admin"

#Cria um dataset e uma tabela dentro do BihQuery com os seguintes schemas: Name, Product, Text e Score
bq mk evaluate_product
bq mk --table $DEVSHELL_PROJECT_ID:evaluate_product.evaluate Name:string,Product:string,Text:string,Score:float

#Cria uma Cloud function com a runtime em Python3.12, usando o código desse repositório e a service account criada anteriormente 
gcloud functions deploy webhook \
    --gen2 \
    --runtime=python312 \
    --region=us-east1 \
    --source=./cloud_function \
    --entry-point=analyze_webhook \
    --trigger-http \
    --service-account virtual-assistant@$DEVSHELL_PROJECT_ID.iam.gserviceaccount.com

gcloud config set compute/region us-east1
gcloud functions list
gcloud functions describe webhook --region us-east1