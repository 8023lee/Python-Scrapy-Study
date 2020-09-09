# -*- conding:utf-8 -*-

import time
import threading

from libs.log.logger import LoggerFactory
from task.post.task_post import TaskPost
from dbs.model.account import Account as AccountModel

# 日志组件
logger = LoggerFactory.get_logger()


def batch_task_run():
    threads = []

    # 获取账号信息
    account_model = AccountModel()
    accounts = account_model.get_post_accounts()

    for key, val in accounts.items():
        # print(key, val)
        task = TaskPost(val)
        t = TaskThread(task)
        t.start()

        logger.info('start thread %s' % key)
        
        threads.append(t)

        # 间隔 5 秒，启动下一个线程
        time.sleep(5)

    for thread in threads:
        thread.join()

    logger.info('All thread done!!!!!')

    return "0"


class TaskThread(threading.Thread):
    task = None

    def __init__(self, task):
        super().__init__()
        self.task = task

    def run(self):
        if self.task:
            self.task.do_process()
        else:
            logger.error('task is None！')


if __name__ == '__main__':
    logger.info('==== post-main runing start ====')

    rtn = batch_task_run()

    logger.info('==== post-main runing end ====')
