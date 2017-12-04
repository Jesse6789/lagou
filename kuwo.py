# coding=utf-8
import pymysql
import re
import requests
from bs4 import BeautifulSoup


class kuwo(object):
    # 执行次数 ,可用于计数和爬到 x 首时停止
    flag = 0
    # 队列
    polls = ['http://www.kuwo.cn']

    # 文件储存的位置
    filePath = './musics.list'

    '''
        链接数据库并 执行Sql语句
    '''

    def execs(self, sql):
        db = pymysql.connect("127.0.0.1", "music", "root", "music")
        cursor = db.cursor()
        cursor.execute('SET NAMES utf8;')
        cursor.execute(sql)
        db.commit()
        data = cursor.fetchone()
        db.close()
        return data

    def join(self, url, title):
        '''
            插入一首音乐到数据库的音乐表
            删除重复的
            DELETE FROM `music` WHERE `url` IN( SELECT `url` FROM `music` GROUP BY `url` HAVING COUNT(*) > 1 )
            AND `id` NOT IN( SELECT MIN(`id`) FROM `music` GROUP BY `id` HAVING COUNT(*) > 1 )

            查询出单独的URL ,并统计数量
            SELECT title ,COUNT(id) FROM `music` GROUP BY url ,title ORDER BY id DESC
        '''
        return self.execs(
            "INSERT INTO `music` (`id`, `url`, `title`) VALUES (NULL, '%s', '%s')"
            % (
                url.encode("utf-8").decode("latin1"), title.encode("utf-8").decode("latin1"),
            )
        )

    def parseATag(self, tag, prefixUrl="http://www.kuwo.cn"):
        '''
            解析 bs4 处理过的 A标记
        '''
        # 拿到href值
        href = str(tag.get('href'));
        # 过滤资源和 js 链接
        pattern = re.compile(r'javascript.+|.+jpg|.+JPG|.+png|.+jpeg|.+PNG|.+JPEG|.+pdf|.+exe|.+apk')
        if pattern.match(href):
            return False;

        # 过滤站点根目录 避免死循环处理
        pattern = re.compile(r'.+\.com$|.+\.cn$|.+\.com\/$|.+\.cn\/$')
        if pattern.match(href):
            return False

        # 过滤出音乐的链接 并写入到文件中
        pattern = re.compile(r'.+kuwo.+yinyue\/\d')
        if pattern.match(href):
            return self.saveMusicInfo(tag)

        # 过滤是否带有http或者https前缀 ,不带则需要拼接
        pattern = re.compile(r'http|https.+')
        if pattern.match(href):
            # 判断是否在本站 ,如果是则返回 ,不是则不处理 ,避免跳转到其他站点
            pattern = re.compile(r'.+kuwo.+')
            if pattern.match(href):
                return href;
        else:
            pattern = re.compile(r'.+kuwo.+')
            if pattern.match(href):
                # 拼接URL前缀
                return prefixUrl + str(href)

    def saveMusicInfo(self, tag):
        '''
            在文件或数据库中追加一条数据
        '''
        self.flag += 1
        self.writeFile(self.filePath, '%s         %s\n' % (tag.get('href'), tag.text));
        # 可选操作 写入数据库
        self.join(tag.get('href'), tag.text)
        return False

    def writeFile(self, path, content):
        '''
            写入文件 ,文件名 ,写入内容
        '''
        file = open(path, 'a+', encoding='utf-8');
        file.write(content);
        file.close();
        return False

    def do(self, url):
        ''' 执行任务 ,爬取某个url
        '''
        # 从队列中移除自己 ,避免重复请求
        self.polls.remove(url)
        # 请求HTML资源
        data = requests.get(url)
        # 拿到HTML交由bs4使用lxml解析器处理
        soup = BeautifulSoup(data.text, 'lxml');
        # 拿到文件中的所有a标记
        urls = soup.find_all('a')
        ''' 遍历所有的a标记
        '''
        for url in urls:
            # 处理这个url 音乐则存起来 ,其他则返回回来插入队列
            url = self.parseATag(url)
            # 判断返回的url不是false 且不在队列中 避免重复抓取
            if url and url not in self.polls:
                # 插入队列
                self.polls.append(url)

        ''' 死递归处理队列 python 默认递归深度是998 ,可以调节 ,
            但是这里其实没有必要用递归 ,就改了
            
            # 延时0.1秒
            time.sleep(0.1)
            # 处理完一个链接 ,将下一个需要处理的不是音乐的链接地址作为标题写入文件
            self.writeFile(self.filePath, '<h1>%s</h1>' % (self.polls[0]));
    
            # 打印到控制台处理完成的链接 ,和即将进行处理的下一个链接 ,
            print('success Url : %s ,Next Url : %s \n' % ( url ,self.polls[0]))
    
            # 递归处理队列中的第1一个链接
            self.do(self.polls[0]);
        '''


''' 初始化第一个链接
	http://other.web.nf03.sycdn.kuwo.cn/07028ed6a3b05d09d1518e8b2cee8dad/5a214137/resource/a1/31/30/1022995145.aac
	http://www.kuwo.cn/yinyue/24720751?catalog=yueku2016
'''
kuwo().do('http://www.kuwo.cn');

# 死循环处理队列 没有深度限制
while True:
    # 延时0.1秒
    # time.sleep(0.1)
    # 处理完一个链接 ,将下一个需要处理的不是音乐的链接地址作为标题写入文件
    kuwo().writeFile(kuwo().filePath, '' % (kuwo().polls[0], kuwo().polls[0]));

    # 打印到控制台即将进行处理的下一个链接 ,
    print(kuwo().polls[0])

    # 递归处理队列中的第1一个链接
    kuwo().do(kuwo().polls[0]);
