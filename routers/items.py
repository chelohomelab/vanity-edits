from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy import distinct
from sqlalchemy.orm import Session

import database as models
from dependencies import get_db, save_uploaded_file, delete_uploaded_file
from schemas import ItemPatchPayload

router = APIRouter(prefix="/items", tags=["items"])

AUTOCOMPLETE_FIELDS = {"brand", "name", "shade"}


@router.get("/autocomplete")
def autocomplete(
    field: str,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
) -> List[str]:
    if field not in AUTOCOMPLETE_FIELDS:
        return []
    col = getattr(models.Item, field, None)
    if col is None:
        return []
    q = db.query(distinct(col)).filter(col.isnot(None), col != "", models.Item.is_deleted == False)
    if category:
        q = q.filter(models.Item.category == category)
    return sorted(v for (v,) in q.all() if v)


def _photo_list(item: models.Item) -> list:
    return [{"id": p.id, "path": p.path, "is_primary": p.is_primary, "position": p.position}
            for p in sorted(item.photos, key=lambda p: (not p.is_primary, p.position))]


def _primary_photo(item: models.Item) -> Optional[str]:
    for p in item.photos:
        if p.is_primary:
            return p.path
    return item.photos[0].path if item.photos else None


def _item_dict(i: models.Item) -> dict:
    return {
        "id": i.id,
        "category": i.category,
        "brand": i.brand,
        "name": i.name,
        "status": i.status,
        "quantity": i.quantity,
        "price_paid": i.price_paid,
        "upc": i.upc,
        "notes": i.notes,
        "date_added": i.date_added,
        "is_deleted": i.is_deleted,
        "product_type": i.product_type,
        "shade": i.shade,
        "finish": i.finish,
        "concentration": i.concentration,
        "volume_ml": i.volume_ml,
        "scent_type": i.scent_type,
        "color_family": i.color_family,
        "polish_type": i.polish_type,
        "photos": _photo_list(i),
        "primary_photo": _primary_photo(i),
    }


@router.get("/")
def list_items(
    db: Session = Depends(get_db),
    category: Optional[str] = None,
    status: Optional[str] = None,
):
    q = db.query(models.Item).filter(models.Item.is_deleted == False)
    if category:
        q = q.filter(models.Item.category == category)
    if status:
        q = q.filter(models.Item.status == status)
    return [_item_dict(i) for i in q.order_by(models.Item.brand, models.Item.name).all()]


@router.post("/")
async def add_item(
    request: Request,
    category: str = Form(...),
    brand: str = Form(...),
    name: Optional[str] = Form(default=None),
    status: str = Form(default="new"),
    quantity: Optional[int] = Form(default=1),
    price_paid: Optional[float] = Form(default=None),
    upc: Optional[str] = Form(default=None),
    notes: Optional[str] = Form(default=None),
    product_type: Optional[str] = Form(default=None),
    shade: Optional[str] = Form(default=None),
    finish: Optional[str] = Form(default=None),
    concentration: Optional[str] = Form(default=None),
    volume_ml: Optional[float] = Form(default=None),
    scent_type: Optional[str] = Form(default=None),
    color_family: Optional[str] = Form(default=None),
    polish_type: Optional[str] = Form(default=None),
    image: Optional[UploadFile] = File(default=None),
    db: Session = Depends(get_db),
):
    if category not in ("makeup", "perfume", "nail_polish"):
        raise HTTPException(400, "Invalid category")
    img_path = await save_uploaded_file(image, category)
    item = models.Item(
        category=category,
        brand=brand.strip(),
        name=name.strip() if name else None,
        status=status or "new",
        quantity=quantity or 1,
        price_paid=price_paid,
        upc=upc or None,
        notes=notes or None,
        date_added=datetime.utcnow().strftime("%Y-%m-%d"),
        product_type=product_type or None,
        shade=shade or None,
        finish=finish or None,
        concentration=concentration or None,
        volume_ml=volume_ml,
        scent_type=scent_type or None,
        color_family=color_family or None,
        polish_type=polish_type or None,
    )
    db.add(item)
    db.flush()
    if img_path:
        db.add(models.ItemPhoto(item_id=item.id, path=img_path, position=0, is_primary=True))
    db.commit()
    db.refresh(item)
    return _item_dict(item)


@router.get("/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    i = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not i:
        raise HTTPException(404, "Not found")
    return _item_dict(i)


@router.patch("/{item_id}")
def patch_item(item_id: int, payload: ItemPatchPayload, db: Session = Depends(get_db)):
    i = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not i:
        raise HTTPException(404, "Not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(i, field, value)
    db.commit()
    db.refresh(i)
    return _item_dict(i)


@router.get("/{item_id}/photos/")
def get_photos(item_id: int, db: Session = Depends(get_db)):
    i = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not i:
        raise HTTPException(404, "Not found")
    return _photo_list(i)


@router.post("/{item_id}/photos/")
async def add_photo(
    item_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    i = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not i:
        raise HTTPException(404, "Not found")
    path = await save_uploaded_file(image, i.category)
    if not path:
        raise HTTPException(400, "No image provided")
    max_pos = max((p.position for p in i.photos), default=-1)
    is_first = len(i.photos) == 0
    photo = models.ItemPhoto(item_id=item_id, path=path, position=max_pos + 1, is_primary=is_first)
    db.add(photo)
    db.commit()
    db.refresh(i)
    return _photo_list(i)


@router.delete("/{item_id}/photos/{photo_id}")
def delete_photo(item_id: int, photo_id: int, db: Session = Depends(get_db)):
    photo = db.query(models.ItemPhoto).filter(
        models.ItemPhoto.id == photo_id, models.ItemPhoto.item_id == item_id
    ).first()
    if not photo:
        raise HTTPException(404, "Photo not found")
    was_primary = photo.is_primary
    delete_uploaded_file(photo.path)
    db.delete(photo)
    db.flush()
    if was_primary:
        remaining = db.query(models.ItemPhoto).filter(
            models.ItemPhoto.item_id == item_id
        ).order_by(models.ItemPhoto.position).first()
        if remaining:
            remaining.is_primary = True
    db.commit()
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    return _photo_list(item)


@router.post("/{item_id}/photos/{photo_id}/set-primary/")
def set_primary_photo(item_id: int, photo_id: int, db: Session = Depends(get_db)):
    photos = db.query(models.ItemPhoto).filter(models.ItemPhoto.item_id == item_id).all()
    found = False
    for p in photos:
        if p.id == photo_id:
            p.is_primary = True
            found = True
        else:
            p.is_primary = False
    if not found:
        raise HTTPException(404, "Photo not found")
    db.commit()
    item = db.query(models.Item).filter(models.Item.id == item_id).first()
    return _photo_list(item)


@router.post("/{item_id}/status/")
def set_status(item_id: int, status: str = Form(...), db: Session = Depends(get_db)):
    if status not in ("new", "open", "finished"):
        raise HTTPException(400, "Invalid status")
    i = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not i:
        raise HTTPException(404, "Not found")
    i.status = status
    db.commit()
    return _item_dict(i)


@router.post("/{item_id}/trash/")
def trash_item(item_id: int, request: Request, db: Session = Depends(get_db)):
    if not getattr(request.state, "user", None):
        raise HTTPException(401)
    i = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not i:
        raise HTTPException(404, "Not found")
    i.is_deleted = True
    db.commit()
    return {"ok": True}


@router.post("/{item_id}/restore/")
def restore_item(item_id: int, request: Request, db: Session = Depends(get_db)):
    if not getattr(request.state, "user", None) or not request.state.user.is_admin:
        raise HTTPException(403, "Admin required")
    i = db.query(models.Item).filter(models.Item.id == item_id).first()
    if not i:
        raise HTTPException(404, "Not found")
    i.is_deleted = False
    db.commit()
    return {"ok": True}
