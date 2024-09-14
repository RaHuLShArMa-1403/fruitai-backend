from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# FastAPI app setup
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# SQLAlchemy model for FAQ
class FAQModel(Base):
    __tablename__ = "faqs"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True)
    answer = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class FAQ(BaseModel):
    id: int
    question: str
    answer: str

    class Config:
        orm_mode = True

class User(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions for JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    return token_data

# Fake user database (for demonstration purposes)
fake_users_db = {
    "test@example.com": {
        "email": "test@example.com",
        "hashed_password": get_password_hash("password123"),
    }
}

# Auth endpoints
@app.post("/login", response_model=Token)
async def login(form_data: User):
    user = fake_users_db.get(form_data.email)
    if user is None or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

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
    db_faq = FAQModel(question=faq.question, answer=faq.answer)
    db.add(db_faq)
    db.commit()
    db.refresh(db_faq)
    return db_faq

@app.put("/faqs/{id}", response_model=FAQ)
def update_faq(id: int, faq: FAQ, db: Session = Depends(get_db)):
    db_faq = db.query(FAQModel).filter(FAQModel.id == id).first()
    if db_faq is None:
        raise HTTPException(status_code=404, detail="FAQ not found")
    if faq.question:
        db_faq.question = faq.question
    if faq.answer:
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
