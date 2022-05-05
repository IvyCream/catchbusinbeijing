#!/usr/bin/python3
#coding=utf-8
import notify

if __name__ == '__main__':
    # 微信配置
    wechat_config = {
        'appid': '', #(No.1)此处填写公众号的appid
        'appsecret': '', #(No.2)此处填写公众号的appsecret
        'template_id': '	', #(No.3)此处填写公众号的模板消息ID
        'bus_line': '450', # 公交线路
        'station': '洼里南口', # 上车站点
        'line_orientation': '田村半壁店东',  # 线路终点站（识别方向）
        'walktime': 10  # 步行到公交站的时间
    }
    
    # 用户列表
    openids = [
        'oApSc6cLiSNhziY4S1k_qi2EziVs', #(No.4)此处填写你的微信号（微信公众平台上的微信号）
    ]

    # 执行
    bus = notify.DontMissTheBus(wechat_config)

    '''
    run()方法可以传入openids列表，也可不传参数
    不传参数则对微信公众号的所有用户进行群发
    '''
    bus.run()
