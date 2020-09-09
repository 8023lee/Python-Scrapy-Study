# -*- coding: utf-8 -*-

"""
"""


__author__ = 'lijingang'


from dbs.model.posttask_platform import PostTaskPlatform as PostTaskPlatformModel
from mscrapy.middlewares.pipeline.mysql import MysqlPipeline


class PostTaskPlatformPipeline(MysqlPipeline):

    name = 'PostTaskPlatformPipeline'

    def __init__(self):
        super().__init__()

    def process_item(self, item, spider):
        if item['viewCount']:
            id = item['id']
            posttask_platform_model = PostTaskPlatformModel()
            # 覆盖Model里的DB，避免每次都重新打开数据库连接
            posttask_platform_model.DB = self.DB
            affected_rows = posttask_platform_model.update(item)
            if affected_rows:
                self.logger.info('更新[m_post_task_platform.id=%d]的viewCount成功。' % id)
            else:
                self.logger.info('更新[m_post_task_platform.id=%d]的viewCount失败, viewCount=%s, aff_rows=%d。' % (id, item['viewCount'], affected_rows))
        else:
            self.logger.info('更新[m_post_task_platform.id=%d]的viewCount失败, viewCount=%s。' % (id, item['viewCount']))

        return item


