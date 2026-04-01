import os
import ast
import operator as op
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SerpAPIWrapper

load_dotenv()

# ========= 1) 初始化模型 =========
llm = ChatOpenAI(
    model="stepfun/step-3.5-flash:free",
    temperature=0.5,
    base_url=os.getenv("OPENROUTER_BASE_URL"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# ========= 2) 初始化搜索工具 =========
search_wrapper = SerpAPIWrapper(
    serpapi_api_key=os.getenv("SERPAPI_API_KEY")
)

# ========= 3) 自定义工具 =========
@tool("web_search")
def web_search(query: str) -> str:
    """搜索互联网上的实时信息。适用于价格、新闻、市场行情等问题。"""
    try:
        return search_wrapper.run(query)
    except Exception as e:
        return f"搜索失败: {e}"


_ALLOWED_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.Mod: op.mod,
}

def _safe_eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numbers are allowed.")
    elif isinstance(node, ast.Num):  
        return node.n
    elif isinstance(node, ast.BinOp):
        if type(node.op) not in _ALLOWED_OPERATORS:
            raise ValueError("Operator not allowed.")
        return _ALLOWED_OPERATORS[type(node.op)](
            _safe_eval(node.left),
            _safe_eval(node.right),
        )
    elif isinstance(node, ast.UnaryOp):
        if type(node.op) not in _ALLOWED_OPERATORS:
            raise ValueError("Operator not allowed.")
        return _ALLOWED_OPERATORS[type(node.op)](
            _safe_eval(node.operand)
        )
    else:
        raise ValueError("Unsupported expression.")


@tool("calculator")
def calculator(expression: str) -> str:
    """执行数学计算。适用于加减乘除、百分比定价、毛利加价等问题。"""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return str(result)
    except Exception as e:
        return f"计算失败: {e}"


tools = [web_search, calculator]

# ========= 4) 创建 Agent =========
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "你是一个中文商业助理。"
        "遇到市场价格、行情、最新信息时，优先使用 web_search。"
        "遇到加价、折扣、百分比、成本核算时，优先使用 calculator。"
        "请尽量先查信息，再做计算。"
        "最终请用中文给出简洁清晰的结论。"
    ),
)

# ========= 5) 输入问题 =========
query = """目前市场上玫瑰花的一般进货价格是多少？
如果我在此基础上加价5%，应该如何定价？"""

# ========= 6) 用 stream 模拟 verbose =========
print("===== Agent 开始执行 =====")

final_answer = None

for chunk in agent.stream(
    {
        "messages": [
            {"role": "user", "content": query}
        ]
    },
    stream_mode="updates",
):

    print("\n----- 更新 -----")
    print(chunk)

    if isinstance(chunk, dict):
        for node_name, node_data in chunk.items():
            if isinstance(node_data, dict) and "messages" in node_data:
                msgs = node_data["messages"]
                if msgs:
                    last_msg = msgs[-1]
                    if hasattr(last_msg, "content") and last_msg.content:
                        final_answer = last_msg.content

print("\n===== Agent 执行结束 =====")
print("最终回答：")
print(final_answer)