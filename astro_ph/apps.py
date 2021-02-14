# standard library
import asyncio
from dataclasses import dataclass
from typing import AsyncIterable, Awaitable, Callable, Iterable, TypeVar


# type hints
S = TypeVar("S")
T = TypeVar("T")


# helper functions
async def amap(
    afunc: Callable[[S], Awaitable[T]],
    aiterable: AsyncIterable[S],
    n_concurrent: int = 5,
) -> Awaitable[Iterable[T]]:
    """Async map function.

    Args:
        afunc: Coroutine function.
        aiterable: Async iterable that yields args of afunc.
        n_concurrent: Number of concurrent processes.

    Returns:
        Generator that yields results of afunc.

    """
    queue_in = asyncio.Queue()
    queue_out = asyncio.Queue()

    # step 1: create consumer coroutines
    async def consume() -> Awaitable[None]:
        async def _consume() -> Awaitable[None]:
            while True:
                arg = await queue_in.get()
                result = await afunc(arg)
                await queue_out.put(result)
                queue_in.task_done()

        try:
            await _consume()
        except asyncio.CancelledError:
            pass

    consumers = []

    for _ in range(n_concurrent):
        consumer = asyncio.create_task(consume())
        consumers.append(consumer)

    # step 2: create register coroutine
    async def register() -> Awaitable[None]:
        async for arg in aiterable:
            await queue_in.put(arg)

        await queue_in.join()

        for consumer in consumers:
            consumer.cancel()

    # step 3: run coroutines concurrently
    await asyncio.gather(register(), *consumers)

    # step 4: return results as a generator
    def results():
        while not queue_out.empty():
            yield queue_out.get_nowait()

    return results()
