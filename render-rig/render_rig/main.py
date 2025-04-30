# main.py

from fastapi import FastAPI, HTTPException
from render_rig.chart_engine.manager import generate_charts_for_log
from render_rig.cache.store import get_chart_json

app = FastAPI()


@app.get("/charts/{log_id}")
def generate_charts(log_id: str):
    return generate_charts_for_log(log_id)


@app.get("/chart/{chart_id}/json")
def serve_chart_json(chart_id: str):
    try:
        return get_chart_json(chart_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Chart not found")
