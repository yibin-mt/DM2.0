class MusaChat(LlmBot):
    def __init__(self, seeds_file=None, concat=False, prompt_file=None, model_name=None, role="children", default_mark="instruction"):
        if seeds_file:
            super(MusaChat, self).__init__(seeds_file)
        self.headers = {"User-Agent": "MusaChat Client"}
        # musa_chat
        self.model_name = model_name if model_name else "MusaChat-13B-Ins-v2.09-1300"
        self.worker_addr = self.get_worker_addr()

        # self.worker_addr = "http://172.31.208.06:58091/worker_generate_stream_v2"

        self.system_prompt, self.default_prompt = "", ""
        if prompt_file:
            self.system_prompt, self.default_prompt = get_prompts(prompt_file, key=role)

        self.concat = concat

    def get_worker_addr(self):
        ret = requests.post('http://172.31.208.10:6064' + "/get_worker_address",
                            json={"model": self.model_name})
        return ret.json()["address"]

    def chat_request(self, prompt=None, user=True, prompts: list[dict] = None):
        if prompts and prompt:
            messages = prompts + [{"role": "user" if user else "assistant", "content": prompt}]
        elif prompts:
            messages = prompts
        elif prompt:
            messages = [{"role": "user" if user else "assistant", "content": prompt}]
        else:
            print('should provide prompt or prompts')

        if self.system_prompt: # list
            messages = [{'role': 'system', 'content': self.system_prompt}] + messages

        if self.concat: # system prompt放在最后
            messages = self.concat_messages(messages)
        elif self.default_prompt:
            messages[-1]['content'] += '\n instruction:' + self.default_prompt

        # print('messages are:', messages)
        pload = {
            # "model": "MusaChat-13B-Ins-v2.09-1300",
            # "config_id": "moderation_rail",
            "messages": messages,
            "temperature": 0.0,
            "max_new_tokens": 30,
            "repetition_penalty": 1.0,
        }
        response = requests.post(self.worker_addr+"/worker_generate_stream_v2",
                                 headers=self.headers, json=pload)
        # print('worker addr is:', self.worker_addr)
        for chunk in response.iter_lines(decode_unicode=False, delimiter=b"\0"):
            if len(chunk) > 0:
                rsp_data = json.loads(chunk)

        assert rsp_data["error_code"] == 0
        reply = rsp_data["choices"][0]["message"]["content"]

        # reply = response.json()
        # reply = reply['messages'][-1]['content']
        return [reply]

    def concat_messages(self, messages):
        """
        将多轮数据转化为单轮数据格式
        对于Nemo-Guardrail，将所有轮数的chat拼接成一个prompts.
        直接调用MusaChat，则不需要concat
        system prompt放在了最后
        :return:
        """
        content = ""
        system_prompt = None
        if messages[0]['role'] == 'system':
            system_prompt = messages[0]['content']
        for i, x in enumerate(messages[1:] if system_prompt is not None else messages):
            if i == 0:  # system和第一个user对应的信息，不需要加content
                content += x['content'] + '\n'
            else:
                content += x['role'] + ":" + x['content'] + '\n'

        if system_prompt is not None:
            content += "system:"+system_prompt
        return [{'role': 'user', 'content': content}]