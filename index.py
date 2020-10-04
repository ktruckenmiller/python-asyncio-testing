import asyncio
import time
import random

import boto3
from botocore.config import Config

from asgiref.sync import sync_to_async




class SomeObject():
    def __init__(self):
        self.cf = boto3.client('cloudformation')
        self.age = 0

@sync_to_async
def list_stacks(some_obj):
    print(f'Age of this guy {some_obj.age:2f}')
    return some_obj.cf.list_stacks()


async def worker(name, queue, started_at):
    while True:
        some_obj = await queue.get()

        await list_stacks(some_obj)
        queue.task_done()
        print(f'{name} took about {(time.monotonic() - started_at):.2f} seconds')

async def main():
    worker_num = 100
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
