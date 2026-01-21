import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count
from typing import Callable

import httpx

async_client = httpx.AsyncClient()


async def benchmark(fetch_many: Callable, n: int):
    tik = time.perf_counter()
    results = await fetch_many(n)
    tok = time.perf_counter()

    num_drop = 0
    with open(f"xkcd_{fetch_many.__name__}.txt", "w") as f:
        for r in results:
            num_drop += (len(r) == 0)
            f.write(r)

    avg_dur = (tok - tik) / n

    print(f"iter: {n:4d} | avg_time: {avg_dur:.2f} | drop: {num_drop}")


def fetch(i: int) -> str:
    try:
        resp = httpx.get(f"https://xkcd.com/{i}/info.0.json")
    except httpx.ConnectTimeout:
        return ""

    if resp.status_code == 200:
        body = resp.json()
        title = body["safe_title"]
        line = f"{i}-{title}\n"
        return line
    return ""


async def fetch_many(n: int) -> list[str]:
    results: list[str] = []
    for i in range(1, n + 1):
        r = fetch(i)
        results.append(r)
    return results


async def fetch_many_mp(n: int) -> list[str]:
    with Pool(cpu_count()) as p:
        results = p.map(fetch, range(1, n + 1))
    return results


async def fetch_many_mt(n: int) -> list[str]:
    with ThreadPoolExecutor(max_workers=cpu_count()) as pool:
        results = pool.map(fetch, range(1, n + 1))
    return list(results)


async def fetch_async(i: int) -> str:
    try:
        resp = await async_client.get(f"https://xkcd.com/{i}/info.0.json")
    except httpx.ConnectTimeout:
        return ""

    if resp.status_code == 200:
        body = resp.json()
        title = body["safe_title"]
        line = f"{i}-{title}\n"
        return line
    return ""


async def fetch_many_async(n: int) -> list[str]:
    results = await asyncio.gather(*[fetch_async(i) for i in range(1, n + 1)])
    return results


async def main():
    n = 500

    print("=== fetch_sync ===")
    await benchmark(fetch_many, 40)
    print()

    print("=== fetch_sync_mp === ")
    await benchmark(fetch_many_mp, n)
    print()

    print("=== fetch_sync_mt === ")
    await benchmark(fetch_many_mt, n)
    print()

    print("=== fetch_async_xkcd ===")
    await benchmark(fetch_many_async, n)
    print()


if __name__ == "__main__":
    asyncio.run(main())
