from typing import Optional
from pydantic import BaseModel


class ItemPatchPayload(BaseModel):
    brand: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    quantity: Optional[int] = None
    price_paid: Optional[float] = None
    upc: Optional[str] = None
    notes: Optional[str] = None
    product_type: Optional[str] = None
    shade: Optional[str] = None
    finish: Optional[str] = None
    concentration: Optional[str] = None
    volume_ml: Optional[float] = None
    scent_type: Optional[str] = None
    color_family: Optional[str] = None
    polish_type: Optional[str] = None


class AdminUserPatch(BaseModel):
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None


class SettingsPatch(BaseModel):
    value: str
