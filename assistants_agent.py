# 导入环境变量
from dotenv import load_dotenv
import os
import time
load_dotenv()

# 创建Client
from openai import OpenAI
client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OpenRouter_API_KEY"))

thread = client.responses.create(
    model="stepfun/step-3.5-flash:free",
    input="你能够帮我计算鲜花的价格，3束玫瑰每束12元，再加2束百合每束15元，一共多少钱？"
)

# print(thread)

message = client.responses.create(
    model="stepfun/step-3.5-flash:free",
    input="我把每个花束定价为进价基础上加价20%,进价80元时,我的售价是多少。"
)

# 打印消息
# print(message)

# 再次获取 Run 的状态
run_status = client.responses.create(
    model="stepfun/step-3.5-flash:free",
    input="你现在的状态如何？"
)

# 打印 Run 状态
print(run_status)

polling_interval = 5
while True:
    status = run_status.status
    print(f"Run Status: {status}")

    if status in ['completed', 'failed', 'expired']:
        break

    time.sleep(polling_interval)

if status == 'completed':
    print("Run completed successfully.")
elif status == 'failed' or status == 'expired':
    print("Run failed or expired.")

messages = client.responses.create(
    model="stepfun/step-3.5-flash:free",
    input="查看当前对话中的所有消息。"
)

print(messages)