# streaming-kafka-sim

**streaming-kafka-sim** is a **work-in-progress** telemetry simulation and analytics platform designed for real-time log ingestion, transformation, and visualization. It simulates Kafka-based telemetry ingestion, applies transformations using dbt, and leverages a distributed chart rendering engine—**`render-rig2`**—to generate compute-heavy visualizations.

---

## 🖼️ `render-rig2`: Chart Rendering Engine

`render-rig2` is the backbone of the visualization pipeline and is designed to render high-cost charts in parallel using a **distributed task queue architecture** powered by **Celery** and **Redis**.

### 🔧 Key Capabilities

- **Parallel Chart Rendering**: Leverages ECS and Celery workers for scalable, distributed processing.
- **Extensible Architecture**: Add new chart types in  
  `render-rig/render_rig2/chart_engine/charts/`
- **API Interface**: Exposes endpoints for on-demand chart rendering.
- **Docker-First Setup**: Spin it up locally using Docker Compose.

### 🧪 Use Case

This engine is built with **PX4 log analysis** in mind—helping drone engineers and developers **quickly visualize metrics** from telemetry logs, such as acceleration profiles, orientation timelines, and sensor readings.

---

## 🔁 Project Modules

```bash
streaming-kafka-sim/
├── render-rig2/              # Chart rendering engine (Celery + Redis + API)
├── dbt_analytics/            # dbt models for transforming telemetry
├── tools/ypr-tools-skyhawk/ # AWS CLI tools (EC2, RDS, EMR, Security)
├── polling/                 # PX4 telemetry poller
├── scripts/                 # Utility scripts for DB setup and environments
├── services/                # Redis, Airflow, etc.
├── scratch-codeartifact.py  # Experimental scripts
├── requirements.txt
