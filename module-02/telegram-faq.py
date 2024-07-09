from elasticsearch import Elasticsearch
from telegram.ext import *
from asyncio import Queue
from openai import OpenAI
import logging
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
)

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



def build_prompt(query, search_results):
    prompt_template = """
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT: 
{context}
""".strip()

    context = ""
    
    for doc in search_results:
        context = context + f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}\n\n"
    
    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt

def llm(prompt, model):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    
    return response.choices[0].message.content

def rag(query, model="phi3"):
    search_results = elastic_search(query)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt, model)
    return answer

async def start(update, context):
    await update.message.reply_text('Hello! Send me a question about Data Talks Zoomcamps.')

async def handle_message(update, context):
    user_message = update.message.text
    rag_response = rag(user_message)
    await update.message.reply_text(rag_response)

def main():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling(1.0)
if __name__ == '__main__':
    main()
