import requests
import json

class Musachat_inference(object):
    
    def __init__(self, ip, port):
        super(Musachat_inference, self).__init__()
        self.ip = ip
        self.port = port
        self.worker_addr = 'http://'+self.ip+':'+self.port+'/v1/chat/completions'
        self.headers = {'Content-Type': 'application/json'}
        
    def response(self, pyload):
        response = requests.post(self.worker_addr,json=pyload, headers = self.headers, stream=True)
        res = ''
        for chunk in response.iter_lines(decode_unicode=False, delimiter=b"\n\n"):
            if chunk:
                if '[DONE]' in str(chunk):
                    break
                data = json.loads(chunk.split(b' ', 1)[1].decode('utf-8'))
                if data['error_code'] == 0:
                    res+=data["choices"][0]['delta']['content']
                    yield res.strip()

    
