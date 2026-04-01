# 读取系统变量
from dotenv import load_dotenv
import os
load_dotenv()  

# 初始化客户端
from openai import OpenAI
client = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# 定义检索鲜花库存的函数
import json
def get_flower_inventory(city):
    """获取指定城市的鲜花库存"""
    if "北京" in city:
        return json.dumps({"city": "北京", "inventory": "玫瑰: 100, 郁金香: 150"})
    elif "上海" in city:
        return json.dumps({"city": "上海", "inventory": "百合: 80, 康乃馨: 120"})
    elif "深圳" in city:
        return json.dumps({"city": "深圳", "inventory": "向日葵: 200, 玉兰: 90"})
    else:
        return json.dumps({"city": city, "inventory": "未知"})

# 工具（也就是函数）的元数据
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_flower_inventory",
            "description": "获取指定城市的鲜花库存",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，例如：北京、上海或深圳"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

tool_registry = {
    "get_flower_inventory" : get_flower_inventory,
}

# 第一次对话的Message
messages = [{"role": "user", "content": "北京、上海和深圳的鲜花库存是多少？"}]
print("message:", messages)

# 第一次对话的返回结果
first_response = client.chat.completions.create(
    model="stepfun/step-3.5-flash:free",
    messages=messages,
    tools=tools,
    tool_choice="auto",
    temperature=1.0
)
print("first_response:", first_response)
response_message = first_response.choices[0].message

tool_calls = response_message.tool_calls

# 如果返回结果要求用Function Call，就调用函数，并把函数的查询结果附加到消息中
if tool_calls:
    messages.append(response_message)
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        func = tool_registry[function_name]

        function_response = func(** function_args)
        print(f"function_response: {function_response}")

        messages.append(
            {
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": function_name,
                "content": function_response,
            }
        )

print("message:", messages)

# 用有了库存查询结果的Message再来一次对话
second_response = client.chat.completions.create(
    model="stepfun/step-3.5-flash:free",
    messages=messages,
    temperature=1.0
)

print("second_response:", second_response.choices[0].message.content)