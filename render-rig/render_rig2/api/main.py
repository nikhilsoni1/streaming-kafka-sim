from fastapi import FastAPI
from render_rig2.api.routes import chart_generator
from render_rig2.api.routes import chart_generator_v2
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Render Rig Service API", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(chart_generator.router, prefix="/charts", tags=["Chart Generator"])

app.include_router(chart_generator_v2.router, prefix="/v2/charts", tags=["Chart Generator V2"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
