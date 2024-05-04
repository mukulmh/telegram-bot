from fastapi import FastAPI, Request
from pydantic import BaseModel
from celery_config import send_message_to_group

app = FastAPI()

class MessageData(BaseModel):
    api_token: str
    group_id: str
    message: str

@app.post("/send_message")
async def handle_send_message(data: MessageData):
    task = send_message_to_group.apply_async(
        args=(data.api_token, data.group_id, data.message)
    )
    return {"task_id": task.id}

@app.get("/")
async def home(request: Request):
    return {"message": "Success"}

# To run the FastAPI application, use the following command in the terminal:
# uvicorn app:app --host 0.0.0.0 --port 8000
