from fastapi import FastAPI
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
app = FastAPI()


voyager_state = {
    "electric_power": 10,
    "signal_strength": 71,
    "internal_temperature": 90,
    "mag_status": "ON",
    "pls_status": "OFF",
    "pws_status": "ON",
    "iss_status": "OFF",
    "crs_status": "ON",
    "mode": "NORMAL",
}


@app.get("/")
def read_root():
    logger.info("Voyager service root endpoint requested")

    return {
        "service": "voyager-service",
        "description": "simulates the deep-space probe Voyager",
    }


@app.get("/health")
def health():
    return {
        "status": "online",
    }


@app.get("/telemetry")
def telemetry():
    logger.info("Voyager telemetry requested")
    return voyager_state


@app.post("/commands")
def commands():
    return {}


@app.post("/simulate-anomaly")
def simulate_anomaly():
    return {}
