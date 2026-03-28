from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import os
import requests
from dotenv import load_dotenv
from IPython.display import Image, display
import base64
import json

if __name__ == '__main__':
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.environ["DEEPSEEK_API_KEY"],
        base_url="https://api.deepseek.com/v1"
    )

    messages = [
        ("system", "你是一个帮助用户了解鲜花信息的智能助手。请始终输出合法JSON，格式为 {\"recommended_flower\": \"...\", \"delivery_time\": \"...\"}。"),
        ("human", "生日送什么花最好？"),
        ("ai", "玫瑰花是生日礼物的热门选择。"),
        ("human", "送货需要多长时间？请结合上下文，按指定JSON格式返回。")
    ]

    option = False
    if option == True:
        ai_msg = llm.invoke(messages)
        print(ai_msg.content)

    api_key = os.environ["MINIMAX_API_KEY"]
    url = "https://api.minimaxi.com/v1/image_generation"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    Query = input("请输入：")

    payload = {
        "model": "image-01",
        "prompt": Query,
        "aspect_ratio": "1:1",
        "response_format": "base64"
    }

    response = requests.post(url, headers=headers, json=payload)

    print("status_code =", response.status_code)
    print("raw text =", response.text)

    response.raise_for_status()

    data = response.json()
    print("json =", json.dumps(data, ensure_ascii=False, indent=2))

    if "data" not in data:
        raise ValueError(f"接口返回中没有 data 字段，完整返回为：{json.dumps(data, ensure_ascii=False)}")

    if "image_base64" not in data["data"]:
        raise ValueError(f"data 中没有 image_base64 字段，完整返回为：{json.dumps(data, ensure_ascii=False)}")

    img_b64 = data["data"]["image_base64"][0]
    img_bytes = base64.b64decode(img_b64)

    display(Image(data=img_bytes))
    output_path = "generated_image.png"
    with open(output_path, "wb") as f:
        f.write(img_bytes)

    print(f"图片已保存到: {os.path.abspath(output_path)}")