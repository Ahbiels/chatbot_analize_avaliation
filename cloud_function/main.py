import functions_framework
from flask import jsonify
from google.cloud import language_v1
from google.cloud import bigquery
from typing import Dict

def natural_language(text,tag):
    product = tag
    client = language_v1.LanguageServiceClient()
    document = language_v1.types.Document(
      content=text, type_=language_v1.types.Document.Type.PLAIN_TEXT
    )
    sentiment = client.analyze_sentiment(request={"document": document}).document_sentiment
    analyze_iter = iter(["product", product, "text", text, "sentiment_score", f"{sentiment.score:.2f}", "sentiment_magnitude", f"{sentiment.magnitude:.2f}"])
    analyze: Dict[str, str] = {}

    for analyze_name in analyze_iter:
        analyze[analyze_name] = next(analyze_iter)
    
    return analyze

def write_data_bq(analyzed_text):
    client = bigquery.Client()
    dataset_id = "projeto-estudos-415711.data_test.test"
    QUERY = f"""
        INSERT INTO `{dataset_id}` (Product, Text, Score) VALUES ("{analyzed_text["product"]}","{analyzed_text["text"]}",{analyzed_text["sentiment_score"]})
    """
    print(QUERY)
    client.query_and_wait(QUERY)

@functions_framework.http
def analyze_webhook(request):
    data = request.get_json()

    tag = data["fulfillmentInfo"]["tag"]
    text = data["text"]

    analyzed_text = natural_language(text,tag)
    write_data_bq(analyzed_text)

    print(analyzed_text)
    return jsonify(
        {
            'fulfillment_response': {
                'messages': [
                    {
                        'text': {
                            'text': ["Thanks for your rating"]
                        }
                    }
                ]
            }
        }
    )