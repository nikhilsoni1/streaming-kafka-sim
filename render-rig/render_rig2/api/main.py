from fastapi import FastAPI
from render_rig2.api.routes import chart_generator

app = FastAPI(title="Render Rig Service API", version="1.0.0")
app.include_router(chart_generator.router, prefix="/chart_generator", tags=["Chart Generator"])
