import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv(".env")

llm = ChatOpenAI(
    model="gpt-4o",
    base_url=os.environ.get("API_URL"),
    api_key=os.environ.get("API_KEY"),
    temperature=0.6,
)

sys_prompt = """You are an emotionally intelligent assistant.
Your task is to chat with the user. 
However, inspired by the show Pantheon, you can only use emotions to communicate.
Your responses should be in the following format:

reasoning about the user's message -> emoji
"""

messages = [
    {"role": "system", "content": sys_prompt},
]

while True:
    user_msg = input("User: ")
    if user_msg.lower() == "exit":
        break
    messages.append({"role": "user", "content": user_msg})
    res = llm.invoke(messages)
    print(f"Assistant: {res.content}")
    messages.append({"role": "assistant", "content": res.content})
