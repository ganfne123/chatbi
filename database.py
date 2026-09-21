from fastapi import HTTPException
import re
from typing import Tuple
from asyncio import wait
import pymysql
from config import database_config

class DatabaseClient:
    def __init__(self):
        self.config=database_config


    def health_check(self) -> bool :
        """检查数据库连接，返回状态和原始错误信息。"""
        conn = None
        try:
            conn = pymysql.connect(**self.config, connect_timeout=5)
            return  True
        except Exception as exc:
            raise HTTPException(500,f"数据库连接失败，错误信息：{exc}")
        finally:
            if conn is not None:
                conn.close()


    def execute(self,sql : str) ->Tuple[list[str],list[tuple]]:
        """执行sql"""
        conn=pymysql.connect(**self.config)
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                if cursor.description:
                    columns = [desc[0] for desc in cursor.description]
                else:
                    columns = []
                results = cursor.fetchall()
            return  columns,results
        finally:
            conn.close()

if __name__=='__main__':
    pass
