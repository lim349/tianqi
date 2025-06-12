import requests
from bs4 import BeautifulSoup
import csv
import json

def getHTMLtext(url):
    """请求获得网页内容"""
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        print("成功访问")
        return r.text
    except:
        print("访问错误")
        return ""

def get_content(html):
    """处理得到有用信息保存数据文件"""
    final = []  # 初始化一个列表保存数据
    bs = BeautifulSoup(html, "html.parser")  # 创建BeautifulSoup对象
    body = bs.body
    data = body.find('div', {'id': '7d'})  # 找到div标签且id=7d

    # 下面爬取当天的数据
    data2 = body.find_all('div', {'class': 'left-div'})
    text = data2[2].find('script').string
    # 移除改var data=将其变为json数据
    text = text[text.index('=') + 1:-2]
    jd = json.loads(text)
    # 找到当天的数据
    dayone = jd['od']['od2']
    final_day = []  # 存放当天的数据
    count = 0
    for i in dayone:
        if count <= 23:
            temp = [
                i['od21'],  # 小时
                i['od22'],  # 温度
                i['od24'],  # 风力方向
                i['od25'],  # 风级
                i['od26'],  # 降水量
                i['od27'],  # 相对湿度
            ]
            final_day.append(temp)
            count = count + 1

    # 下面爬取7天的数据
    ul = data.find('ul')  # 找到所有的ul标签
    li = ul.find_all('li')  # 找到所有的li标签
    i = 1  # 控制爬取的天数
    # 遍历找到的每一个li
    for day in li:
        if i < 8 and i > 0:
            # 临时存放每天的数据
            temp = []
            # 得到日期
            date = day.find('h1').string
            date = date[0:date.index('（')]  # 取出日期号
            temp.append(date)
            inf = day.find_all('p')  # 找出li下面的p标签,提取第一个p标签的值,即天气
            temp.append(inf[0].string)
            tem_low = inf[1].find('i').string  # 找到最低气温

            if inf[1].find('span') is None:  # 天气预报可能没有最高气温
                tem_high = None
            else:
                tem_high = inf[1].find('span').string  # 找到最高气温

            temp.append(tem_low[:-1])
            if tem_high[-1] == 'C':
                temp.append(tem_high[:-1])
            else:
                temp.append(tem_high)

            wind = inf[2].find_all('span')  # 找到风向
            for j in wind:
                temp.append(j['title'])

            wind_scale = inf[2].find('i').string  # 找到风级
            index1 = wind_scale.index('级')
            temp.append(int(wind_scale[index1-1:index1]))
            final.append(temp)
            i = i + 1
    return final_day, final

def get_content2(html):
    """处理得到有用信息保存数据文件"""
    final = []  # 初始化一个列表保存数据
    bs = BeautifulSoup(html, "html.parser")  # 创建BeautifulSoup对象
    body = bs.body
    data = body.find('div', {'id': '15d'})  # 找到div标签且id=15d
    ul = data.find('ul')  # 找到所有的ul标签
    li = ul.find_all('li')  # 找到所有的li标签
    i = 0  # 控制爬取的天数
    for day in li:  # 遍历找到的每一个li
        if i < 8:
            temp = []  # 临时存放每天的数据
            # 得到日期
            date = day.find('span', {'class': 'time'}).string
            date = date[date.index('（') + 1:-2]  # 取出日期号
            temp.append(date)
            # 找到天气
            weather = day.find('span', {'class': 'wea'}).string
            temp.append(weather)
            # 找到温度
            tem = day.find('span', {'class': 'tem'}).text
            temp.append(tem[tem.index('/') + 1:-1])  # 找到最低气温
            temp.append(tem[:tem.index('/') - 1])  # 找到最高气温
            # 找到风向
            wind = day.find('span', {'class': 'wind'}).string
            if '转' in wind:  # 如果有风向变化
                temp.append(wind[:wind.index('转')])
                temp.append(wind[wind.index('转') + 1:])
            else:  # 如果没有风向变化,前后风向一致
                temp.append(wind)
                temp.append(wind)
            # 找到风级
            wind_scale = day.find('span', {'class': 'wind1'}).string
            index1 = wind_scale.index('级')
            temp.append(int(wind_scale[index1-1:index1]))
            final.append(temp)
            i = i + 1
    return final

def write_to_csv(file_name, data, day=14):
    """保存为CSV文件"""
    with open(file_name, 'w', errors='ignore', newline='',  encoding='utf-8') as f:
        if day == 14:
            header = ['日期', 'PM2', '最低气温', '最高气温', '风向1', '风向2', '风级']
        else:
            header = ['小时', '温度', '风力方向', '风级', '降水量', '相对湿度']
        f_csv = csv.writer(f)
        f_csv.writerow(header)
        f_csv.writerows(data)

def main():
    """主函数"""
    print("Weather test")
    # 珠海
    url1 = 'https://www.weather.com.cn/weather/101280701.shtml'  # 7天天气中国天气网
    url2 = 'http://www.weather.com.cn/weather15d/101280701.shtml'  # 8-15天天气中国天气网
    html1 = getHTMLtext(url1)
    data1, data1_7 = get_content(html1)  # 获得1-7天和当天的数据
    html2 = getHTMLtext(url2)
    data8_14 = get_content2(html2)  # 获得8-14天数据
    data14 = data1_7 + data8_14
    write_to_csv('weather14.csv', data14, day=14)  # 保存为csv文件
    write_to_csv('weather1.csv', data1, day=1)

if __name__ == '__main__':
    main()