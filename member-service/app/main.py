from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database
from .database import engine
from .seed import seed_members

models.Base.metadata.create_all(bind=engine)
# Seed the database
seed_members()

app = FastAPI(
    title="Member Service",
    description="API for managing members",
    version="1.0.0",
    openapi_tags=[{
        "name": "members",
        "description": "Operations with members"
    }]
)

@app.post("/members/", response_model=schemas.Member, tags=["members"])
def create_member(member: schemas.MemberCreate, db: Session = Depends(database.get_db)):
    db_member = models.Member(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@app.get("/members/", response_model=List[schemas.Member], tags=["members"])
def get_members(db: Session = Depends(database.get_db)):
    members = db.query(models.Member)\
        .filter(models.Member.is_deleted == False)\
        .order_by(models.Member.followers.desc())\
        .all()
    return members

@app.delete("/members/", tags=["members"])
def delete_members(db: Session = Depends(database.get_db)):
    db.query(models.Member).update({"is_deleted": True})
    db.commit()
    return {"message": "All members have been soft deleted"} 