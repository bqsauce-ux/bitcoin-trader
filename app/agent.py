from chroma_db import collection
from openai import OpenAI

client = OpenAI()

def ask_agent(question):

    # 1. Search ChromaDB
    results = collection.query(
        query_texts=[question],
        n_results=3
    )

    documents = results["documents"][0]

    context = "\n".join(documents)

    # 2. Send retrieved context to LLM
    prompt = f"""
You are an AI assistant.

Use the following information to answer the user's question.

Context:
{context}

Question:
{question}

Answer clearly and accurately.
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return response.output_text