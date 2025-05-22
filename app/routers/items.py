"""Items router module."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(
    prefix="/items",
    tags=["items"],
    responses={404: {"description": "Item not found"}},
)

# Sample data
items_db = {
    1: {"name": "Item 1", "description": "This is item 1"},
    2: {"name": "Item 2", "description": "This is item 2"},
}


class Item(BaseModel):
    """Item model."""
    name: str
    description: str = None


@router.get("/")
async def read_items():
    """Get all items."""
    return items_db


@router.get("/{item_id}")
async def read_item(item_id: int):
    """Get a specific item by ID."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


@router.post("/", status_code=201)
async def create_item(item_id: int, item: Item):
    """Create a new item."""
    if item_id in items_db:
        raise HTTPException(status_code=400, detail="Item already exists")
    items_db[item_id] = item.model_dump()
    return items_db[item_id]


@router.put("/{item_id}")
async def update_item(item_id: int, item: Item):
    """Update an existing item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    items_db[item_id] = item.model_dump()
    return items_db[item_id]


@router.delete("/{item_id}")
async def delete_item(item_id: int):
    """Delete an item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    deleted_item = items_db.pop(item_id)
    return {"message": "Item deleted", "item": deleted_item}