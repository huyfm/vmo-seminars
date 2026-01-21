import asyncio


async def worker(fut: asyncio.Future):
    print("worker: started")
    result = await fut          # suspend here, waiting on a Future
    print("worker: got", result)
    return result * 2


async def main():
    loop = asyncio.get_running_loop()

    fut = loop.create_future()          # manually create Future
    coro = worker(fut)                  # coroutine object
    task = asyncio.create_task(coro)    # wrap coroutine into Task

    print("main: task created")

    # simulate "event happens later"
    # loop.call_later(1, fut.set_result, 21)

    result = await task                 # await Task (Task is a Future)
    print("main: task result =", result)

asyncio.run(main())
