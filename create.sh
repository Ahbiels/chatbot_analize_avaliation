gcloud iam service-accounts create virtual-assistant \
  --description="Service account that will be used in the Cloud Function to access BigQuery" \
  --display-name="Virtual Assistant"

gcloud projects add-iam-policy-binding $DEVSHELL_PROJECT_ID \
  --member="serviceAccount:virtual-assistant@$DEVSHELL_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.admin"

#roles/bigquery.admin

gcloud functions deploy webhook3 \
    --gen2 \
    --runtime=python312 \
    --region=us-east1 \
    --source=./cloud_function \
    --entry-point=analyze_webhook \
    --allow-unauthenticated \
    --trigger-http \
    --service-account virtual-assistant@$DEVSHELL_PROJECT_ID.iam.gserviceaccount.com


#Name, Product, Text, Score
bq mk evaluate_product
bq mk --table $DEVSHELL_PROJECT_ID:evaluate_product.evaluate Name:string,Product:string,Text:string,Score:float