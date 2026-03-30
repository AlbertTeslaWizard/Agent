import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

load_dotenv()

if __name__ == "__main__":
    prompt = ChatPromptTemplate.from_template("请讲一个关于 {topic} 的故事")
    prompt = ChatPromptTemplate.from_template("{flower}的花语是？")

    model = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com/v1",
    )

    output_parser = StrOutputParser()

    chain = prompt | model | output_parser

    # message = chain.invoke({"topic": "水仙花"})
    
    message = chain.invoke({"flower" : "豌豆花"})
    print(message)