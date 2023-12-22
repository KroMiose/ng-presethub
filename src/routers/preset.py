from fastapi import APIRouter, Depends, HTTPException, status

from src.conf import config  # noqa: F401
from src.log import logger
from src.models.preset import DBPreset
from src.models.user import DBUser
from src.schemas.message import Ret
from src.schemas.perm import Role
from src.schemas.preset import (
    PresetCreate,
    PresetQuery,
    PresetUpdate,
)
from src.utils.deps import get_current_active_user

ROUTER_TAG = "Preset"

router = APIRouter()


@router.post("/create", tags=[ROUTER_TAG], summary="创建")
async def create(data: PresetCreate):
    """创建 Preset 资源"""
    try:
        item = DBPreset(**data.model_dump())
        DBPreset.add(item)
        return Ret.success(
            "Create success",
            data={
                "id": item.id,
                "name": item.name,
                "last_update_time": item.last_update_time,
                "created_time": item.created_time,
            },
        )
    except:
        logger.error(f"Create {data} resource failed")
        return Ret.fail("Create failed")


@router.get("/detail", tags=[ROUTER_TAG], summary="查询详情")
async def get(_id):
    """根据 id 查询 Preset 资源"""

    item = DBPreset.get_by_id(_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return Ret.success(
        "query success",
        data={
            "id": item.id,
            "name": item.name,
            "last_update_time": item.last_update_time,
            "created_time": item.created_time,
        },
    )


@router.post("/list", tags=[ROUTER_TAG], summary="检索分页")
async def query(data: PresetQuery):
    """根据条件检索 Preset 资源"""

    try:
        # TODO DBPreset.query 方法默认提供了分页、排序、关键字过滤，如果需要其他条件需自行实现
        try:
            items, total = DBPreset.query(data.condition)
        except Exception as e:
            logger.error(f"Query {data} resource failed: {e}")
            return Ret.fail("Query failed, please check your parameter and try again")

        return Ret.success(
            "query success",
            data={
                "list":[{
                    "id": item.id,
                    "name": item.name,
                    "created_time": item.created_time,
                    "last_update_time": item.last_update_time,
                } for item in items],
                "total": total,
            },
        )
    except Exception as e:
        logger.error(f"Query {data} resource failed: {e}")
        return Ret.fail("Query failed")


@router.put("/update", tags=[ROUTER_TAG], summary="更新数据")
async def update(data: PresetUpdate):
    """根据 id 更新 Example 资源"""
    item = DBPreset.get_by_id(data.id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    try:
        update_data = data.model_dump()
        # ... deal with update

        DBPreset.update(item, **update_data)
        return Ret.success("Update success", data={"id": item.id, "name": item.name})
    except Exception as e:
        logger.error(f"Update {data} resource failed: {e}")
        return Ret.fail("Update failed")


@router.delete("/delete", tags=[ROUTER_TAG], summary="删除数据")
async def delete(_id: int, current_user: DBUser = Depends(get_current_active_user)):
    """根据 id 删除 Preset 资源"""
    if current_user.perm_level < Role.Admin: # type: ignore
        return Ret.fail("Permission denied")
    try:
        item = DBPreset.get_by_id(_id)
        DBPreset.delete(item)
        return Ret.success("Delete success")
    except Exception as e:
        logger.error(f"Delete resource(id: {_id}) failed: {e}")
        return Ret.fail("Delete failed")


logger.success(f"Router {ROUTER_TAG} initialized")
