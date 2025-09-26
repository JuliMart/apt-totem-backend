from pydantic import BaseModel
from typing import Optional, Dict, Tuple

class OrmBase(BaseModel):
    class Config:
        from_attributes = True  # reemplaza orm_mode en Pydantic v2

# ---- Producto ----
class ProductoBase(BaseModel):
    nombre: str
    id_categoria: int
    marca: Optional[str] = None

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase, OrmBase):
    id_producto: int

# ---- Categoria ----
class CategoriaBase(BaseModel):
    nombre: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase, OrmBase):
    id_categoria: int

# ---- Respuesta de ASR ----
class ASRResponse(BaseModel):
    text: str
    duration: float
    intent: Optional[str] = None
    slots: Optional[Dict[str, str]] = None

    class Config:
        from_attributes = True

# ---- Respuesta de Color ----
class ColorResponse(BaseModel):
    color_name: str
    rgb: Tuple[int, int, int]
    hex: str

    class Config:
        from_attributes = True
