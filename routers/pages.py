from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

import database as models
from config import templates
from dependencies import get_db

router = APIRouter()

MAKEUP_TYPES = [
    "Lipstick", "Lip Gloss", "Lip Liner", "Foundation", "Concealer",
    "Powder", "Blush", "Bronzer", "Highlighter", "Contour",
    "Eyeshadow", "Eyeliner", "Mascara", "Brow", "Primer",
    "Setting Spray", "Setting Powder", "Other",
]

MAKEUP_FINISHES = [
    "Matte", "Satin", "Glossy", "Shimmer", "Metallic", "Cream",
    "Dewy", "Velvet", "Sheer",
]

PERFUME_CONCENTRATIONS = [
    "Eau de Parfum (EDP)", "Eau de Toilette (EDT)", "Parfum",
    "Eau de Cologne", "Body Mist", "Hair Mist",
]

SCENT_TYPES = [
    "Floral", "Woody", "Oriental", "Fresh", "Citrus",
    "Fruity", "Gourmand", "Aquatic", "Musky", "Powdery",
]

POLISH_TYPES = [
    "Regular", "Gel", "Dip Powder", "Press-On",
    "Top Coat", "Base Coat", "Nail Treatment",
]

POLISH_FINISHES = [
    "Cream", "Shimmer", "Glitter", "Matte", "Jelly",
    "Metallic", "Holographic", "Duochrome", "Sheer",
]

COLOR_FAMILIES = [
    "Red", "Pink", "Nude", "Coral", "Orange", "Berry",
    "Purple", "Blue", "Green", "Yellow", "Brown", "Black",
    "White", "Silver", "Gold", "Multi", "Clear",
]


def _category_counts(db: Session) -> dict:
    base = db.query(models.Item).filter(models.Item.is_deleted == False)
    return {
        "makeup": base.filter(models.Item.category == "makeup").count(),
        "perfume": base.filter(models.Item.category == "perfume").count(),
        "nail_polish": base.filter(models.Item.category == "nail_polish").count(),
    }


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    counts = _category_counts(db)
    total = sum(counts.values())
    recent = (
        db.query(models.Item)
        .filter(models.Item.is_deleted == False)
        .order_by(models.Item.id.desc())
        .limit(6)
        .all()
    )
    return templates.TemplateResponse(request, "index.html", {
        "user": request.state.user,
        "counts": counts,
        "total": total,
        "recent": recent,
    })


@router.get("/collection/{category}", response_class=HTMLResponse)
async def inventory_page(category: str, request: Request, db: Session = Depends(get_db)):
    if category not in ("makeup", "perfume", "nail_polish"):
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/", status_code=302)
    items = (
        db.query(models.Item)
        .filter(models.Item.is_deleted == False, models.Item.category == category)
        .order_by(models.Item.brand, models.Item.name)
        .all()
    )
    ctx = {
        "user": request.state.user,
        "items": items,
        "category": category,
        "makeup_types": MAKEUP_TYPES,
        "makeup_finishes": MAKEUP_FINISHES,
        "perfume_concentrations": PERFUME_CONCENTRATIONS,
        "scent_types": SCENT_TYPES,
        "polish_types": POLISH_TYPES,
        "polish_finishes": POLISH_FINISHES,
        "color_families": COLOR_FAMILIES,
    }
    return templates.TemplateResponse(request, "inventory.html", ctx)


@router.get("/item/{item_id}", response_class=HTMLResponse)
async def item_detail_page(item_id: int, request: Request, db: Session = Depends(get_db)):
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not item:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse(request, "item_detail.html", {
        "user": request.state.user,
        "item": item,
        "makeup_types": MAKEUP_TYPES,
        "makeup_finishes": MAKEUP_FINISHES,
        "perfume_concentrations": PERFUME_CONCENTRATIONS,
        "scent_types": SCENT_TYPES,
        "polish_types": POLISH_TYPES,
        "polish_finishes": POLISH_FINISHES,
        "color_families": COLOR_FAMILIES,
    })


@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(request: Request, db: Session = Depends(get_db)):
    if not getattr(request.state, "user", None) or not request.state.user.is_admin:
        from fastapi import HTTPException
        raise HTTPException(403, "Admin required")
    users = db.query(models.User).order_by(models.User.id).all()
    return templates.TemplateResponse(request, "admin_users.html", {
        "user": request.state.user,
        "users": users,
    })


@router.get("/admin/trash", response_class=HTMLResponse)
async def trash_page(request: Request, db: Session = Depends(get_db)):
    if not getattr(request.state, "user", None) or not request.state.user.is_admin:
        from fastapi import HTTPException
        raise HTTPException(403, "Admin required")
    return templates.TemplateResponse(request, "admin_trash.html", {
        "user": request.state.user,
    })
