from fastapi import FastAPI
from render_rig2.api.routes import chart_generator
from render_rig2.api.routes import chart_generator_v2
from render_rig2.api.routes import task_status
from fastapi.middleware.cors import CORSMiddleware
from render_rig2.api.routes import health


app = FastAPI(title="Render Rig Service API", version="1.0.0")
app.include_router(health.router, prefix="/health", tags=["Health Check"])
app.include_router(chart_generator.router, prefix="/charts", tags=["Chart Generator"])

# v2 endpoints
app.include_router(chart_generator_v2.router, prefix="/v2/charts", tags=["Chart Generator V2"])
app.include_router(task_status.router, prefix="/v2/status", tags=["Task Status"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
