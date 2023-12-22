import time
from typing import Dict, List

from pydantic import BaseModel

from src.conf import config


class AccRecord(BaseModel):
    ip: str
    recent_access_records: List = []
    banned_until: int = 0

    def calc_access_qps(self, sec: int) -> float:
        """计算最近 sec 秒的访问频率"""
        now = time.time()
        recent_records = [
            record for record in self.recent_access_records if record > now - sec
        ]
        return len(recent_records) / sec

    def drop_expired_records(self, sec: int):
        """删除过期的访问记录"""
        now = time.time()
        self.recent_access_records = [
            record for record in self.recent_access_records if record > now - sec
        ]


acc_records: Dict[str, AccRecord] = {}


def check_ip_accessible(ip: str, auto_ban: bool = True) -> bool:
    """检查 IP 是否可访问"""
    if ip not in acc_records:
        acc_records[ip] = AccRecord(ip=ip)

    ip_record = acc_records[ip]
    ip_record.drop_expired_records(300)
    access_rate = ip_record.calc_access_qps(60)

    if auto_ban:
        for i in range(2, 8):
            if access_rate > config.ACCESS_QPM_LIMIT * i:
                ip_record.banned_until = int(time.time() + 60 * i)
                return False

    if acc_records[ip].banned_until > time.time():
        return False

    if access_rate > config.ACCESS_QPM_LIMIT:
        return False

    ip_record.recent_access_records.append(time.time())
    return True
