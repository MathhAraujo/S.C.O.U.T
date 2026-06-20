from fastapi import APIRouter

from app.api.v1 import athletes, device_assignments, devices, telemetry

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(athletes.router)
api_router.include_router(devices.router)
api_router.include_router(device_assignments.router)
api_router.include_router(telemetry.router)
