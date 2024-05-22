import functions_framework
from flask import jsonify
from google.cloud import language_v1
from google.cloud import bigquery
from typing import Dict

def natural_language(name, text,product):
    client = language_v1.LanguageServiceClient()
    document = language_v1.types.Document(
      content=text, type_=language_v1.types.Document.Type.PLAIN_TEXT
    )
    sentiment = client.analyze_sentiment(request={"document": document}).document_sentiment
    analyze_iter = iter(["name", name ,"product", product, "text", text, "sentiment_score", f"{sentiment.score:.2f}", "sentiment_magnitude", f"{sentiment.magnitude:.2f}"])
    analyze: Dict[str, str] = {}

    for analyze_name in analyze_iter:
        analyze[analyze_name] = next(analyze_iter)

    response_user = ""
    if float(analyze["sentiment_score"]) < -0.5:
        response_user = "We're sorry you didn't like it. We'll work to improve."
    elif float(analyze["sentiment_score"]) >= -0.5 and float(analyze["sentiment_score"]) < 0:
        response_user = "We're sorry it wasn't a good experience for you. We'll work to improve."
    elif float(analyze["sentiment_score"]) >= 0 and float(analyze["sentiment_score"]) < 0.6:
        response_user = "We're glad you enjoyed it! Your feedback is important for us to improve."
    elif float(analyze["sentiment_score"]) >= 0.6:
        response_user = "We're happy to hear you had a great experience."
    
    return analyze,response_user

def write_data_bq(analyzed_text):
    client = bigquery.Client()
    dataset_id = "projeto-estudos-415711.evaluate_product.evaluate"
    QUERY = f"""
        INSERT INTO `{dataset_id}` (Name, Product, Text, Score) VALUES ("{analyzed_text["name"]}","{analyzed_text["product"]}","{analyzed_text["text"]}",{analyzed_text["sentiment_score"]})
    """
    client.query_and_wait(QUERY)

@functions_framework.http
def analyze_webhook(request):
    data = request.get_json()

    print(data)

    tag = data["fulfillmentInfo"]["tag"]
    text = data["text"]
    name = data["sessionInfo"]["parameters"]["name"]["name"]
    product = data["sessionInfo"]["parameters"]["product"]

    analyzed_text, response_user = natural_language(name,text,product)
    write_data_bq(analyzed_text)

    return jsonify(
        {
            'fulfillment_response': {
                'messages': [
                    {
                        'text': {
                            'text': [response_user]
                        }
                    }
                ]
            }
        }
    )