import asyncio
import time

async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main():
    print(f"started at {time.strftime('%X')}")

    await say_after(5, 'hello')
    await say_after(10, 'world')

    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())