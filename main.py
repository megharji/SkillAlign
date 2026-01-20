from fastapi import FastAPI
from app.routes.auth_routers import auth_routers
from app.routes.hr_routers import hr_routers
from app.common.config import Base, engine
from app.models import * 

# ✅ Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SkillAlign")

# Include routers for different modules
app.include_router(auth_routers, prefix="/auth_routers", tags=["Auth Routers"])
app.include_router(hr_routers, prefix="/hr_routers", tags=["HR Routers"])



@app.get("/")
def home():
    return {"message": "Hello, World!"}
