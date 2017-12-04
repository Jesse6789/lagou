# coding=utf-8
from bs4 import BeautifulSoup
import requests
import json
import pymysql
import time
import threading


def soup(url):
    '''
        获得soup
        工作进程 ,header按需修改
    '''
    res = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'user_trace_token=20171202100105-a80125c3-d704-11e7-9b87-5254005c3644; LGUID=20171202100105-a8012ec6-d704-11e7-9b87-5254005c3644; mds_login_authToken="HuQadT2xOmgTtzyrjEXWbCZBqF90Sm+utXdB10g7nB4ZV3kEiPRkZK4jCKBxlexgiXeToX0T5oUzcG3WaATPbPE/U3nkgSaGSaq/lk+spWiya6BTxgLlp3gGmyem8RmDsksemP9DQjIp7bhxxWM36FQp6QyihUj1Ix6/8BPa5d14rucJXOpldXhUiavxhcCELWDotJ+bmNVwmAvQCptcy5e7czUcjiQC32Lco44BMYXrQ+AIOfEccJKHpj0vJ+ngq/27aqj1hWq8tEPFFjdnxMSfKgAnjbIEAX3F9CIW8BSiMHYmPBt7FDDY0CCVFICHr2dp5gQVGvhfbqg7VzvNsw=="; X_HTTP_TOKEN=cc3f27fa5889092c3bc56e2c7e7bad7c; JSESSIONID=ABAAABAAAFCAAEG4234FBDA9A8263A9366071F51723D691; PRE_UTM=; PRE_HOST=; PRE_SITE=https%3A%2F%2Fwww.lagou.com%2Fzhaopin%2FPHP%2F7%2F%3FfilterOption%3D2; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2Fjobs%2Flist_%3Fcity%3D%25E5%2585%25A8%25E5%259B%25BD%26cl%3Dfalse%26fromSearch%3Dtrue%26labelWords%3D%26suginput%3D; TG-TRACK-CODE=search_code; _putrc=C7768FD2791AD7E5; login=true; unick=%E5%88%98%E9%9D%9E%E5%87%A1; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; SEARCH_ID=d4ca3a89328c49e38d9ea83b139c913e; index_location_city=%E5%85%A8%E5%9B%BD; _gat=1; _ga=GA1.2.272928687.1512180066; _gid=GA1.2.1427659055.1512180066; LGSID=20171202155045-81314b77-d735-11e7-bbd8-525400f775ce; LGRID=20171202160558-a13d7b61-d737-11e7-9b90-5254005c3644; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1512180066,1512181406,1512182491; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1512201959',
        'Host': 'www.lagou.com',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
    })
    return BeautifulSoup(res.text, 'lxml')


def execs(sql):
    '''
        执行一条 SQL 语句
    '''
    db = pymysql.connect("localhost", "music", "root", "music")
    cursor = db.cursor()
    cursor.execute('SET NAMES utf8;')
    cursor.execute(sql)
    db.commit()
    data = cursor.fetchone()
    db.close()
    return data


def join(name, industry, logo, job, profit, welfare, url, page, type, address, money, li_b_l):
    '''
        插入一条数据到数据库
    '''
    return execs(
        "INSERT INTO `jobss` (`id`, `name`, `industry`, `logo`, `job`, `profit`, `welfare`, `url`, `created_at` ,`page` ,`type` ,`address` ,`money` ,`li_b_l`) VALUES (NULL, '%s', '%s', '%s', '%s', '%s', '%s', '%s', CURRENT_TIMESTAMP ,'%s' ,'%s' ,'%s','%s' ,'%s' )" % (
            name.encode("utf-8").decode("latin1"),
            json.dumps(industry, ensure_ascii=False).encode("utf-8").decode("latin1"),
            logo.encode("utf-8").decode("latin1"),
            job.encode("utf-8").decode("latin1"),
            json.dumps(profit, ensure_ascii=False).encode("utf-8").decode("latin1"),
            json.dumps(welfare, ensure_ascii=False).encode("utf-8").decode("latin1"),
            url.encode("utf-8").decode("latin1"),
            str(page),
            str(type),
            str(address).encode("utf-8").decode("latin1"),
            str(money).encode("utf-8").decode("latin1"),
            str(li_b_l).encode("utf-8").decode("latin1")
        ))


def do(job):
    '''
        一个爬虫线程
    '''
    # 拿到总页数 ,异常不处理 ,继续执行
    try:
        pages = soup('https://www.lagou.com/zhaopin/' + str(job) + '/1').select('.totalNum')[0].text
    except ():
        pages = soup('https://www.lagou.com/zhaopin/' + str(job) + '/1').select('.totalNum')[0].text

    res = []
    # 遍历所有页
    for page in range(1, int(pages) + 1):

        # 得到本页的所有职位信息
        positions = soup('https://www.lagou.com/zhaopin/' + str(job) + '/' + str(page)).select(
            '.item_con_list .con_list_item')

        # 遍历本页所有职位信息
        for position in positions:

            #  每个信息的详细数据
            info = {
                #  企业名
                'name': position.select('.list_item_top .company .company_name a')[0].text,
                # 企业性质
                'industry': position.select('.list_item_top .company .industry')[0].text.strip().split(' / ', 1),
                # 招聘职位
                'job': position.select('.list_item_top .position .p_top h3')[0].text,
                # 所在地
                'address': position.select('.list_item_top .position .p_top span em')[0].text,
                # 薪资
                'money': position.select('.list_item_top .position .p_bot .money')[0].text,
                # 岗位要求
                'li_b_l': position.select('.list_item_top .position .li_b_l')[0].text.strip()[7, -1],
                # 企业LOGO
                'logo': 'https:' + position.select('.list_item_top .com_logo a img')[0].get('src'),
                # 职位标签
                'profit': position.select('.list_item_bot .li_b_l')[0].text[1:-1].split(),
                # 福利待遇
                'welfare': position.select('.list_item_bot .li_b_r')[0].text[1:-1].split(',', 1),
                # 职位对应的URL
                'url': position.select('.list_item_top .position .p_top a')[0].get('href'),
            }

            # 控制台打印出当前爬取的职位类别 企业名 所在页
            print(job + ' ----  P' + str(page) + ' --- ' + info['name'] + '\n')

            # 把改企业的信息插入数据库
            join(info['name'], info['industry'], info['logo'], info['job'], info['profit'], info['welfare'],
                 info['url'], page, job, info['address'], info['money'], info['li_b_l'])

            # 爬取完成等待1秒 ,拉钩有请求频率的限制 ,经过测试1秒就很稳定
            time.sleep(1)
            # res.append(info)


# 工作列表池 ,需要爬取的分类
works = (
    'PHP',
    'Python',
    'JavaScript',
    'webqianduan',
    'Node.js',
    'Java',
    'HTML5',
    'UIshejishi',
    'pingmianshejishi',
    'chanpinjingli1',
    'iOS',
    'shoujiceshi',
    'zidonghuaceshi',
    'ceshigongchengshi',
    'C++',
    'Android',
    'APPshejishi',
    'go',
    'Ruby',
    'Hadoop',
    'sousuosuanfa',
    'shujuwajue',
    'quanzhangongchengshi',
    'asp',
    'shichangyingxiao1',
    'fawu2',
    'houduankaifaqita',
    'yunweikaifagongchengshi',
    'C%23',
);

'''
    多线程处理 ,已经废弃 ,改为单线程循环
'''
# 线程池
workers = []

# 把所有任务都加入线程池
for work in works:
    do(work);
    # workers.append(threading.Thread(target=do, args=(work)))

exit();
# 开始所有线程
for worker in workers:
    worker.setDaemon(True)
    worker.start()
