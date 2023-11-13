import sys
import argparse 
sys.path.append('./DM/')
sys.path.append('./DM/models/')
from DmClass import *

text = '帮订一张从深圳到北京的机票'
history = {'conversation':['','']}

parser = argparse.ArgumentParser()
parser.add_argument('--robot_type', default='', choices=['DH', 'KF'], type=str, help='Robot type, DH or KF')
parser.add_argument('--chat_repo', default=1, choices=[0, 1], type=int, help='which repo used by chat_infer module')
parser.add_argument('--skill_type', default='DH', choices=['DH', 'KF'], help='What type of multi-turn capability the robot has')
parser.add_argument('--FAQ', action="store_true", default=False, help='if use the faq server')
parser.add_argument('--QR', action="store_true", default=False, help='if use the query rewrite server')

parser.add_argument('--qr_ip', default='192.168.68.26', type=str)
parser.add_argument('--qr_port', default='60005', type=str)
parser.add_argument('--faq_ip', default='172.31.208.10', type=str)
parser.add_argument('--faq_port', default='58999', type=str)
parser.add_argument('--docqa_ip', default='172.31.208.4', type=str)
parser.add_argument('--docqa_port', default='60005', type=str)
parser.add_argument('--chat_ip', default='172.31.208.9', type=str)
parser.add_argument('--chat_port', default='60005', type=str)
parser.add_argument('--emotion_ip', default='172.31.208.10', type=str)
parser.add_argument('--emotion_port', default='58999', type=str)
args = parser.parse_args(args=[])
dm  = DmClass(args)
dm.load_data(text, history, '1', -1)

ans, history, emotion = dm.response()
print(ans)