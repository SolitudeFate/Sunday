import asyncio
import sys

finished = False
buffer = ''
cursor = 0

MIN_INTERVAL = 1
MAX_INTERVAL = 200


async def wait(ms: int):
    await asyncio.sleep(ms / 1000)


async def print_buffer_smoothly():
    global buffer, finished, cursor
    while not finished or cursor < len(buffer):
        if cursor < len(buffer):
            print(buffer[cursor], end='', flush=True)
            sys.stdout.flush()

            if finished:
                interval = MIN_INTERVAL
            else:
                remaining = len(buffer) - cursor
                interval = (1 / remaining) * 2000
                interval = max(MIN_INTERVAL, min(MAX_INTERVAL, interval))
            await wait(interval)

            cursor += 1
        else:
            await wait(50)  # 等待更多字符或者结束信号


def add_response_text(text: str):
    global buffer
    buffer += text


'''
模拟gpt的流式回复：
    1、使用buffer进行平滑处理、防止抖动
    2、buffer中，内容越多，输出越快；内容越少，输出越慢
    3、最后输出速度会越来越慢，然后停止
'''


async def stream_output():
    global finished
    task = asyncio.create_task(print_buffer_smoothly())

    add_response_text(
        'Dolor enim officia excepteur reprehenderit anim irure. Eu eu tempor excepteur commodo sunt dolor mollit. Magna non anim cillum fugiat aliquip commodo occaecat. Sunt aliqua do labore.')
    await wait(1000)  # 模拟异步等待
    add_response_text(
        'Dolor enim officia excepteur reprehenderit anim irure. Eu eu tempor excepteur commodo sunt dolor mollit. Magna non anim cillum fugiat aliquip commodo occaecat. Sunt aliqua do labore.')
    await wait(1000)  # 模拟异步等待

    finished = True
    await task  # 确保打印任务完成


asyncio.run(stream_output())
