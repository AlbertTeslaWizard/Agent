from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import tool
import os

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.environ["DEEPSEEK_API_KEY"],  # 有些兼容服务会忽略它，填占位值即可
    base_url="https://api.deepseek.com/v1",
)

search = SerpAPIWrapper()

@tool
def search_web(query: str) -> str:
    """当需要查询最新信息或模型自身不知道的知识时，使用搜索工具。"""
    return search.run(query)

agent = create_agent(
    model=llm,
    tools=[search_web],
    system_prompt="你是一个有帮助的研究助手。当你不确定或需要最新信息时，使用 search_web 工具。"
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Garnet Crow的中村由利是谁？"}]}
)

print(result["messages"][-1].content)