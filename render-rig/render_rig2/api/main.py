from fastapi import FastAPI
from render_rig2.api.routes import chart_generator
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Render Rig Service API", version="1.0.0")

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(
    chart_generator.router, prefix="/charts", tags=["Chart Generator"]
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
