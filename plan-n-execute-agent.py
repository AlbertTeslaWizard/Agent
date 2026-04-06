import os
from dotenv import load_dotenv

load_dotenv()

# ===== 1. 工具 =====
from langchain.tools import tool


@tool
def check_inventory(flower_type: str) -> int:
    """
    查询特定类型花的库存数量。
    参数:
    - flower_type: 花的类型
    返回:
    - 库存数量
    """
    inventory_db = {
        "玫瑰": 100,
        "rose": 100,
        "百合": 60,
        "lily": 60,
        "康乃馨": 80,
        "carnation": 80,
    }
    return inventory_db.get(flower_type, 0)


@tool
def calculate_price(base_price: float, markup: float, quantity: int) -> float:
    """
    根据基础单价、加价比例和数量计算最终总价。
    参数:
    - base_price: 基础单价
    - markup: 加价比例，例如 0.2 表示加价 20%
    - quantity: 购买数量
    返回:
    - 最终总价
    """
    return round(base_price * (1 + markup) * quantity, 2)


@tool
def schedule_delivery(order_id: int, delivery_date: str) -> str:
    """
    安排订单配送。
    参数:
    - order_id: 订单编号
    - delivery_date: 配送日期
    返回:
    - 配送确认信息
    """
    return f"订单 {order_id} 已安排在 {delivery_date} 配送，预计当天 18:00 前送达。"


tools = [check_inventory, calculate_price, schedule_delivery]


# ===== 2. 模型 =====
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="stepfun/step-3.5-flash:free",
    temperature=0,
    base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


# ===== 3. Plan-and-Execute =====
from langchain_experimental.plan_and_execute import (
    PlanAndExecute,
    load_agent_executor,
    load_chat_planner,
)

planner = load_chat_planner(llm)

# verbose=True 可以看到执行过程
executor = load_agent_executor(
    llm=llm,
    tools=tools,
    verbose=True,
)

agent = PlanAndExecute(
    planner=planner,
    executor=executor,
    verbose=True,
)


# ===== 4. 运行 =====
if __name__ == "__main__":
    query = (
        "先查询玫瑰的库存。"
        "如果库存不少于50朵，就按玫瑰基础单价5元、加价20%计算50朵玫瑰的总价。"
        "然后给出当天配送方案，并把结果用中文清楚地告诉我。"
    )

    result = agent.run(query)
    print("\n===== 最终结果 =====")
    print(result)