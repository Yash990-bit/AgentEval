from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import time
import random
from ...db.session import get_db
from ...db.models import ApiKeyModel, MemberModel

router = APIRouter(prefix="/settings", tags=["settings"])

class ApiKeyRead(BaseModel):
    id: str
    name: str
    scopes: str
    created: str
    lastUsed: str
    requests: str
    status: str
    value: str

    class Config:
        from_attributes = True

class ApiKeyCreate(BaseModel):
    id: Optional[str] = None
    name: str
    scopes: Optional[str] = "read/write"
    created: Optional[str] = None
    last_used: Optional[str] = "Never"
    requests: Optional[str] = "0"
    status: Optional[str] = "active"
    value: Optional[str] = None

class MemberRead(BaseModel):
    id: str
    name: str
    role: str
    lastActive: str

    class Config:
        from_attributes = True

class MemberCreate(BaseModel):
    id: Optional[str] = None
    name: str
    role: str
    last_active: Optional[str] = "Invited"

@router.get("/keys", response_model=List[ApiKeyRead])
def get_keys(db: Session = Depends(get_db)):
    keys = db.query(ApiKeyModel).all()
    if not keys:
        # Seed initial default keys
        default_keys = [
            ApiKeyModel(id="key-1", name="Gemini Production Key", scopes="read/write", created="2026-05-10", last_used="3m ago", requests="1.2M", status="active", value="sk_live_gemini7482hsa0"),
            ApiKeyModel(id="key-2", name="OpenAI Observability ReadOnly", scopes="read-only", created="2026-05-12", last_used="1h ago", requests="430k", status="active", value="sk_live_openaiajs8291n"),
            ApiKeyModel(id="key-3", name="Legacy Test Token", scopes="admin", created="2026-04-01", last_used="12d ago", requests="12k", status="revoked", value="sk_test_legacytoken839")
        ]
        for dk in default_keys:
            db.add(dk)
        db.commit()
        keys = db.query(ApiKeyModel).all()

    # Map database underscore attributes to camelCase for the frontend
    return [
        ApiKeyRead(
            id=k.id,
            name=k.name,
            scopes=k.scopes,
            created=k.created,
            lastUsed=k.last_used,
            requests=k.requests,
            status=k.status,
            value=k.value
        )
        for k in keys
    ]

@router.post("/keys", response_model=ApiKeyRead)
def create_key(req: ApiKeyCreate, db: Session = Depends(get_db)):
    key_id = req.id or f"key-{int(time.time())}"
    generated_val = req.value or f"sk_live_{random.randint(10000000, 99999999)}"
    new_key = ApiKeyModel(
        id=key_id,
        name=req.name,
        scopes=req.scopes or "read/write",
        created=req.created or time.strftime("%Y-%m-%d"),
        last_used=req.last_used or "Never",
        requests=req.requests or "0",
        status=req.status or "active",
        value=generated_val
    )
    db.add(new_key)
    db.commit()
    return ApiKeyRead(
        id=new_key.id,
        name=new_key.name,
        scopes=new_key.scopes,
        created=new_key.created,
        lastUsed=new_key.last_used,
        requests=new_key.requests,
        status=new_key.status,
        value=new_key.value
    )

@router.put("/keys/{key_id}/revoke", response_model=ApiKeyRead)
def revoke_key(key_id: str, db: Session = Depends(get_db)):
    key = db.query(ApiKeyModel).filter(ApiKeyModel.id == key_id).first()
    if not key:
        raise HTTPException(status_code=404, detail="Key not found")
    key.status = "revoked"
    db.commit()
    return ApiKeyRead(
        id=key.id,
        name=key.name,
        scopes=key.scopes,
        created=key.created,
        lastUsed=key.last_used,
        requests=key.requests,
        status=key.status,
        value=key.value
    )

@router.get("/members", response_model=List[MemberRead])
def get_members(db: Session = Depends(get_db)):
    members = db.query(MemberModel).all()
    if not members:
        # Seed initial default member
        dm = MemberModel(id="m-1", name="Yash Raghubanshi (You)", role="Owner", last_active="Active Now")
        db.add(dm)
        db.commit()
        members = db.query(MemberModel).all()

    return [
        MemberRead(
            id=m.id,
            name=m.name,
            role=m.role,
            lastActive=m.last_active
        )
        for m in members
    ]

@router.post("/members", response_model=MemberRead)
def create_member(req: MemberCreate, db: Session = Depends(get_db)):
    new_member = MemberModel(
        id=req.id or f"member-{int(time.time())}",
        name=req.name,
        role=req.role,
        last_active=req.last_active or "Invited"
    )
    db.add(new_member)
    db.commit()
    return MemberRead(
        id=new_member.id,
        name=new_member.name,
        role=new_member.role,
        lastActive=new_member.last_active
    )
