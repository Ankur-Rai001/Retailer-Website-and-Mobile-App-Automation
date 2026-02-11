from fastapi import APIRouter
from typing import List
from models import Template

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=List[Template])
async def get_templates():
    templates = [
        Template(
            template_id="modern_minimal",
            name="Modern Minimal",
            category="general",
            preview_url="https://images.unsplash.com/photo-1441986300917-64674bd600d8",
            description="Clean and minimal design perfect for any store",
            is_premium=False,
            price=0
        ),
        Template(
            template_id="grocery_fresh",
            name="Grocery Fresh",
            category="grocery",
            preview_url="https://images.unsplash.com/photo-1542838132-92c53300491e",
            description="Vibrant template for grocery and food stores",
            is_premium=False,
            price=0
        ),
        Template(
            template_id="fashion_boutique",
            name="Fashion Boutique",
            category="clothing",
            preview_url="https://images.unsplash.com/photo-1441984904996-e0b6ba687e04",
            description="Elegant template for clothing and fashion",
            is_premium=True,
            price=999
        ),
        Template(
            template_id="electronics_pro",
            name="Electronics Pro",
            category="electronics",
            preview_url="https://images.unsplash.com/photo-1498049794561-7780e7231661",
            description="Tech-focused design for electronics stores",
            is_premium=True,
            price=1499
        )
    ]
    return templates
