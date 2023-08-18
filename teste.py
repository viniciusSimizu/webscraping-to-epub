import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing.pool import Pool, ThreadPool
import time


def func(value: int) -> int:
    time.sleep(value)


async def main() -> None:
    values = range(7)

    with ProcessPoolExecutor(3) as pool:
        start = time.perf_counter()
        for _ in pool.map(func, values):
            end = time.perf_counter()
            print(end - start)


asyncio.run(main())
