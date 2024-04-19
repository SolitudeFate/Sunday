import asyncio
import sys

from zhipuai import ZhipuAI

finished = False
buffer = ''
cursor = 0

MIN_INTERVAL = 1
MAX_INTERVAL = 200


async def wait(ms: int):
    await asyncio.sleep(ms / 1000)


async def print_buffer_smoothly_for_textedit(self):
    global buffer, finished, cursor
    while not finished or cursor < len(buffer):
        if cursor < len(buffer):
            print(buffer[cursor], end='', flush=True)
            # append后会自动添加换行，不适合流式回复
            # self.main.textEdit.append(f"{buffer[cursor]}")
            self.main.textEdit.insertPlainText(f"{buffer[cursor]}")
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


async def print_buffer_smoothly_for_lineedit(self):
    global buffer, finished, cursor
    while not finished or cursor < len(buffer):
        if cursor < len(buffer):
            print(buffer[cursor], end='', flush=True)
            self.main.lineEdit.insert(f"{buffer[cursor]}")
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


async def stream_output_song_info(api_key, song_name, self):
    global finished
    client = ZhipuAI(api_key=api_key)
    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {"role": "system", "content": "详细地介绍一下这首歌的歌曲信息和歌手信息，回复格式不要用markdown格式，我这里无法解析markdown"},
            {"role": "user", "content": song_name},
        ],
        stream=True,
    )

    finished = True

    # self.main.textEdit.setEnabled(False)
    for chunk in response:
        for word in chunk.choices[0].delta.content:
            add_response_text(word)
            task = asyncio.create_task(print_buffer_smoothly_for_textedit(self))
            await task
    # self.main.textEdit.setEnabled(True)


async def stream_output_song_name(song_name, self):
    global finished
    finished = True

    add_response_text(song_name)
    task = asyncio.create_task(print_buffer_smoothly_for_lineedit(self))
    await task
