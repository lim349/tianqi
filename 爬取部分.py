import time
import csv
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def get_weather_data(url):
    weather_info = []

    # 配置Edge选项
    edge_options = Options()
    edge_options.add_argument('--headless')  # 无头模式，不显示浏览器窗口
    edge_options.add_argument('--disable-gpu')
    edge_options.add_argument('--no-sandbox')
    edge_options.add_argument('--disable-dev-shm-usage')
    edge_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36')

    # 初始化Edge WebDriver
    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=edge_options)

    try:
        # 访问网页
        driver.get(url)
        print("正在加载网页...")

        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//ul[@class='thrui']/li"))
        )

        # 查找并点击"显示更多"按钮
        try:
            more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[7]/div[1]/div[4]/ul/div"))
            )
            print("找到'显示更多'按钮，点击加载更多数据...")
            more_button.click()

            # 等待额外数据加载完成
            time.sleep(3)
        except Exception as e:
            print(f"未找到'显示更多'按钮或点击失败: {e}")

        # 获取所有天气数据
        weather_elements = driver.find_elements(By.XPATH, "//ul[@class='thrui']/li")
        print(f"找到 {len(weather_elements)} 条天气数据")

        for element in weather_elements:
            day_weather_info = {}

            # 提取日期
            date_element = element.find_elements(By.XPATH, "./div[1]")
            day_weather_info['date_time'] = date_element[0].text.split(' ')[0] if date_element else ""

            # 提取最高气温
            high_element = element.find_elements(By.XPATH, "./div[2]")
            high = high_element[0].text if high_element else ""
            day_weather_info['high'] = high.replace("°C", "")

            # 提取最低气温
            low_element = element.find_elements(By.XPATH, "./div[3]")
            low = low_element[0].text if low_element else ""
            day_weather_info['low'] = low.replace("°C", "")

            # 提取天气
            weather_element = element.find_elements(By.XPATH, "./div[4]")
            day_weather_info['weather'] = weather_element[0].text if weather_element else ""

            weather_info.append(day_weather_info)

        print(f"成功爬取 {len(weather_info)} 条天气数据")
        return weather_info

    except Exception as e:
        print(f"爬取数据时出错: {e}")
        return []

    finally:
        # 关闭浏览器
        driver.quit()


# 数据写入CSV
try:
    base_url = "https://lishi.tianqi.com/sanya/"

    all_weathers = []

    # 遍历年份和月份
    for year in range(2021, 2022):  #爬取2021年的数据
        for month in range(1, 13):  # 1~12月
            url = f"{base_url}{year}{str(month).zfill(2)}.html"
            print(f"正在爬取 {year} 年 {month} 月的数据...")
            weathers = get_weather_data(url)
            all_weathers.extend(weathers)

    # 写入CSV文件
    with open('weather.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['日期', '最高气温', '最低气温', '天气'])

        for day_data in all_weathers:
            writer.writerow([
                day_data['date_time'],
                day_data['high'],
                day_data['low'],
                day_data['weather']
            ])

        print(f"全年数据已成功写入 weather.csv，共{len(all_weathers)}条记录")

except Exception as e:
    print(f"写入CSV文件时出错: {e}")