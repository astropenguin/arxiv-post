# stanard library
import asyncio
from typing import AsyncIterable, Awaitable


# third-party packages
from astro_ph.apps import amap


# test functions
def test_amap() -> None:
    async def arange(maximum: int) -> AsyncIterable[int]:
        for number in range(maximum):
            yield number

    async def afunc(number: int) -> Awaitable[int]:
        return number * 2

    async def main() -> Awaitable[None]:
        result = set(await amap(afunc, arange(5)))
        expected = set(i * 2 for i in range(5))
        assert result == expected

    asyncio.run(main())
