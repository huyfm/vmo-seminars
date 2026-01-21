from fastapi import FastAPI
import httpx


app = FastAPI()
client = httpx.Client()
async_client = httpx.AsyncClient()


@app.get("/xkcd/non-blocking")
# non-blocking async/await
async def get_xkcd_image_sync(i: int) -> dict:
    resp = await async_client.get(f"https://xkcd.com/{i}/info.0.json")
    return resp.json()


@app.get("/xkcd/blocking")
# multithreading
def get_xkcd_image_async(i: int) -> dict:
    resp = client.get(f"https://xkcd.com/{i}/info.0.json")
    return resp.json()


@app.get("/xkcd/cpu-bound")
# multithreading
async def increase_i(i: int) -> dict:
    for _ in range(100):
        i += 1
    return {"result": i}
