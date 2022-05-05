#!/usr/bin/python3
#coding=utf-8
from ctypes.wintypes import PINT
import sys
import json
import requests

from bus_service import Busstat

class DontMissTheBus:
    # 初始化
    def __init__(self, wechat_config):
        self.appid = wechat_config['appid'].strip()
        self.appsecret = wechat_config['appsecret'].strip()
        self.template_id = wechat_config['template_id'].strip()
        self.access_token = ''
        self.bus_line = wechat_config['bus_line'].strip()
        self.station = wechat_config['station'].strip()
        self.line_orientation = wechat_config['line_orientation'].strip()
        self.walktime = wechat_config['walktime']

    # 错误代码
    def get_error_info(self, errcode):
        return {
            40013: '不合法的 AppID ，请开发者检查 AppID 的正确性，避免异常字符，注意大小写',
            40125: '无效的appsecret',
            41001: '缺少 access_token 参数',
            40003: '不合法的 OpenID ，请开发者确认 OpenID （该用户）是否已关注公众号，或是否是其他公众号的 OpenID',
            40037: '无效的模板ID',
        }.get(errcode,'unknown error')

    # 打印日志
    def print_log(self, data, openid=''):
        errcode = data['errcode']
        errmsg = data['errmsg']
        if errcode == 0:
            print(' [INFO] send to %s is success' % openid)
        else:
            print(' [ERROR] (%s) %s - %s' % (errcode, errmsg, self.get_error_info(errcode)))
            if openid != '':
                print(' [ERROR] send to %s is error' % openid)
            sys.exit(1)

    # 获取access_token
    def get_access_token(self, appid, appsecret):
        url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (appid, appsecret)
        r = requests.get(url)
        data = json.loads(r.text)
        if 'errcode' in data:
            self.print_log(data)
        else:
            self.access_token = data['access_token']

    # 获取用户列表
    def get_user_list(self):
        if self.access_token == '':
            self.get_access_token(self.appid, self.appsecret)
        url = 'https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s&next_openid=' % self.access_token
        r = requests.get(url)
        data = json.loads(r.text)
        if 'errcode' in data:
            self.print_log(data)
        else:
            openids = data['data']['openid']
            return openids

    # 发送消息
    def send_msg(self, openid, template_id, arrive_time):
        msg = {
            'touser': openid,
            'template_id': template_id,
            'data': {
                "title": {
                    "value":"希望这次能赶上公交车!(ง •_•)ง",
                    "color":"#173177"
                },
                "nearest":{
                    "value":"没有查到公交信息...(；′⌒`)",
                },
                "outdoor":{
                    "value":"暂时不知道...(・∀・(・∀・(・∀・*)"
                }
            }
        }

        for _,t in enumerate(arrive_time):
            if t >self.walktime:
                msg['data']["nearest"] = {
                        "value":"预计还有{}分钟到达 {}".format(t,self.station),
                        "color":"#173177"
                    }
                msg['data']['outdoor']={
                        "value":"必须在{}分钟之内出门才能赶上车！".format(t-self.walktime),
                }
        
        json_data = json.dumps(msg)
        if self.access_token == '':
            self.get_access_token(self.appid, self.appsecret)
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=%s' % self.access_token
        r = requests.post(url, json_data)
        return json.loads(r.text)

    # 为设置的用户列表发送消息
    def get_arrival_time(self, openids):
        bus = Busstat()
        arrive_time = bus.timeEstimate(self.bus_line, self.station, self.line_orientation)
        for openid in openids:
            openid = openid.strip()
            result = self.send_msg(openid, self.template_id, arrive_time)
            self.print_log(result, openid)

    # 执行
    def run(self, openids=[]):
        if openids == []:
            # 如果openids为空，则遍历用户列表
            openids = self.get_user_list()
        # 根据openids对用户进行群发
        self.get_arrival_time(openids)
