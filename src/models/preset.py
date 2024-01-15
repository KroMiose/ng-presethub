from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from src.log import logger
from src.schemas.preset import QueryCondition
from src.utils.db import Base, db, ensure_connection


# 定义 Preset 模型
class DBPreset(Base):
    __tablename__ = "preset"

    id = Column(
        String(64),
        primary_key=True,
        nullable=False,
        comment="Preset Id (由 preset_key 和 self_info 生成 用于标记唯一的预设信息)",
    )
    # 在此添加表结构信息:
    name = Column(String(255), nullable=False, comment="Preset 名称")
    preset_key = Column(String(32), nullable=False, comment="Preset 标识符")
    description = Column(String(255), nullable=False, comment="Preset 描述")
    self_intro = Column(String(8192), nullable=False, comment="Preset 预设信息")
    uploader = Column(String(255), nullable=False, comment="上传者")
    used_count = Column(Integer, default=0, comment="使用次数")
    from_ip = Column(String(32), nullable=False, comment="来自客户端 IP")

    last_update_time = Column(DateTime, default=datetime.now)
    created_time = Column(DateTime, default=datetime.now)

    @classmethod
    def add(cls, data: "DBPreset"):
        """新增 Preset 资源"""

        try:
            ensure_connection()
            data.last_update_time = datetime.now()
            data.created_time = datetime.now()
            db.add(data)
            db.commit()
        except Exception as e:
            db.rollback()
            logger.exception(f"添加预设时出现错误: {e}")
            return False
        else:
            return True

    @classmethod
    def get_by_id(cls, _id: int):
        """根据 id 查询 Preset 资源"""

        ensure_connection()
        return db.query(cls).filter(cls.id == _id).first()

    @classmethod
    def query(cls, condition: QueryCondition):
        """根据条件查询 Preset 资源"""

        ensure_connection()
        page = condition.page if condition.page else 1
        page_size = condition.page_size if condition.page_size else 10
        order_field_name = condition.order_by.field_name
        order_desc = condition.order_by.desc
        keyword = condition.keyword

        query = db.query(cls)

        # for _filter in condition.filters:
        #     field_name = _filter.field_name
        #     value = _filter.value

        #     # TODO 待实现: 检查参数类型，根据不同类型添加不同筛选条件

        if keyword:
            query = db.query(cls).filter(cls.name.like(f"%{keyword}%"))

        if order_field_name:
            query = query.order_by(
                getattr(cls, order_field_name).asc()
                if not order_desc
                else getattr(cls, order_field_name).desc(),
            )

        total = query.count()

        if page and page_size:
            query = query.offset((page - 1) * page_size)
        query = query.limit(page_size)

        return query, total

    @classmethod
    def update(cls, data: "DBPreset", **kwargs):
        """更新 Preset 资源"""

        ensure_connection()
        try:
            if "id" in kwargs:
                del kwargs["id"]
            if "created_time" in kwargs:
                del kwargs["created_time"]
            if "last_update_time" in kwargs:
                del kwargs["last_update_time"]
            data.last_update_time = datetime.now()
            db.query(cls).filter(cls.id == data.id).update(dict(**kwargs))
            db.commit()
        except Exception as e:
            db.rollback()
            logger.exception(f"编辑预设时出现错误: {e}")
        else:
            return True

    @classmethod
    def delete(cls, data: "DBPreset"):
        """删除 Preset 资源"""

        ensure_connection()
        try:
            db.query(cls).filter(cls.id == data.id).delete()
            db.commit()
        except:
            db.rollback()
            return False
        else:
            return True
