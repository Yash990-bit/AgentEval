from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ...db.session import get_db
from ...models.agent_template import AgentTemplate, RoleEnum
from ...schemas.agent_template import AgentTemplateCreate, AgentTemplateUpdate, AgentTemplateRead
from ...services.agent_template_service import (
    create_template,
    get_template,
    list_templates,
    update_template,
    fork_template,
    increment_use_count,
)

router = APIRouter(prefix="/templates", tags=["agent templates"])

@router.get("/", response_model=List[AgentTemplateRead])
def read_templates(
    search: Optional[str] = None,
    role: Optional[RoleEnum] = None,
    sort: str = "popular",
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    # Simple filtering – expand as needed
    templates = list_templates(db, skip=skip, limit=limit)
    if search:
        templates = [t for t in templates if search.lower() in t.name.lower()]
    if role:
        templates = [t for t in templates if t.role == role]
    if sort == "popular":
        templates.sort(key=lambda t: t.use_count or 0, reverse=True)
    elif sort == "newest":
        templates.sort(key=lambda t: t.created_at, reverse=True)
    elif sort == "performance":
        templates.sort(key=lambda t: t.avg_performance_score or 0, reverse=True)
    return templates

@router.post("/", response_model=AgentTemplateRead)
def create_new_template(template: AgentTemplateCreate, db: Session = Depends(get_db)):
    # In a real app, retrieve current user id via auth dependency
    created_by = "00000000-0000-0000-0000-000000000000"
    return create_template(db, template, created_by)

@router.get("/{template_id}", response_model=AgentTemplateRead)
def read_template(template_id: str, db: Session = Depends(get_db)):
    tmpl = get_template(db, template_id)
    if not tmpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return tmpl

@router.put("/{template_id}", response_model=AgentTemplateRead)
def update_existing_template(template_id: str, update: AgentTemplateUpdate, db: Session = Depends(get_db)):
    updated = update_template(db, template_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Template not found")
    return updated

@router.post("/{template_id}/fork", response_model=AgentTemplateRead)
def fork_existing_template(template_id: str, db: Session = Depends(get_db)):
    # In a real app, retrieve current user id via auth dependency
    new_owner = "00000000-0000-0000-0000-000000000000"
    forked = fork_template(db, template_id, new_owner)
    if not forked:
        raise HTTPException(status_code=404, detail="Template not found")
    return forked

@router.post("/{template_id}/use")
def increment_usage(template_id: str, db: Session = Depends(get_db)):
    increment_use_count(db, template_id)
    return {"status": "usage incremented"}
