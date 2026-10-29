from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI




app = FastAPI()




@app.get('/')
async def main():
    return {'message':'welcome!'}