# -*- coding: utf-8 -*-
"""初始化数据"""

__author__ = 'lijingang'

import sys
import time

import libs.config as conf
from libs.log.logger import LoggerFactory
from dbs.db import DB

# 日志组件
logger = LoggerFactory.get_logger('dbinit')

class DBinit(object):
    def __init__(self):
        self.DB = DB()
        pass

    def create_database(self):
        self.DB.connect(True)
        self.DB.execute("CREATE DATABASE " + conf.env.DB_NAME + " DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
        self.DB.close()
        pass
    
    def create_tables(self):
        self.DB.connect()

        _sql = '''
        CREATE TABLE IF NOT EXISTS `anyun`.`m_platform` (
        `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
        `sn` VARCHAR(30) NOT NULL COMMENT '平台编号',
        `name` VARCHAR(30) NOT NULL COMMENT '平台名称',
        `type` VARCHAR(30) NOT NULL DEFAULT 'post' COMMENT '类型(post-发布/get-爬取)',
        `homeUrl` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '平台首页',
        `sdkClass` VARCHAR(30) NOT NULL DEFAULT '' COMMENT 'SDK类名',
        `isEnable` TINYINT(1) UNSIGNED NOT NULL DEFAULT 1 COMMENT '是否可用',
        `createTIme` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updateTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`))
        ENGINE = InnoDB;
        '''
        rtn = self.DB.execute(_sql)

        _sql = '''
        CREATE TABLE IF NOT EXISTS `anyun`.`m_platform_account` (
        `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
        `platformSn` VARCHAR(30) NOT NULL COMMENT '平台编号',
        `platformName` VARCHAR(30) NOT NULL COMMENT '平台名称',
        `loginname` VARCHAR(30) NOT NULL COMMENT '登录名',
        `loginpass` VARCHAR(30) NOT NULL COMMENT '登录密码',
        `phoneNum` VARCHAR(11) NOT NULL COMMENT '手机号码',
        `isEnable` TINYINT(1) NOT NULL DEFAULT 1 COMMENT '是否有效',
        `postUrl` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '发表博客URL',
        `createTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updateTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`))
        ENGINE = InnoDB;
        '''
        rtn = self.DB.execute(_sql)
        
        _sql = '''
        CREATE TABLE IF NOT EXISTS `anyun`.`m_post_task` (
        `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
        `title` VARCHAR(100) NOT NULL COMMENT '标题',
        `selfCategory` VARCHAR(30) NOT NULL DEFAULT '' COMMENT '个人分类',
        `tags` VARCHAR(30) NOT NULL DEFAULT '' COMMENT '标签',
        `content` TEXT NOT NULL COMMENT '内容',
        `status` VARCHAR(30) NOT NULL DEFAULT 'init' COMMENT '状态(init-初始/processing-处理中/success-成功/fail-失败)',
        `planPostTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '预定发布时间',
        `createTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updateTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`))
        ENGINE = InnoDB
        COMMENT = '发布任务表';
        '''
        rtn = self.DB.execute(_sql)

        _sql = '''
        CREATE TABLE IF NOT EXISTS `anyun`.`m_post_task_platform` (
        `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
        `taskId` INT NOT NULL COMMENT '任务ID',        
        `platformSn` VARCHAR(30) NOT NULL COMMENT '平台编号',
        `accountId` INT NOT NULL COMMENT '账户ID',
        `status` VARCHAR(30) NOT NULL DEFAULT 'init' COMMENT '状态(init-初始/processing-处理中/success-成功/fail-失败)',
        `detailUrl` VARCHAR(100) NOT NULL DEFAULT '' COMMENT '详情页URL',
        `viewCount` INT NOT NULL DEFAULT 0 COMMENT '浏览数量',
        `lastViewTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后浏览时间',
        `createTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        `updateTime` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`))
        ENGINE = InnoDB;
        '''
        rtn = self.DB.execute(_sql)

        self.DB.close()

    def create_data(self):
        self.DB.connect()

        # # m_platform
        # _data = [
        #     ('sinablog', '新浪博客', 'post', 'http://blog.sina.com.cn/', 'SinaSDK', 1, time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S')),
        #     ('hexunblog', '和讯博客', 'post', 'http://blog.hexun.com/', 'HexunSDK', 1, time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S'))
        # ]
        # _sql = "insert into m_platform(sn, name, type, homeUrl, sdkClass, isEnable, createTime, updateTime) values(%s, %s, %s, %s, %s, %s, %s, %s)"
        # # _sql = "insert into m_platform(sn, name, type, homeUrl, sdkClass, isEnable, createTime, updateTime) values('sinablog','新浪博客', 'post', 'http://blog.sina.com.cn/', 'SinaSDK', 1, '2019-01-28 14:53:05', '2019-01-28 14:53:05')"
        # # self.DB.executemany(_sql, _data)

        # m_platform_account
        _data = [
            # ('sinablog', '新浪博客', '17611240182', 'asdf12#$', '17611240182', 1, 'http://control.blog.sina.com.cn/admin/article/article_add.php?is_new_editor=1', time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S')),
            # ('hexunblog', '和讯博客', '17611240182', 'asdf12#$', '17611240182', 1, 'http://post.blog.hexun.com/31122825/newpostblog.aspx', time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S')),
            # ('sinablog', '新浪博客', '17611258729', 'asdf12#$', '17611258729', 1, 'http://control.blog.sina.com.cn/admin/article/article_add.php?is_new_editor=1', time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S')),
            # ('hexunblog', '和讯博客', '17611258729', 'asdf12#$', '17611258729', 1, 'http://post.blog.hexun.com/31122834/newpostblog.aspx', time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S')),

            ('newsmth', '水木社区', 'wolala99', 'wo@999999', '19010001001', 1, 0,
             'http://www.newsmth.net/nForum/index', time.strftime('%Y-%m-%d %H:%M:%S'),
             time.strftime('%Y-%m-%d %H:%M:%S')),

            ('newsmth', '水木社区', 'love777777', 'love@8989', '19010001002', 1, 0,
             'http://www.newsmth.net/nForum/index', time.strftime('%Y-%m-%d %H:%M:%S'),
             time.strftime('%Y-%m-%d %H:%M:%S')),

            ('newsmth', '水木社区', 'wiccpp', 'ccc@66699', '19010001003', 1, 0,
             'http://www.newsmth.net/nForum/index', time.strftime('%Y-%m-%d %H:%M:%S'),
             time.strftime('%Y-%m-%d %H:%M:%S')),

            ('newsmth', '水木社区', 'xiifly', 'yyy@666666', '19010001004', 1, 0,
             'http://www.newsmth.net/nForum/index', time.strftime('%Y-%m-%d %H:%M:%S'),
             time.strftime('%Y-%m-%d %H:%M:%S')),

            ('newsmth', '水木社区', 'goodbbb', 'wo@999999', '19010001005', 1, 0,
             'http://www.newsmth.net/nForum/index', time.strftime('%Y-%m-%d %H:%M:%S'),
             time.strftime('%Y-%m-%d %H:%M:%S')),

            ('newsmth', '水木社区', 'xgggy', 'yyy@666666', '19010001006', 1, 0,
             'http://www.newsmth.net/nForum/index', time.strftime('%Y-%m-%d %H:%M:%S'),
             time.strftime('%Y-%m-%d %H:%M:%S')),
        ]
        _sql = "insert into m_platform_account(platformSn, platformName, loginname, loginpass, phoneNum, isEnable, isPost, postUrl, createTime, updateTime) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.DB.executemany(_sql, _data)

        # # m_post_task
        # _content1 = '''
        # <div class="article-content"><p>有效能的亲子互动，不但拉近彼此的距离，也提升幼儿各项身心发展。不管多么忙碌，每天抽出一点时间陪伴孩子成长，或许你会从中获得不一样的惊喜。</p><div class="img-container"><img class="normal" data-loadfunc="0" src="https://ss1.baidu.com/6ONXsjip0QIZ8tyhnq/it/u=3387886969,2427578226&amp;fm=173&amp;s=AE5005C706DA7BDED23CBC1E03001050&amp;w=400&amp;h=300&amp;img.JPEG" data-loaded="0" width="400px"></div><p><span class="bjh-strong"><span class="bjh-br"></span><span class="bjh-br"></span></span></p><p><span class="bjh-br"></span><span class="bjh-br"></span></p><p><span class="bjh-strong">亲子互动效益多</span></p><p>孩子的成长只有一次，每天短短的互动，不仅有助于孩子的发展，父母也可从中观察孩子的成长历程。“尤其当小朋友是给他人代为照顾时，更能清楚了解，孩子的发展进度跟照顾者所说明的是否符合，”台北市保母协会理事长何云凤特别提出说明。</p><p>现代人工作繁忙，家长与孩子间互动的频率、时间也随之减少，“每天至少要有2小时的互动，”何理事长建议。互动过程中的“质”比“量”更重要。父母应依自己的体力、时间、目的等，来做互动方式的安排。如果今天工作很累，可以跟宝宝进行简单的按摩、柔和的运动，等到精神、体力较充足时，再换以较动态的活动即可。</p><div class="img-container"><img class="normal" data-loadfunc="0" src="https://ss2.baidu.com/6ONYsjip0QIZ8tyhnq/it/u=4264143341,3950306581&amp;fm=173&amp;s=01C2DD155C63448A469DE0EE03007062&amp;w=400&amp;h=300&amp;img.JPEG" data-loaded="0" width="400px"></div><p>特别需要家长注意的是，在跟宝宝游戏的过程中，要以孩子的角色来陪伴孩子，让孩子把大人当做是他的同伴，尤其对于独生子女来说，可以从中同时学习如何与团体、同侪相处。</p><p><span class="bjh-strong">天马行空的创意</span></p><p>进行亲子互动前，建议父母先学习一些必要的知识及方法，让活动的效能更加的发挥作用，包括“语言、视觉的发展、大小肌肉的发育，以及各年龄的发展进程等，设计亲子互动模式之前，都应先考量及学习相关知识之后，再加以运用于整个过程，”何理事长建议家长。另外，针对孩子不同的特质、年龄、能力去设计互动的方式，是否可以引起他的兴趣，都是应该要衡量的要素。</p><p><span class="bjh-br"></span><span class="bjh-br"></span></p><p>游戏设计也可以未来将会学习、使用的知识或是技能为主，但要注意整个游戏的难易度、适龄性、实用性等。举例来说，3岁以下的小朋友并不懂图画书中的内容，但是爸爸妈妈可以利用书中的图片、游戏等的说明，进一步培养他的视力、色彩的辨别等的能力。当孩子已经达到现阶段的目标时，家长可适度的调整游戏的难度，让他的能力可以更往前迈进。</p><div class="img-container"><img class="normal" data-loadfunc="0" src="https://ss0.baidu.com/6ONWsjip0QIZ8tyhnq/it/u=1082045148,730573433&amp;fm=173&amp;s=11227433457257845A5529E90300E022&amp;w=500&amp;h=333&amp;img.JPEG" data-loaded="0" width="500px"></div><p>“适时的加入创意元素，”是亲子互动里相当重要的一环，何理事长表示。游戏的过程中，当孩子表现预期外的行为，不妨鼓励孩子发挥创意、潜力，加入新的创意方式，跟孩子一起创造新的游戏方式，或是让游戏的方式更加的完美等，不要限制孩子创意及想象的空间。</p></div>
        # '''
        # _content2 = '''
        # <div class="article-content"><p><span class="bjh-p"></span></p><div class="img-container"><img class="large" data-loadfunc="0" src="http://t10.baidu.com/it/u=1148749497,629561652&amp;fm=173&amp;app=25&amp;f=JPEG?w=600&amp;h=86" data-loaded="0"></div><p><span class="bjh-p">大部分家长都知道亲子阅读是非常重要的亲子互动一步，不仅仅可以增进母子的关系，而且还可以提高孩子的认知能力，提高他们的阅读量以及思维空间。</span></p><div class="img-container"><img class="large" data-loadfunc="0" src="http://t10.baidu.com/it/u=3758561646,453416793&amp;fm=173&amp;app=25&amp;f=JPEG?w=590&amp;h=388&amp;s=D018AE7609D64EDA42DBE57C0300E07A" data-loaded="0"></div><p><span class="bjh-p"><span class="bjh-br"></span></span></p><p><span class="bjh-p">小编自从孩子一岁半岁左右就开始给他讲睡前故事。也让孩子养成一个固定的睡觉模式，那就是睡觉之前给他讲故事。现在孩子已经大概四周岁左右了，可以讲很多本故事书，认的字卡也超过一百字以上，并不是说小编在这里夸奖自己的孩子，而是想跟你们讲，每天坚持亲子阅读的话会有一个具有很多的好处。那么具体的好处又有哪些呢？下面小编来简单的说一下。</span></p><p><span class="bjh-h3">第一、增加母子之间的亲密度</span></p><p><span class="bjh-p">有时候小编在跟孩子讲故事的时候，我们有时候会针对故事里面的角色某一个行为而互相讨论，发表自己的看法。孩子有时候会看到这个故事搞笑的片段而哈哈大笑。这样子的行为，会让母子之间沟通起来更为的顺畅。以前孩子小的时候看的大多数是生字动画卡片，后来慢慢的就是小故事跟绘本。现在对于他来说故事并不是枯燥东西，而是一件有趣的事情。</span></p><div class="img-container"><img class="large" data-loadfunc="0" src="http://t10.baidu.com/it/u=2062643019,234929117&amp;fm=173&amp;app=25&amp;f=JPEG?w=597&amp;h=390&amp;s=F01AAE761D5255CE1AD9807A0300607B" data-loaded="0"></div><p><span class="bjh-p"><span class="bjh-br"></span></span></p><p><span class="bjh-h3">第二、讲故事也是另一种教育方式</span></p><p><span class="bjh-p">小编并没有针对性的听某些教育专家购买哪些故事，而是带孩子自己去书店，让孩子自主选择他自己所感兴趣的绘本，然后再从中讲解。小编最喜欢买的故事书，那就是睡前故事。而通过讲睡前故事，小编有时候会对孩子错误的行为善加引导，比如说老师说孩子在幼儿园犯了什么错误，那么小编就会跟孩子讲他的行为是不是跟故事里面的某一个人物的行为是一样的呢？如果他在持续这样子做的话，那么他会跟故事里面的某一个角色一样都是不受欢迎的。这样子教育的话更加的轻松。</span></p><div class="img-container"><img class="normal" data-loadfunc="0" src="http://t12.baidu.com/it/u=3631860536,3538924131&amp;fm=173&amp;app=25&amp;f=JPEG?w=519&amp;h=305&amp;s=7C28BE5741506DCE52FF386803005038" data-loaded="0" width="519px"></div><p><span class="bjh-p"><span class="bjh-br"></span></span></p><p><span class="bjh-h3">第三、就是培养孩子自己固定的一个睡眠模式</span></p><p><span class="bjh-p">一般小编给孩子讲故事，都是讲睡前故事的。那么在之前小编就会让他自己把所有的玩具收拾好，下一步自己去刷牙洗脸。这样子他自己就会养成一个固定的睡觉模式。如果我要听故事了，那么我现在要做的就是一些准备的行为。他自己会有意识地把这些行为都给完成，所以说读故事的话可以利于他们培养自己的时间观念和行为能力。</span></p><div class="img-container"><img class="large" data-loadfunc="0" src="http://t10.baidu.com/it/u=3977658180,3573518034&amp;fm=173&amp;app=25&amp;f=JPEG?w=640&amp;h=480&amp;s=B09AAF77D3ABC54D024B2C690300E078" data-loaded="0"></div><p><span class="bjh-p"><span class="bjh-br"></span></span></p><p><span class="bjh-p">作为妈妈的你，有留出和孩子的亲子阅读时间吗？你有哪些新颖的方式呢？一起交流一下帮助孩子们共同成长！<span class="bjh-br"></span></span></p><p><span class="bjh-p"><span class="bjh-br"></span></span></p><p><span class="bjh-p"><span class="bjh-br"></span></span></p><p><span class="bjh-p"></span></p></div>
        # '''
        # _data = [
        #     ('父母须知——亲子互动好处多', '亲子阅读', '亲子 互动', _content1, 'init', time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S')),
        #     ('亲子阅读这三大好处，聪明的父母都应该这么做！', '亲子阅读', '亲子 互动', _content2, 'init', time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S'), time.strftime('%Y-%m-%d %H:%M:%S'))
        # ]
        # _sql = "insert into m_post_task(title, selfCategory, tags, content, status, planPostTime, createTime, updateTime) values(%s, %s, %s, %s, %s, %s, %s, %s)"
        # # self.DB.executemany(_sql, _data)



        self.DB.commit()
        self.DB.close()

if __name__ == '__main__':
    logger.info("db init begin")
    
    _dbinit = DBinit()

    # _dbinit.create_database()
    # _dbinit.create_tables()
    _dbinit.create_data()

    logger.info("db init end")