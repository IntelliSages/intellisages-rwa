"""Evidence-gated verification of product deployments.

A deployment is created unverified. Verification is an explicit, administrator
action that must carry source evidence, and every change is kept as an
append-only event so a verification can be audited or revoked without losing
history. The ``is_verified`` flag on the deployment always reflects the latest
event.
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.imports import require_import_admin
from app.schemas import StrictModel

router = APIRouter(prefix="/api/v1/registry/deployments", tags=["deployment verification"])


class VerificationCreate(StrictModel):
    verified: bool = True
    evidence_ref: str = Field(min_length=10, max_length=500)
    verified_by: str = Field(min_length=1, max_length=160)


class VerificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    deployment_id: str
    verified: bool
    evidence_ref: str
    verified_by: str
    created_at: datetime


def _deployment(db: Session, deployment_id: str) -> models.Deployment:
    deployment = db.get(models.Deployment, deployment_id)
    if deployment is None:
        raise HTTPException(status_code=404, detail="Deployment not found.")
    return deployment


@router.post("/{deployment_id}/verification", response_model=VerificationRead, status_code=201,
             dependencies=[Depends(require_import_admin)])
def record_verification(deployment_id: str, payload: VerificationCreate, db: Session = Depends(get_db)):
    deployment = _deployment(db, deployment_id)
    event = models.DeploymentVerificationEvent(
        deployment_id=deployment.id, verified=payload.verified,
        evidence_ref=payload.evidence_ref, verified_by=payload.verified_by)
    deployment.is_verified = payload.verified
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/{deployment_id}/verification-events", response_model=list[VerificationRead])
def list_verification_events(deployment_id: str, db: Session = Depends(get_db)):
    _deployment(db, deployment_id)
    return db.scalars(select(models.DeploymentVerificationEvent).where(
        models.DeploymentVerificationEvent.deployment_id == deployment_id).order_by(
        models.DeploymentVerificationEvent.created_at, models.DeploymentVerificationEvent.id)).all()
