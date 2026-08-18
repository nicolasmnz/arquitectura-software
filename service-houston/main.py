from fastapi import FastAPI, HTTPException
import httpx
import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

app = FastAPI()


VOYAGER_SERVICE_URL = "http://voyager-service:8000"


def send_command(command: dict):
    logger.info("Sending command to Voyager: %s", command["command"])

    try:
        response = httpx.post(f"{VOYAGER_SERVICE_URL}/commands", json=command)

        response.raise_for_status()

    except httpx.HTTPError as error:
        logger.error("Failed to send command to Voyager: %s", error)

        raise HTTPException(status_code=503, detail="Could not send command to Voyager")

    logger.info("Command executed successfully: %s", command["command"])

    return response.json()


@app.get("/")
def read_root():
    logger.info("Mission Control root endpoint requested")

    return {
        "service": "mission-control-service",
        "description": "Monitors and controls the Voyager probe",
    }


@app.get("/health")
def health():
    return {
        "status": "online",
    }


@app.get("/monitor")
def monitor():
    logger.info("Starting Voyager monitoring")

    try:
        response = httpx.get(f"{VOYAGER_SERVICE_URL}/telemetry")

        response.raise_for_status()

    except httpx.HTTPError as error:
        logger.error("Could not communicate with Voyager service: %s", error)

        raise HTTPException(status_code=503, detail="Voyager service unavailable")

    telemetry = response.json()

    alerts = []

    if telemetry["internal_temperature"] > 100:
        logger.warning(
            "High Voyager internal temperature detected: %s",
            telemetry["internal_temperature"],
        )

        alerts.append("HIGH_TEMPERATURE")

    if telemetry["signal_strength"] < 30:
        logger.warning(
            "Low Voyager signal strength detected: %s", telemetry["signal_strength"]
        )

        alerts.append("LOW_SIGNAL")

    if telemetry["electric_power"] < 5:
        logger.warning(
            "Low Voyager electric power detected: %s", telemetry["electric_power"]
        )

        alerts.append("LOW_POWER")

    if len(alerts) == 0:
        logger.info("Voyager operating normally")

    return {
        "telemetry": telemetry,
        "alerts": alerts,
    }


@app.post("/monitor-and-correct")
def monitor_and_correct():
    logger.info("Starting Voyager monitoring and correction cycle")

    try:
        response = httpx.get(f"{VOYAGER_SERVICE_URL}/telemetry")

        response.raise_for_status()

    except httpx.HTTPError as error:
        logger.error("Could not communicate with Voyager service: %s", error)

        raise HTTPException(status_code=503, detail="Voyager service unavailable")

    telemetry = response.json()

    actions = []

    if telemetry["signal_strength"] < 30:
        logger.warning("Low signal strength detected: %s", telemetry["signal_strength"])

        send_command({"command": "realign_antenna"})

        actions.append("realign_antenna")

    if telemetry["electric_power"] < 5:
        logger.warning("Low electric power detected: %s", telemetry["electric_power"])

        send_command({"command": "adjust_power", "value": 10})

        actions.append("adjust_power")

    if telemetry["internal_temperature"] > 100:
        logger.warning(
            "High internal temperature detected: %s", telemetry["internal_temperature"]
        )

        send_command({"command": "enter_safe_mode"})

        actions.append("enter_safe_mode")

    if len(actions) == 0:
        logger.info("No corrective actions required")

    return {
        "status": "monitoring cycle completed",
        "actions": actions,
    }
