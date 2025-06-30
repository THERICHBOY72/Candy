from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/chat")
def chat_response(user_message: str):
    responses = {"hello": "Hi there!", "market": "Here’s the latest market data..."}
    return {"response": responses.get(user_message.lower(), "Sorry, I didn't understand that.")}

uvicorn.run(app, host="127.0.0.1", port=8000)