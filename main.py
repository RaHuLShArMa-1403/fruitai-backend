from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI()

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy model for FAQ
class FAQModel(Base):
    __tablename__ = "faqs"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True)
    answer = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic model for FAQ
class FAQ(BaseModel):
    id: int
    question: str
    answer: str

    class Config:
        orm_mode = True

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CRUD operations

@app.get("/")
def read_root():
    return {"message": "Welcome to Fruit.ai API"}



@app.get("/faqs", response_model=List[FAQ])
def get_faqs(db: Session = Depends(get_db)):
    return db.query(FAQModel).all()

@app.get("/faqs/{id}", response_model=FAQ)
def get_faq(id: int, db: Session = Depends(get_db)):
    faq = db.query(FAQModel).filter(FAQModel.id == id).first()
    if faq is None:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq

@app.post("/faqs", response_model=FAQ)
def create_faq(faq: FAQ, db: Session = Depends(get_db)):
    db_faq = FAQModel(id=faq.id, question=faq.question, answer=faq.answer)
    db.add(db_faq)
    db.commit()
    db.refresh(db_faq)
    return db_faq

@app.put("/faqs/{id}", response_model=FAQ)
def update_faq(id: int, faq: FAQ, db: Session = Depends(get_db)):
    db_faq = db.query(FAQModel).filter(FAQModel.id == id).first()
    if db_faq is None:
        raise HTTPException(status_code=404, detail="FAQ not found")
    db_faq.question = faq.question
    db_faq.answer = faq.answer
    db.commit()
    db.refresh(db_faq)
    return db_faq

@app.delete("/faqs/{id}", response_model=dict)
def delete_faq(id: int, db: Session = Depends(get_db)):
    db_faq = db.query(FAQModel).filter(FAQModel.id == id).first()
    if db_faq is None:
        raise HTTPException(status_code=404, detail="FAQ not found")
    db.delete(db_faq)
    db.commit()
    return {"message": "FAQ deleted successfully"}
