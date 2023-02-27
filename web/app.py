import os
import json
from pprint import pprint

from flask import Flask, render_template, jsonify, request
from elasticsearch import Elasticsearch
from bert_serving.client import BertClient
SEARCH_SIZE = 10
INDEX_NAME = os.environ['INDEX_NAME']
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def analyzer():
    print("inside search......")
    # bc = BertClient(ip='localhost', port=5555, output_fmt='list')
    bc = BertClient(ip='bertserving', output_fmt='list')
    # client = Elasticsearch('http://localhost:9200')
    client = Elasticsearch('http://elasticsearch:9200')
    resp = client.info()
    print(resp)
    # print("client")
    
    query = request.args.get('q')
    
    query_vector = bc.encode([query])[0]
    print(query_vector)

    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'text_vector') + 1.0",
                "params": {"query_vector": query_vector}
            }
        }
    }


    response = client.search(
        index=INDEX_NAME,
        query=script_query,
        size=10,
        source_includes=["title", "text"]
    )
    
    print("query is:")
    print(query)
    print("response is:")
    pprint(response)
    print(type(response))
    res = dict(response)
    return jsonify(res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5100)