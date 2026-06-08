import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ..models.agent_template import AgentTemplate, RoleEnum
from ..schemas.agent_template import AgentTemplateCreate, AgentTemplateUpdate, AgentTemplateRead


def _increment_version(version: str) -> str:
    """Simple version bump: increase patch number.
    Assumes semantic versioning 'major.minor.patch'.
    """
    parts = version.split('.')
    if len(parts) != 3:
        return version
    major, minor, patch = parts
    try:
        patch = str(int(patch) + 1)
    except ValueError:
        return version
    return f"{major}.{minor}.{patch}"


def create_template(db: Session, template_in: AgentTemplateCreate, created_by: str) -> AgentTemplateRead:
    db_obj = AgentTemplate(
        id=uuid.uuid4(),
        created_by=uuid.UUID(created_by),
        name=template_in.name,
        role=RoleEnum(template_in.role),
        description=template_in.description,
        system_prompt=template_in.system_prompt,
        default_objective_template=template_in.default_objective_template,
        default_tools=template_in.default_tools,
        default_resource_budget=template_in.default_resource_budget,
        default_trust_score=template_in.default_trust_score,
        personality_traits=template_in.personality_traits.dict() if template_in.personality_traits else None,
        tags=template_in.tags,
        version="1.0.0",
        is_public=template_in.is_public,
        use_count=0,
        avg_performance_score=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return AgentTemplateRead.from_orm(db_obj)


def get_template(db: Session, template_id: str) -> Optional[AgentTemplateRead]:
    obj = db.query(AgentTemplate).filter(AgentTemplate.id == uuid.UUID(template_id)).first()
    return AgentTemplateRead.from_orm(obj) if obj else None


def list_templates(db: Session, skip: int = 0, limit: int = 100) -> List[AgentTemplateRead]:
    objs = db.query(AgentTemplate).offset(skip).limit(limit).all()
    return [AgentTemplateRead.from_orm(o) for o in objs]


def update_template(db: Session, template_id: str, update: AgentTemplateUpdate) -> Optional[AgentTemplateRead]:
    obj = db.query(AgentTemplate).filter(AgentTemplate.id == uuid.UUID(template_id)).first()
    if not obj:
        return None
    # Create a new version record rather than mutating existing
    new_version = _increment_version(obj.version)
    # Build new object copying old values and applying updates
    new_obj = AgentTemplate(
        id=uuid.uuid4(),
        created_by=obj.created_by,
        name=update.name or obj.name,
        role=obj.role,
        description=update.description if update.description is not None else obj.description,
        system_prompt=update.system_prompt if update.system_prompt is not None else obj.system_prompt,
        default_objective_template=update.default_objective_template if update.default_objective_template is not None else obj.default_objective_template,
        default_tools=update.default_tools if update.default_tools is not None else obj.default_tools,
        default_resource_budget=update.default_resource_budget if update.default_resource_budget is not None else obj.default_resource_budget,
        default_trust_score=update.default_trust_score if update.default_trust_score is not None else obj.default_trust_score,
        personality_traits=update.personality_traits.dict() if update.personality_traits is not None else obj.personality_traits,
        tags=update.tags if update.tags is not None else obj.tags,
        version=new_version,
        is_public=update.is_public if update.is_public is not None else obj.is_public,
        use_count=obj.use_count,
        avg_performance_score=obj.avg_performance_score,
        created_at=obj.created_at,
        updated_at=datetime.utcnow(),
    )
    db.add(new_obj)
    db.commit()
    db.refresh(new_obj)
    return AgentTemplateRead.from_orm(new_obj)


def fork_template(db: Session, template_id: str, new_owner: str) -> Optional[AgentTemplateRead]:
    source = db.query(AgentTemplate).filter(AgentTemplate.id == uuid.UUID(template_id)).first()
    if not source:
        return None
    forked = AgentTemplate(
        id=uuid.uuid4(),
        created_by=uuid.UUID(new_owner),
        name=source.name,
        role=source.role,
        description=source.description,
        system_prompt=source.system_prompt,
        default_objective_template=source.default_objective_template,
        default_tools=source.default_tools,
        default_resource_budget=source.default_resource_budget,
        default_trust_score=source.default_trust_score,
        personality_traits=source.personality_traits,
        tags=source.tags,
        version="1.0.0",
        is_public=source.is_public,
        use_count=0,
        avg_performance_score=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(forked)
    db.commit()
    db.refresh(forked)
    return AgentTemplateRead.from_orm(forked)


def increment_use_count(db: Session, template_id: str) -> None:
    obj = db.query(AgentTemplate).filter(AgentTemplate.id == uuid.UUID(template_id)).first()
    if obj:
        obj.use_count = (obj.use_count or 0) + 1
        db.commit()
