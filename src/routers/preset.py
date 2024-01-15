from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status

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
from src.utils.md5 import md5

ROUTER_TAG = "Preset"

router = APIRouter()


def gen_hashed_id(preset_key, self_intro):
    return md5(f"${preset_key}$*${self_intro}$")[:16]


def get_ip(request: Request):
    if request.client.host == "127.0.0.1":
        from_ip: Optional[str] = request.headers.get("X-Real-IP", "127.0.0.1")
    else:
        from_ip = request.client.host
    # logger.info(f"Request received [{from_ip}]: path {request.url.path}")
    return from_ip


def custom_authorize(request: Request):
    return request.headers.get("Authorization") == md5(config.SUPER_ACCESS_KEY)


@router.post("/create", tags=[ROUTER_TAG], summary="创建")
async def create(data: PresetCreate, request: Request):
    """创建 Preset 资源"""
    try:
        item = DBPreset(**data.model_dump())

        if item.uploader == "KroMiose" and not custom_authorize(request):
            return Ret.fail("不能冒充 KroMiose!")

        preset_id = gen_hashed_id(item.preset_key, item.self_intro)
        if DBPreset.get_by_id(preset_id):
            return Ret.fail("预设已存在")

        item = DBPreset(
            id=preset_id,
            name=item.name,
            preset_key=item.preset_key,
            description=item.description,
            self_intro=item.self_intro,
            uploader=item.uploader,
            from_ip=get_ip(request),
        )

        if DBPreset.add(item):
            logger.info(f"预设 {item.name}[{item.id}] 上传成功 ({item.from_ip})")
            return Ret.success(
                "Create success",
                data={
                    "id": item.id,
                },
            )
        logger.error(f"Create {data} resource failed")
        return Ret.fail("上传预设失败")
    except:
        logger.error(f"Create {data} resource failed")
        return Ret.fail("Create failed")


@router.get("/detail", tags=[ROUTER_TAG], summary="查询详情")
async def get(_id: str, use: str):
    """根据 id 查询 Preset 资源"""

    item = DBPreset.get_by_id(_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if use.lower() == "true":
        DBPreset.update(item, used_count=item.used_count + 1)

    return Ret.success(
        "query success",
        data={
            "id": item.id,
            "name": item.name,
            "preset_key": item.preset_key,
            "description": item.description,
            "self_intro": item.self_intro,
            "uploader": item.uploader,
            "used_count": item.used_count,
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
                "list": [
                    {
                        "id": item.id,
                        "name": item.name,
                        "preset_key": item.preset_key,
                        "description": item.description,
                        "self_intro": item.self_intro,
                        "uploader": item.uploader,
                        "used_count": item.used_count,
                        "created_time": item.created_time,
                        "last_update_time": item.last_update_time,
                    }
                    for item in items
                ],
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
async def delete(_id: str, request: Request):
    """根据 id 删除 Preset 资源"""
    if not custom_authorize(request):
        return Ret.fail("预设中心访问权限受限")

    try:
        item = DBPreset.get_by_id(_id)
        DBPreset.delete(item)
        return Ret.success("Delete success")
    except Exception as e:
        logger.error(f"Delete resource(id: {_id}) failed: {e}")
        return Ret.fail("Delete failed")


logger.success(f"Router {ROUTER_TAG} initialized")
