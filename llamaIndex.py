from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os

if __name__ == '__main__':
    # 1. 配置 LLM：用 OpenRouter 上的免费 StepFun
    Settings.llm = OpenAILike(
        model="stepfun/step-3.5-flash:free",
        api_base="https://openrouter.ai/api/v1",
        api_key=os.environ["OpenRouter_API_KEY"],
        is_chat_model=True,
    )

    # 2. 配置 embedding：本地句向量模型
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-zh-v1.5"
    )

    # 3. 读取本地文档
    documents = SimpleDirectoryReader("data").load_data()

    # 4. 建立向量索引
    index = VectorStoreIndex.from_documents(documents)

    # 5. 创建查询引擎
    query_engine = index.as_query_engine()

    # 6. 提问
    response = query_engine.query("花语秘境的员工有几种角色，分别是什么？")
    response2 = query_engine.query("花语秘境的Agent叫什么？")
    print(response)
    print(response2)

    index.storage_context.persist()