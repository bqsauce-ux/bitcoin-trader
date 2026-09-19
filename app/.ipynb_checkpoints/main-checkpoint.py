from fastapi import FastAPI
from pydantic import BaseModel
from agent import ask_agent

app = FastAPI()


class ChatRequest(BaseModel):
    question: str


@app.post("/chat")
def chat(request: ChatRequest):

    answer = ask_agent(request.question)

    return {
        "question": request.question,
        "answer": answer
    }