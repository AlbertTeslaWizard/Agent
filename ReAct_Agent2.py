import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain.tools import tool
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_openrouter import ChatOpenRouter

load_dotenv()


# ====== 模拟业务数据 ======
INVENTORY_DB = {
    "玫瑰": 100,
    "百合": 60,
    "康乃馨": 80,
}

BASE_PRICE_DB = {
    "玫瑰": 5.0,   # 单价，示例
    "百合": 8.0,
    "康乃馨": 4.0,
}


# ====== 工具定义 ======
@tool
def check_inventory(flower_type: str) -> int:
    """
    查询某种花的库存数量。
    参数:
    - flower_type: 花的类型，例如“玫瑰”
    返回:
    - 当前库存数量
    """
    return INVENTORY_DB.get(flower_type, 0)


@tool
def calculate_total_price(
    flower_type: str,
    quantity: int,
    markup: float = 0.2,
) -> float:
    """
    根据花的类型、数量和加价比例计算总价。
    参数:
    - flower_type: 花的类型，例如“玫瑰”
    - quantity: 数量
    - markup: 加价比例，0.2 表示加价 20%
    返回:
    - 总价
    """
    base_price = BASE_PRICE_DB.get(flower_type, 0.0)
    return round(base_price * quantity * (1 + markup), 2)


@tool
def schedule_delivery(order_id: int, delivery_date: str) -> str:
    """
    安排订单配送。
    参数:
    - order_id: 订单编号
    - delivery_date: 配送日期，例如“今天”或“2026-04-06”
    返回:
    - 配送安排说明
    """
    return f"订单 {order_id} 已安排在 {delivery_date} 配送，预计当天 18:00 前送达。"


# ====== 结构化输出 ======
class FlowerOrderPlan(BaseModel):
    flower_type: str = Field(description="花的类型")
    quantity: int = Field(description="数量")
    inventory: int = Field(description="库存数量")
    total_price: float = Field(description="总价")
    can_fulfill_today: bool = Field(description="是否能当天完成需求")
    delivery_plan: str = Field(description="配送方案说明")
    summary: str = Field(description="给用户的最终简要说明")


# ====== OpenRouter 模型 ======
llm = ChatOpenRouter(
    model="stepfun/step-3.5-flash:free",
    temperature=0,
    reasoning={"effort": "low", "summary": "auto"}
)

SYSTEM_PROMPT = """
你是花店订单助理。

处理用户请求时必须遵守：
1. 涉及库存时，先调用 check_inventory。
2. 涉及价格时，必须调用 calculate_total_price，不要自己编价格。
3. 涉及配送方案时，必须调用 schedule_delivery。
4. 如果库存不足，要明确说明不足多少。
5. 先完成必要工具调用，再给出最终回答。
"""


agent = create_agent(
    model=llm,
    tools=[check_inventory, calculate_total_price, schedule_delivery],
    system_prompt=SYSTEM_PROMPT,
    response_format=ToolStrategy(FlowerOrderPlan),  # 不需要结构化结果的话可删掉
)


if __name__ == "__main__":
    user_query = "查查玫瑰的库存然后给出50朵玫瑰的价格和当天的配送方案！"

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": user_query}
        ]
    })

    # 结构化结果
    structured = result.get("structured_response")
    if structured:
        print("=== structured_response ===")
        print(structured)

    print("\n=== final message ===")
    print(result["messages"][-1].content)