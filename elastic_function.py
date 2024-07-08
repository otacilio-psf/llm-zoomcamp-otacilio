from elasticsearch import Elasticsearch
es_client = Elasticsearch('http://localhost:9200')
index_name = "course-questions"

def elastic_search(query, size=5, query_filter=False):
    search_query = {
        "size": size,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^4", "text"],
                        "type": "best_fields"
                    }
                }
            }
        }
    }

    if query_filter:
        search_query['query']['bool'].update(query_filter)

    response = es_client.search(index=index_name, body=search_query)
    
    result_docs = []
    
    for hit in response['hits']['hits']:
        hit['_source']['_score'] = hit['_score']
        result_docs.append(hit['_source'])
    
    return result_docs