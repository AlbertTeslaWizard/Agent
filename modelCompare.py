import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY")

if not DEEPSEEK_API_KEY:
    raise ValueError("未找到 DEEPSEEK_API_KEY")
if not MINIMAX_API_KEY:
    raise ValueError("未找到 MINIMAX_API_KEY")


deepseek_client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

minimax_client = OpenAI(
    api_key=MINIMAX_API_KEY,
    base_url="https://api.minimaxi.com/v1"
)


def ask_deepseek(prompt: str) -> str:
    resp = deepseek_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": prompt}
        ],
        stream=False
    )
    return resp.choices[0].message.content


def ask_minimax(prompt: str) -> str:
    resp = minimax_client.chat.completions.create(
        model="MiniMax-M2.7",
        messages=[
            {"role": "system", "content": "你是一个有帮助的助手。"},
            {"role": "user", "content": prompt}
        ]
    )
    return resp.choices[0].message.content


def compare(prompt: str):
    models = {
        "DeepSeek": ask_deepseek,
        "MiniMax": ask_minimax,
    }

    for name, fn in models.items():
        print("=" * 20, name, "=" * 20)
        try:
            answer = fn(prompt)
            print(answer)
        except Exception as e:
            print(f"[调用失败] {e}")
        print()


if __name__ == "__main__":
    compare("百合花源自哪个国家？")