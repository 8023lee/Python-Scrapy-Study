# -*- coding: utf-8 -*-

"""
生成SinaBlog任务
"""

__author__ = 'lijingang'

import time
import datetime

from optparse import OptionParser

from dbs.db import DB
from libs.log.logger import LoggerFactory


class TaskCreateTrans:
    def __init__(self, from_platform_sn = 'csdn', to_platform_sn='sinablog', plan_posttime = ''):
        self.from_platform_sn = from_platform_sn
        self.to_platform_sn = to_platform_sn
        self.plan_posttime = plan_posttime

        if not self.plan_posttime:
            # self.plan_posttime = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            self.plan_posttime = datetime.date.today().strftime("%Y-%m-%d")

        self.DB = DB()
        self.logger = LoggerFactory.get_logger('task-create-trans')

    def run(self):
        while True:
            try:
                self.DB.connect()

                # 获取前一天csdn发布成功的任务
                sql = "select a.taskId, min(a.detailUrl) as detailUrl " \
                      "from m_post_task_platform as a " \
                      "     inner join m_post_task as b on a.taskId = b.id " \
                      "where a.platformSn='%s' and a.status ='success' and b.planPostTime <= '%s' " \
                      " and a.taskId not in (select taskId from m_post_task_platform where platformSn = '%s') " \
                      "group by a.taskId" \
                      % (self.from_platform_sn, self.plan_posttime, self.to_platform_sn)

                self.logger.info('获取前一天csdn发布成功的任务：%s' % sql)

                task_platforms = self.DB.fetchall(sql)

                # 获取sina账号
                sql = "select id, platformSn from m_platform_account where isEnable = 1 and isPost = 1 and platformSn = '%s'" % self.to_platform_sn
                accounts = self.DB.fetchall(sql)

                self.logger.info('获取sina账号：%s' % sql)

                # 生成sina任务
                if task_platforms and accounts:
                    acct_index = 0
                    data = []
                    for task_platform in task_platforms:
                        acct = accounts[acct_index]

                        data.append((task_platform['taskId'], acct['platformSn'], acct['id'], 'init', task_platform['detailUrl']))

                        acct_index += 1
                        if acct_index == len(accounts):
                            acct_index = 0

                    # 写入数据库
                    sql = 'insert into m_post_task_platform(taskId, platformSn, accountId, status, refUrl) values(%s, %s, %s, %s, %s)'
                    if data:
                        affected_rows = self.DB.executemany(sql, data)

                        self.logger.info('写入数据库 %d' % affected_rows)

                self.DB.commit()

            except Exception as ex:
                self.DB.rollback()
                self.logger.exception(str(ex))
            finally:
                self.DB.close()

            self.logger.info('刷新一轮完成后，休息 24 小时')
            time.sleep(24 * 60 * 60)


if __name__ == '__main__':
    # 设置帮助参数
    usage = """Example: 'python %prog -f csdn -t sinablog -p 2019-04-15'"""
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--fromPlatformSn", action="store", type="string", dest="fromPlatformSn", metavar="[csdn]",
                      help="源平台编号")
    parser.add_option("-t", "--toPlatformSn", action="store", type="string", dest="toPlatformSn", metavar="[sinablog]",
                      help="目的平台编号")
    parser.add_option("-p", "--planPostTime", action="store", type="string", dest="planPostTime", metavar="[YYYY-MM-DD]",
                      help="源平台任务发布日期")
    (options, args) = parser.parse_args()

    if not options.fromPlatformSn:
        options.fromPlatformSn = 'csdn'
    if not options.toPlatformSn:
        options.toPlatformSn = 'sinablog'

    task_create_trans = TaskCreateTrans(options.fromPlatformSn, options.toPlatformSn, options.planPostTime)
    task_create_trans.run()
