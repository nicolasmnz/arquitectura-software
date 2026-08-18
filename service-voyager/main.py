from fastapi import FastAPI, HTTPException
import logging
from enum import Enum
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
app = FastAPI()


class CommandType(str, Enum):
    ADJUST_POWER = "adjust_power"
    ENTER_SAFE_MODE = "enter_safe_mode"
    REALIGN_ANTENNA = "realign_antenna"
    RESET_INSTRUMENT = "reset_instrument"


class Command(BaseModel):
    command: CommandType
    value: int | str | None = None


class Anomaly(BaseModel):
    electric_power: int | None = None
    signal_strength: int | None = None
    internal_temperature: int | None = None


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

    if voyager_state["internal_temperature"] > 100:
        logger.warning(
            "High internal temperature detected: %s",
            voyager_state["internal_temperature"],
        )

    if voyager_state["signal_strength"] < 30:
        logger.warning(
            "Low signal strength detected: %s",
            voyager_state["signal_strength"],
        )

    if voyager_state["electric_power"] < 5:
        logger.warning(
            "Low electric power detected: %s",
            voyager_state["electric_power"],
        )

    return voyager_state


@app.post("/commands")
def commands(command: Command):
    logger.info("Command received: %s", command.command.value)
    if command.command == CommandType.ADJUST_POWER:
        if command.value is None:
            logger.error("adjust_power command received without a value")

            raise HTTPException(
                status_code=400,
                detail="adjust_power requires a value",
            )

        voyager_state["electric_power"] = command.value

        logger.info(
            "Electric power adjusted to %s",
            command.value,
        )

    elif command.command == CommandType.ENTER_SAFE_MODE:
        voyager_state["mode"] = "SAFE_MODE"

        logger.warning("Voyager entered SAFE_MODE")

    elif command.command == CommandType.REALIGN_ANTENNA:
        voyager_state["signal_strength"] = 100

        logger.info("Antenna realigned successfully")

    elif command.command == CommandType.RESET_INSTRUMENT:
        if command.value is None:
            raise HTTPException(
                status_code=400,
                detail="reset_instrument requires an instrument name",
            )

        instrument = str(command.value).lower()
        status_key = f"{instrument}_status"

        if status_key not in voyager_state:
            logger.error("Unknown instrument: %s", instrument)

            raise HTTPException(
                status_code=404,
                detail=f"Unknown instrument: {instrument}",
            )

        voyager_state[status_key] = "ON"

        logger.info(
            "Instrument %s reset successfully",
            instrument.upper(),
        )

    return {
        "status": "command executed",
        "command": command.command,
        "voyager_state": voyager_state,
    }
    return {}


@app.post("/simulate-anomaly")
def simulate_anomaly(anomaly: Anomaly):
    logger.warning("Simulating Voyager anomaly")

    if anomaly.electric_power is not None:
        voyager_state["electric_power"] = anomaly.electric_power

        logger.warning(
            "Electric power changed to %s",
            anomaly.electric_power,
        )

    if anomaly.signal_strength is not None:
        voyager_state["signal_strength"] = anomaly.signal_strength

        logger.warning(
            "Signal strength changed to %s",
            anomaly.signal_strength,
        )

    if anomaly.internal_temperature is not None:
        voyager_state["internal_temperature"] = anomaly.internal_temperature

        logger.warning(
            "Internal temperature changed to %s",
            anomaly.internal_temperature,
        )

    return {
        "status": "anomaly simulated",
        "voyager_state": voyager_state,
    }
