import os
from dotenv import load_dotenv
from openai import OpenAI
import json

def encouragement_generator(name, mood):
    replies = {
                "tired" : "好好休息，养精蓄锐！",
                "happy" : "天气晴朗，心情大好！",
                "sad" : "黑暗终将散去，光明终将到来！",
                "smooth" : "晚安好梦！"
            }

    content = replies.get(mood.lower(), "祝你好运！")
    return f"{name}, {content}"

# name = input("请输入你的名字:")
# mood = input("请输入你现在的心情:")
# print(encouragement_generator(name, mood))

# 读取环境变量
load_dotenv()

# 初始化 OpenRouter 客户端
client = OpenAI(
    base_url=os.getenv("OPENROUTER_BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# =========================
# 1. 定义本地函数
# =========================

def get_encouragement(mood, name=None):
    encouragement_messages = {
        "开心": "看到你这么阳光真好！保持这份积极！",
        "难过": "记得，每片乌云背后都有阳光。",
        "压力大": "深呼吸，慢慢呼出，一切都会好起来的。",
        "疲倦": "你已经很努力了，现在是时候休息一下了。"
    }

    base_message = encouragement_messages.get(mood, "抬头挺胸，一切都会变好的。")
    if name:
        return f"{name}，{base_message}"
    return base_message


def get_weather(city):
    return f"{city}今天天气不错，适合出门走走。"


def say_hello(name):
    return f"你好，{name}！很高兴见到你。"


# =========================
# 2. 工具注册表：函数名 -> Python函数
# =========================

tool_registry = {
    "get_encouragement": get_encouragement,
    "get_weather": get_weather,
    "say_hello": say_hello,
}


# =========================
# 3. 定义给模型看的 tools
# =========================

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_encouragement",
            "description": "根据用户的情绪和名字生成一句鼓励的话",
            "parameters": {
                "type": "object",
                "properties": {
                    "mood": {
                        "type": "string",
                        "description": "用户当前情绪，例如 开心、难过、压力大、疲倦"
                    },
                    "name": {
                        "type": "string",
                        "description": "用户名字，例如 小雪"
                    }
                },
                "required": ["mood"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询某个城市的天气信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名，例如 北京、上海、广州"
                    }
                },
                "required": ["city"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "say_hello",
            "description": "向某个人打招呼",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "名字，例如 张三、小雪"
                    }
                },
                "required": ["name"],
                "additionalProperties": False
            }
        }
    }
]


# =========================
# 4. 执行工具调用的通用函数
# =========================

def execute_tool_call(tool_call):
    function_name = tool_call.function.name
    arguments_str = tool_call.function.arguments

    print("\n====================")
    print("检测到工具调用")
    print("function_name:", function_name)
    print("arguments:", arguments_str)

    # 1) 检查函数是否存在
    if function_name not in tool_registry:
        return f"错误：未找到名为 {function_name} 的本地函数。"

    # 2) 解析参数
    try:
        arguments_dict = json.loads(arguments_str) if arguments_str else {}
    except json.JSONDecodeError as e:
        return f"错误：函数参数不是合法 JSON。详细信息：{str(e)}"

    # 3) 动态分发调用
    func = tool_registry[function_name]
    try:
        result = func(**arguments_dict)
        return result
    except TypeError as e:
        return f"错误：函数参数不匹配。详细信息：{str(e)}"
    except Exception as e:
        return f"错误：函数执行失败。详细信息：{str(e)}"


# =========================
# 5. 初始消息
# =========================

messages = [
    {
        "role": "system",
        "content": (
            "你是一个友好、自然、简洁的中文助手。"
            "当用户请求适合用工具完成的任务时，可以调用工具。"
        )
    },
    {
        "role": "user",
        "content": "快鼓励一下疲倦的小雪！"
    }
]


# =========================
# 6. 第一次请求：让模型决定是否调用工具
# =========================

response = client.chat.completions.create(
    model="stepfun/step-3.5-flash:free",
    messages=messages,
    tools=tools,
    tool_choice="auto",
    temperature=1.0
)

assistant_message = response.choices[0].message

print("第一次模型返回：")
print(assistant_message)

# 先把 assistant 消息加入历史
assistant_msg_for_history = {
    "role": "assistant",
    "content": assistant_message.content or ""
}

if assistant_message.tool_calls:
    assistant_msg_for_history["tool_calls"] = []
    for tc in assistant_message.tool_calls:
        assistant_msg_for_history["tool_calls"].append({
            "id": tc.id,
            "type": "function",
            "function": {
                "name": tc.function.name,
                "arguments": tc.function.arguments
            }
        })

messages.append(assistant_msg_for_history)


# =========================
# 7. 如果有工具调用，则逐个执行
# =========================

if assistant_message.tool_calls:
    for tool_call in assistant_message.tool_calls:
        function_result = execute_tool_call(tool_call)

        print("tool result:", function_result)

        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": str(function_result)
        })

    # 第二次请求：基于工具结果生成最终回答
    final_response = client.chat.completions.create(
        model="stepfun/step-3.5-flash:free",
        messages=messages,
        temperature=1.0
    )

    final_text = final_response.choices[0].message.content

    print("\n====================")
    print("最终回复：")
    print(final_text)

else:
    print("\n====================")
    print("模型没有调用工具，直接回复：")
    print(assistant_message.content)
