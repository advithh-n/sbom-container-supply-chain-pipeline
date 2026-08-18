from datetime import UTC, datetime
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field


class GridAsset(BaseModel):
    model_config = ConfigDict(extra="forbid")

    asset_id: str = Field(pattern=r"^[A-Z]{2,5}-[0-9]{3}$")
    asset_type: Literal["solar", "battery", "wind"]
    status: Literal["online", "standby", "maintenance"]
    output_mw: float = Field(ge=0, le=500)


ASSETS = {
    "DER-101": GridAsset(
        asset_id="DER-101", asset_type="solar", status="online", output_mw=82.4
    ),
    "BESS-203": GridAsset(
        asset_id="BESS-203", asset_type="battery", status="standby", output_mw=0
    ),
    "WIND-304": GridAsset(
        asset_id="WIND-304", asset_type="wind", status="online", output_mw=118.6
    ),
}

app = FastAPI(
    title="Grid Asset Status API",
    version="1.0.0",
    description="A minimal service used to demonstrate a secured container supply chain.",
    docs_url=None,
    redoc_url=None,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy", "timestamp": datetime.now(UTC).isoformat()}


@app.get("/api/v1/assets", response_model=list[GridAsset])
def list_assets() -> list[GridAsset]:
    return list(ASSETS.values())


@app.get("/api/v1/assets/{asset_id}", response_model=GridAsset)
def get_asset(asset_id: str) -> GridAsset:
    asset = ASSETS.get(asset_id.upper())
    if asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@app.get("/api/v1/grid/summary")
def grid_summary() -> dict[str, float | int | str]:
    online = [asset for asset in ASSETS.values() if asset.status == "online"]
    return {
        "assets_total": len(ASSETS),
        "assets_online": len(online),
        "generation_mw": round(sum(asset.output_mw for asset in online), 2),
        "timestamp": datetime.now(UTC).isoformat(),
    }

