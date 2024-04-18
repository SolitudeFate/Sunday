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


async def print_buffer_smoothly(self):
    global buffer, finished, cursor
    while not finished or cursor < len(buffer):
        if cursor < len(buffer):
            print(buffer[cursor], end='', flush=True)
            # current_text = self.main.textEdit.toPlainText()
            # print("过去：", current_text, end='', flush=True)
            # new_text = current_text + buffer[cursor]
            # print("追加：", new_text, end='', flush=True)
            # self.main.textEdit.setText(new_text)
            # self.main.textEdit.append(f"{buffer[cursor]}")
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


async def stream_output(song_name, self):
    global finished
    task = asyncio.create_task(print_buffer_smoothly(self))

    client = ZhipuAI(api_key="5579e3ae45b0c5873c19c6b94d682332.E7dXLEng9p0gzyUV")
    response = client.chat.completions.create(
        model="glm-4",  # 填写需要调用的模型名称
        messages=[
            {"role": "system", "content": "详细地介绍一下这首歌的歌曲信息"},
            {"role": "user", "content": song_name},
        ],
        stream=True,
    )

    for chunk in response:
        for word in chunk.choices[0].delta.content:
            add_response_text(word)

    finished = True
    await task  # 确保打印任务完成


if __name__ == '__main__':
    song_name = "《人鱼的眼泪》EXO"
    asyncio.run(stream_output(song_name))
