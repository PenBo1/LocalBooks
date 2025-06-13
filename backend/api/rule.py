from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends
from typing import Optional, List, Dict, Any
from loguru import logger

from database import crud
from database.models import RuleCreate, Rule, PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse)
async def get_rules(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页数量"),
    sort_by: str = Query("updated_at", description="排序字段，支持updated_at(更新时间)、created_at(创建时间)和name(名称)")
):
    """获取规则列表"""
    try:
        rules, total = await crud.get_rules(page, page_size, sort_by)
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": rules
        }
    except Exception as e:
        logger.error(f"获取规则列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取规则列表失败")


@router.get("/{rule_id}", response_model=Rule)
async def get_rule(rule_id: int = Path(..., description="规则ID")):
    """获取规则详情"""
    try:
        rule = await crud.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")
        return rule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取规则详情失败: {e}")
        raise HTTPException(status_code=500, detail="获取规则详情失败")


@router.post("/", status_code=201, response_model=Dict[str, Any])
async def create_rule(rule: RuleCreate):
    """创建规则"""
    try:
        rule_id = await crud.create_rule(rule)
        return {"id": rule_id, "message": "规则创建成功"}
    except Exception as e:
        logger.error(f"创建规则失败: {e}")
        raise HTTPException(status_code=500, detail="创建规则失败")


@router.put("/{rule_id}", response_model=Dict[str, str])
async def update_rule(
    rule_data: Dict[str, Any],
    rule_id: int = Path(..., description="规则ID")
):
    """更新规则"""
    try:
        # 验证规则是否存在
        rule = await crud.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")
        
        # 更新规则
        success = await crud.update_rule(rule_id, rule_data)
        if not success:
            raise HTTPException(status_code=400, detail="更新规则失败")
        
        return {"message": "规则更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新规则失败: {e}")
        raise HTTPException(status_code=500, detail="更新规则失败")


@router.delete("/{rule_id}", response_model=Dict[str, str])
async def delete_rule(rule_id: int = Path(..., description="规则ID")):
    """删除规则"""
    try:
        # 验证规则是否存在
        rule = await crud.get_rule(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")
        
        # 删除规则
        success = await crud.delete_rule(rule_id)
        if not success:
            raise HTTPException(status_code=400, detail="删除规则失败")
        
        return {"message": "规则删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除规则失败: {e}")
        raise HTTPException(status_code=500, detail="删除规则失败")