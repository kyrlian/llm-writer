
import asyncio
from typing import AsyncGenerator, Generator

# async def async_wrapper(normal_generator:Generator)-> AsyncGenerator:
#     """ Convert a normal generator to an async generator """
#     async def getnext(normal_generator):
#         try:
#             v = next(normal_generator)
#             return v,True
#         except StopIteration as e:
#             return None, False
        
#     doloop = True
#     while doloop:
#         val, doloop = await asyncio.create_task(getnext(normal_generator))
#         if doloop:
#             yield val


async def async_wrapper(normal_generator:Generator)-> AsyncGenerator:
    async def g(a):
        return a

    for v in normal_generator:
        yield await asyncio.create_task(g(v))