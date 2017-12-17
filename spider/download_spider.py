# -*- coding: UTF-8 -*-
import requests
import datetime
import pymysql
import pandas as pd
import time
import shutil
import zipfile
import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#KRC96wyxALKp
conn = pymysql.connect(host='127.0.0.1', user='root', passwd='344126509', db='yahoo', charset='utf8')
cur = conn.cursor()
# ---------------------------------------------------------------


"""
#--------------------------------------------------------------------
dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0")  # 设置user-agent请求头
dcap["phantomjs.page.settings.loadImages"] = False  # 禁止加载图片

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/603.2.4 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.4',
    'Connection': 'keep-alive'
}

cap = DesiredCapabilities.PHANTOMJS.copy()#使用copy()防止修改原代码定义dict

for key, value in headers.items():
    cap['phantomjs.page.customHeaders.{}'.format(
        key)] = value

driver = webdriver.PhantomJS(desired_capabilities=dcap,executable_path='/home/david/phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
driver.set_page_load_timeout(40)  # 设置页面最长加载时间为40s
"""

# --------------------------------------------------------------------
def dir_to_zip(startdir):
    file_news = startdir + '.zip'  # 压缩后文件夹的名字
    z = zipfile.ZipFile(file_news, 'w', zipfile.ZIP_DEFLATED)  # 参数一：文件夹名
    for dirpath, dirnames, filenames in os.walk(startdir):
        fpath = dirpath.replace(startdir, '')  # 这一句很重要，不replace的话，就从根目录开始复制
        fpath = fpath and fpath + os.sep or ''  # 这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
        for filename in filenames:
            z.write(os.path.join(dirpath, filename), fpath + filename)
            # print ('压缩成功')
    shutil.rmtree(startdir)
    z.close()

def get_driver_cookies(driver):
    cookie = [item["name"] + ":" + item["value"] for item in driver.get_cookies()]
    cook_map = {}
    for item in cookie:
        str = item.split(':')
        cook_map[str[0]] = str[1]
    cookies = requests.utils.cookiejar_from_dict(cook_map, cookiejar=None, overwrite=True)
    return cookies

def date_to_stamp(date):
    l = date.split('/')
    m = l[0].zfill(2)
    d = l[1].zfill(2)
    y = l[2]

    dt = y+'-'+m+'-'+d+' '+'0:0:0'
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    # 转换成时间戳
    timestamp = str(time.mktime(timeArray))[0:-2]
    return timestamp


def get_driver_info(driver, code='AAPL'):
    driver.get('https://finance.yahoo.com/quote/' + code + '/history?p=' + code)
    time.sleep(1)
    driver.find_element_by_id('Col1-1-HistoricalDataTable-Proxy').find_element_by_tag_name('svg').click()  # 找到小箭头

    try:  # 找到MAX并且点击
        ele = WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located((By.XPATH,
                                                                                   '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/span[2]/div/div[1]/span[8]/span')))
        ele.click()
        time.sleep(1)

    finally:
        pass

    end_date = driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/span[2]/div/input[2]').get_attribute('value')

    try:  # 找到Done并且点击
        ele = WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located((By.XPATH,
                                                                                   '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/span[2]/div/div[3]/button[1]')))
        ele.click()
        time.sleep(1)

    finally:
        pass

    try:  # 找到Apply并且点击
        ele = WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button')))
        ele.click()
        time.sleep(1)

    finally:
        pass

    # driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button').click()#找到Apply按钮并且点击
    time.sleep(5)
    hr = driver.find_element_by_xpath(
        '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]/a').get_attribute(
        'href')  # 找到下载按钮并且点击
    crumb = hr[hr.index('crumb') + 6:]
    cookies = get_driver_cookies(driver)
    end_date = date_to_stamp(end_date)
    return  cookies, crumb, end_date

def download_this_code(code, driver):

    driver.get('https://finance.yahoo.com/quote/' + code + '/history?p=' + code)

    driver.find_element_by_id('Col1-1-HistoricalDataTable-Proxy').find_element_by_tag_name('svg').click()  # 找到小箭头

    try:  # 找到MAX并且点击
        ele = WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located((By.XPATH,
                                                                                   '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/span[2]/div/div[1]/span[8]/span')))
        ele.click()
        time.sleep(1)

    finally:
        pass
    # driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/span[2]/div/div[1]/span[8]/span').click()#找到MAX并且点击

    #
    try:  # 找到Done并且点击
        ele = WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located((By.XPATH,
                                                                                   '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/span[2]/div/div[3]/button[1]')))
        ele.click()
        time.sleep(1)

    finally:
        pass
    # driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/span[2]/div/div[3]/button[1]').click()#找到Done按钮并且点击

    try:  # 找到Apply并且点击
        ele = WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button')))
        ele.click()
        time.sleep(1)

    finally:
        pass

    # driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/button').click()#找到Apply按钮并且点击
    time.sleep(3)
    hr = driver.find_element_by_xpath(
        '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[2]/span[2]/a').get_attribute(
        'href')  # 找到下载按钮并且点击
    print(hr)
    print(hr[hr.index('crumb') + 6:])
    print(datetime.datetime.now())
    cookies = get_driver_cookies(driver)  # 获取cookies
    r = requests.get(hr, cookies=cookies)
    with open("C:/Users/David/Documents/test/" + code + ".csv", "wb") as code:
        code.write(r.content)
    time.sleep(1)

def get_code_start_date(driver,code):
    driver.get('https://finance.yahoo.com/quote/' + code + '/history?p=' + code)
    time.sleep(1)
    driver.find_element_by_id('Col1-1-HistoricalDataTable-Proxy').find_element_by_tag_name('svg').click()  # 找到小箭头

    try:  # 找到MAX并且点击
        ele = WebDriverWait(driver, 10, 0.1).until(EC.presence_of_element_located((By.XPATH,
                                                                                   '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/span[2]/div/div[1]/span[8]/span')))
        ele.click()
        time.sleep(1)

    finally:
        pass

    start_date = driver.find_element_by_xpath('//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[1]/div[1]/div[1]/span[2]/div/input[1]').get_attribute('value')
    start_stamp = str(date_to_stamp(start_date))

    print(start_stamp)
    return start_stamp

#print(get_driver_info(driver))


def get_all_start_stamp():
    codes = pd.read_csv('/home/david/codes.csv')
    for c in codes.codes:
        time.sleep(1)
        pass
        print(c)

        cur.execute("SELECT code FROM codes_start_stamp WHERE code=%s", (c))
        if len(cur.fetchall()[0:100]) != 0:
            print('数据库已经存在此公司。')
            continue

        else:
            print(c)


        try:
            start_stamp = get_code_start_date(driver,c)
            cur.execute('INSERT INTO codes_start_stamp (code, start_stamp) VALUES (%s, %s)', (c, start_stamp))
            cur.connection.commit()
            driver.get_screenshot_as_file('success.png')
        except Exception as e:
            driver.get_screenshot_as_file('defeat.png')
            print(e)

def do_the_task(task_datetime,driver,cookies, crumb, end_date):
    task_dir = '/home/david/codes_historical_data/'+task_datetime

    codes = pd.read_csv('/home/david/codes.csv')
    codes_stamp = pd.read_csv('/home/david/codes_start_stamp.csv')
    total = len(codes.codes)

    try:
        os.makedirs(task_dir)
    except:
        pass
    n = 1
    for c in codes.codes:
        n+=1
        succ = round((n/total),3)*100
        cur.execute("UPDATE main_task SET success=%s;", succ)
        cur.connection.commit()
        
        try:
            stamp = codes_stamp[codes_stamp.code == c]
            temp = len(stamp.index) / len(stamp.index)  # 测试如果长度为零则报错
            for s in stamp.start_stamp:
                # print(s)
                stamp = s
                print('no need new get')
                break

        except Exception as e :#如果文件内没有start_stamp
            print('need new get')
            try:
                stamp = get_code_start_date(driver,c)
                codes_stamp.loc[len(codes_stamp)] = [c, stamp]
                codes_stamp.to_csv('/home/david/codes_start_stamp.csv',index=False)
            except Exception as e :
                print(e)
                if 'NaN-NaN' in e:
                    pass
                else:
                    break

                continue


        url = 'https://query1.finance.yahoo.com/v7/finance/download/' + c + '?period1='+str(stamp)+'&period2='+str(end_date)+'&interval=1d&events=history&crumb='+str(crumb)
        print(url)
        #cookies = get_driver_cookies(driver)  # 获取cookies
        try:
            r = requests.get(url, cookies=cookies)
            with open(task_dir + '/' + c + ".csv", "wb") as code:
                code.write(r.content)
            time.sleep(1)
        except:
            pass
    dir_to_zip(task_dir)


#get_all_start_stamp()
while True:
    time.sleep(10)
    cur.execute("SELECT date_time FROM main_task WHERE status=%s", '正在爬取')
    task = cur.fetchall()[0:100]
    if len(task) != 0:
        #-------------------------
        try:#初始化浏览器
            chrome_opt = webdriver.ChromeOptions()
            prefs = {'profile.managed_default_content_settings.images': 2}
            chrome_opt.add_experimental_option('prefs', prefs)
            chrome_opt.add_argument('--headless')
            chrome_opt.add_argument('--disable-gpu')
            driver = webdriver.Chrome(chrome_options=chrome_opt)
            driver.set_page_load_timeout(40)  # 设置页面最长加载时间为40s
            cookies, crumb, end_date = get_driver_info(driver=driver)
        except:
            try:
                driver.quit()
            except:
                pass
            continue
        #-------------------------
        print(str(task[0][0]))
        do_the_task(str(task[0][0]),driver=driver,cookies=cookies,crumb=crumb, end_date=end_date)
        cur.execute("UPDATE main_task SET status=%s;",'已完成')
        cur.connection.commit()
        driver.quit()
        continue

    else:
        pass
