import random
from time import localtime
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate
import sys
import os


def get_color():
    # 获取随机颜色
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)


def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token


def get_weather(region):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = config["weather_key"]
    region_url = "https://geoapi.qweather.com/v2/city/lookup?location={}&key={}".format(region, key)
    response = get(region_url, headers=headers).json()
    if response["code"] == "404":
        print("推送消息失败，请检查地区名是否有误！")
        os.system("pause")
        sys.exit(1)
    elif response["code"] == "401":
        print("推送消息失败，请检查和风天气key是否正确！")
        os.system("pause")
        sys.exit(1)
    else:
        # 获取地区的location--id
        location_id = response["location"][0]["id"]
    weather_url = "https://devapi.qweather.com/v7/weather/now?location={}&key={}".format(location_id, key)
    response = get(weather_url, headers=headers).json()
    # 天气
    weather = response["now"]["text"]
    # 当前温度
    temp = response["now"]["temp"] + u"\N{DEGREE SIGN}" + "C"
    # 风向
    wind_dir = response["now"]["windDir"]
    # 获取逐日天气预报
    url = "https://devapi.qweather.com/v7/weather/3d?location={}&key={}".format(location_id, key)
    response = get(url, headers=headers).json()
    # 最高气温
    max_temp = response["daily"][0]["tempMax"] + u"\N{DEGREE SIGN}" + "C"
    # 最低气温
    min_temp = response["daily"][0]["tempMin"] + u"\N{DEGREE SIGN}" + "C"
    # 日出时间
    sunrise = response["daily"][0]["sunrise"]
    # 日落时间
    sunset = response["daily"][0]["sunset"]
    url = "https://devapi.qweather.com/v7/air/now?location={}&key={}".format(location_id, key)
    response = get(url, headers=headers).json()
    if response["code"] == "200":
        # 空气质量
        category = response["now"]["category"]
        # pm2.5
        pm2p5 = response["now"]["pm2p5"]
    else:
        # 国外城市获取不到数据
        category = ""
        pm2p5 = ""
    id = random.randint(1, 16)
    url = "https://devapi.qweather.com/v7/indices/1d?location={}&key={}&type={}".format(location_id, key, id)
    response = get(url, headers=headers).json()
    proposal = ""
    if response["code"] == "200":
        proposal += response["daily"][0]["text"]
    return weather, temp, max_temp, min_temp, wind_dir, sunrise, sunset, category, pm2p5, proposal


def get_tianhang():
    try:
        key = config["tian_api"]
        url = "http://api.tianapi.com/caihongpi/index?key={}".format(key)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'Content-type': 'application/x-www-form-urlencoded'

        }
        response = get(url, headers=headers).json()
        if response["code"] == 200:
            chp = response["newslist"][0]["content"]
        else:
            chp = ""
    except KeyError:
        chp = ""
    return chp

    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入地区获取天气信息
    region = config["region"]
    weather, temp, max_temp, min_temp, wind_dir, sunrise, sunset, category, pm2p5, proposal = get_weather(region)
    note_ch = config["note_ch"]
    note_en = config["note_en"]
    if note_ch == "" and note_en == "":
        # 获取词霸每日金句
        note_ch, note_en = get_ciba()
    chp = get_tianhang()
    # 公众号推送消息
    for user in users:
        send_message(user, accessToken, region, weather, temp, wind_dir, note_ch, note_en, max_temp, min_temp, sunrise,
                     sunset, category, pm2p5, proposal, chp)
    os.system("pause")
