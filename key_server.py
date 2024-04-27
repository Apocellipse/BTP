from fastapi import FastAPI
from pydantic import BaseModel
import redis
import uvicorn

app = FastAPI()
rc = redis.Redis(host='redis_server', port=6379)

class Item(BaseModel):
    username: str
    public_key: str

@app.get('/get_public_key')
async def get_public_key(username: str):
    public_key = rc.get(username)
    if public_key:
        return {'public_key': public_key.decode()}
    else:
        return {'error': 'Public key not found for the specified user'}

@app.post('/upload_public_key')
async def upload_public_key(item: Item):
    user = item.username
    public_key = item.public_key

    rc.set(user, public_key)

    return {'message': 'Public key uploaded successfully'}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5050)
