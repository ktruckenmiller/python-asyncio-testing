import asyncio
import time
import random

import boto3
from botocore.config import Config
import aioboto3
import aioify
from concurrent.futures import ProcessPoolExecutor

cloudformation = boto3.client('cloudformation')

class SomeObject():
    def __init__(self):

        self.age = 0

# def list_stacks():
#     print('boston')
#     return ()

boston = aioify(obj=cloudformation.list_stacks, name='blahs')

async def worker(name, queue, started_at):
    while True:
        some_obj = await queue.get()

        # async with aioboto3.client('cloudformation', config=Config(retries = {
        #       'max_attempts': 10,
        #       'mode': 'standard'
        #    })) as cf:
        #    await cf.list_stacks()
        await boston()
        queue.task_done()
        print(f'{name} took about {(time.monotonic() - started_at):.2f} seconds')

async def main():
    worker_num = 1
    queue = asyncio.Queue()
    total_sleep_time = 0

    print('Setting up objects')
    for _ in range(worker_num):
        new_thingy = SomeObject()
        new_thingy.age = random.uniform(0.05, 4.0)
        total_sleep_time += new_thingy.age
        queue.put_nowait(new_thingy)

    tasks = []
    started_at = time.monotonic()
    for i in range(worker_num):
        task = asyncio.create_task(worker(f'worker-{i}', queue, started_at))
        tasks.append(task)


    await queue.join()
    total_slept_for = time.monotonic() - started_at

    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()
    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)
    print('====')
    print(f'{worker_num} workers ran tasks for {total_slept_for:.2f} seconds')
    print(f'total expected completion time: {total_sleep_time:.2f} seconds')

asyncio.run(main())
