import openai
class ChatGPT:
    def __init__(self):
        self.messages = [{"role": "system", "content": "一个有10年Python开发经验的资深算法工程师"}]
        self.filename="./user_messages.json"

    def ask_gpt(self):
        rsp = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=self.messages
        )
        return rsp.get("choices")[0]["message"]["content"]