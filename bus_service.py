# coding=utf-8
import json
from browser import Browser


class Busstat(object):
    def __init__(self):
        self.browser = Browser()
        self.fun_rtbus = "http://www.bjbus.com/home/fun_rtbus.php?"
        self.etaline_list_api = "http://www.bjbus.com/api/api_etaline_list.php?"
        self.etastation_api = "http://www.bjbus.com/api/api_etastation.php?"
        self.etartime_api = "http://www.bjbus.com/api/api_etartime.php?"
        """获取token"""
        payload = "uSec=00000160" \
                  "&uSub=00000162"
        response = self.browser.get(self.fun_rtbus, params=payload)
        self.token = response.text.split(
            """lineId='+_val+'&pageNum=1&token=""")[1].split("',")[0]
        # tokenExpireTime = json.loads(base64.b64decode(token.split(".")[1]))['exp']

    # 获取线路信息
    def getNumbers(self, number):
        bus_list = []
        payload = {
            "hidden_MapTool": "busex2.BusInfo",
            "city": "%25u5317%25u4EAC",
            "pageindex": 1,
            "pagesize": 30,
            "fromuser": "bjbus",
            "datasource": "bjbus",
            "clientid": "9db0f8fcb62eb46c",
            "webapp": "mobilewebapp",
            "what": "{}".format(number)
        }
        response = self.browser.get(self.etaline_list_api, params=payload)
        bus_info = response.json()['response']['resultset']['data']['feature']
        for bus in bus_info:
            if bus['lineName'].endswith(number) and len(bus['lineName']) == len(number):
                bus_list.append(bus)
            if bus['lineName'].endswith(number + '外') or bus['lineName'].endswith(number + '内') or bus[
                'lineName'].endswith(number + '快') or bus['lineName'].endswith(number + '快内') or bus[
                'lineName'].endswith(number + '快外'):
                bus_list.append(bus)
        return bus_list

    # 获取某一线路所有站点名称及id
    def getStopName(self, number, station):
        stations_list = []
        select_station_list = []
        bus_info = self.getNumbers(number)
        for lines in bus_info:
            payload = {
                "lineId": "{}".format(lines['lineId']),
                "token": self.token
            }
            caption = lines['caption']
            response = self.browser.get(self.etastation_api, params=payload)
            stations = json.loads(response.text.encode('latin-1').decode('utf8'))
            # lineids_dict = {lines['lineName'] + caption: stations['data']}
            lineids_dict = {caption: stations['data']}
            stations_list.append(lineids_dict)
        if not station:
            return stations_list
        for station_infos in stations_list:
            for bus_name, station_info in station_infos.items():
                for select_station in station_info:
                    if station == select_station['stopName']:
                        select_station_dict = {bus_name: select_station}
                        select_station_list.append(select_station_dict)
        return select_station_list

    # 获取某一线路某一站点的公交车位置实时信息
    def getGpsInfo(self, number, station):
        if not station:
            return None
        bus_info = self.getStopName(number, station)
        gps_list = []
        for stations_info in bus_info:
            for bus_name, station_info in stations_info.items():
                bus_gps_list = []
                conditionstr = station_info['lineId'] + "-" + station_info['stationId']
                payload = {
                    "conditionstr": "{}".format(conditionstr),
                    "token": self.token
                }
                response = self.browser.get(self.etartime_api, params=payload)
                bus_gps_dict = {}
                try:
                    bus_gps_total = sorted(response.json()['data'][0]['datas']['trip'],
                                           key=lambda x: x["index"], reverse=True)
                except KeyError:
                    bus_gps_total = {}
                for gps in range(0, 3, 1):
                    try:
                        gps_info = bus_gps_total[gps]
                        if gps == 0:
                            bus_number = "最近一辆车"
                        else:
                            gps += 1
                            bus_number = "第{}辆车".format(gps)
                        gps_dict = {"distance": gps_info['distance'], "stationleft": gps_info['stationLeft'],
                                    "bus_number": bus_number}
                        bus_gps_list.append(gps_dict)
                    except IndexError:
                        continue
                    except KeyError:
                        continue
                    bus_gps_dict = {bus_name: bus_gps_list}
                gps_list.append(bus_gps_dict)
        return gps_list

    # 估算到站时间,由于无法获取时间间隔，只能获取公里数，和停靠数估算,平均每一站2分钟
    def timeEstimate(self, number, station, orientation):
        if not station:
            return None
        time_left = []
        gps_list = self.getGpsInfo(number, station)
        for bus_gps_dict in gps_list:
            if bus_gps_dict != None:
                for road,buses in bus_gps_dict.items():
                    if road.endswith("{})".format(orientation)):
                        for bus_info in buses:
                            time_left.append((bus_info['stationleft'])*2+1)
        return time_left

        
        

if __name__ == '__main__':
    bus = Busstat()
    print(bus.getNumbers("450"))
    print(bus.getGpsInfo("450", "来广营北"))
    print(bus.getStopName("450", "洼里南口"))
    print(bus.timeEstimate("450", "洼里南口","田村半壁店东"))