import os
import time
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 中的环境变量（包含 OpenRouter_API_KEY）
load_dotenv()

# 初始化客户端，指向 OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OpenRouter_API_KEY"),
)

# 模型名称（OpenRouter 上的 stepfun 免费模型）
MODEL = "stepfun/step-3.5-flash:free"

# ==================== 手动管理对话历史 ====================
messages = []

# ---------- 第一轮对话 ----------
user_input_1 = "你能够帮我计算鲜花的价格，3束玫瑰每束12元，再加2束百合每束15元，一共多少钱？"
messages.append({"role": "user", "content": user_input_1})

response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    temperature=0.7,
)
assistant_reply_1 = response.choices[0].message.content
print(f"助手（第一轮）: {assistant_reply_1}\n")

# 将助手的回复加入历史
messages.append({"role": "assistant", "content": assistant_reply_1})

# ---------- 第二轮对话 ----------
user_input_2 = "我把每个花束定价为进价基础上加价20%,进价80元时,我的售价是多少。"
messages.append({"role": "user", "content": user_input_2})

response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    temperature=0.7,
)
assistant_reply_2 = response.choices[0].message.content
print(f"助手（第二轮）: {assistant_reply_2}\n")

# 将第二轮回复也加入历史（可选）
messages.append({"role": "assistant", "content": assistant_reply_2})

# ---------- 第三轮对话：查看当前对话中的消息（模拟原代码中的“查看当前对话中的所有消息”）----------
user_input_3 = "查看当前对话中的所有消息。"
messages.append({"role": "user", "content": user_input_3})

response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    temperature=0.7,
)
assistant_reply_3 = response.choices[0].message.content
print(f"助手（第三轮）: {assistant_reply_3}")

# 你也可以手动打印 messages 列表来查看历史
print("\n===== 实际对话历史 =====")
for idx, msg in enumerate(messages):
    print(f"{idx+1}. {msg['role']}: {msg['content'][:100]}...")  # 只显示前100字符