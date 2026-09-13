import os
import httpx
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# 1. Read Database URL from environment variables (injected via compose.yaml)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/service_pulse")

# 2. Database connection setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 3. Database Table Model
class ServiceModel(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    status = Column(String, default="UNKNOWN")

# Ensure table creation on application startup
Base.metadata.create_all(bind=engine)

# Dependency to provide a database session per HTTP request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 4. Request / Response Validation Schemas
class ServiceCreate(BaseModel):
    name: str
    url: str

class ServiceResponse(BaseModel):
    id: int
    name: str
    url: str
    status: str

    class Config:
        from_attributes = True

# 5. FastAPI Application
app = FastAPI(title="ServicePulse API")

@app.get("/health")
def health_check():
    return {"status": "running"}

@app.get("/services", response_model=list[ServiceResponse])
def get_services(db: Session = Depends(get_db)):
    """Retrieve all monitored services from PostgreSQL."""
    return db.query(ServiceModel).all()

@app.post("/services", response_model=ServiceResponse, status_code=201)
def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    """Add a new service to monitor in PostgreSQL."""
    new_service = ServiceModel(name=service.name, url=service.url, status="UNKNOWN")
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

@app.post("/services/{service_id}/check", response_model=ServiceResponse)
def check_service_health(service_id: int, db: Session = Depends(get_db)):
    """Ping a service over HTTP and update its status (UP or DOWN) in PostgreSQL."""
    # 1. Locate the service in the database by ID
    service = db.query(ServiceModel).filter(ServiceModel.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # 2. Perform HTTP GET probe with timeout
    try:
        response = httpx.get(service.url, timeout=5.0)
        # 2xx and 3xx status codes indicate healthy service
        if 200 <= response.status_code < 400:
            service.status = "UP"
        else:
            service.status = "DOWN"
    except Exception:
        # Connection failure, DNS failure, or timeout
        service.status = "DOWN"

    # 3. Persist updated status in database
    db.commit()
    db.refresh(service)
    return service
