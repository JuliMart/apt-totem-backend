from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base

# --- Catálogo ---
class Categoria(Base):
    __tablename__ = "categoria"
    id_categoria = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    productos = relationship("Producto", back_populates="categoria")

class Producto(Base):
    __tablename__ = "producto"
    id_producto = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=False)
    marca = Column(String(60))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    categoria = relationship("Categoria", back_populates="productos")
    variantes = relationship("ProductoVariante", back_populates="producto")

class ProductoVariante(Base):
    __tablename__ = "producto_variante"
    id_variante = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("producto.id_producto"), nullable=False)
    sku = Column(String(40), unique=True, nullable=False)
    talla = Column(String(20))
    color = Column(String(30))
    precio = Column(Float, nullable=False)
    image_url = Column(String(400))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    producto = relationship("Producto", back_populates="variantes")

# --- Interacciones ---
class Sesion(Base):
    __tablename__ = "sesion"
    id_sesion = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    inicio = Column(DateTime, default=datetime.utcnow)
    termino = Column(DateTime, nullable=True)
    canal = Column(String(20))  # voz / vision / mixto

    detecciones = relationship("Deteccion", back_populates="sesion")
    consultas_voz = relationship("ConsultaVoz", back_populates="sesion")

class ConsultaVoz(Base):
    __tablename__ = "consulta_voz"
    id_consulta = Column(Integer, primary_key=True, index=True)
    id_sesion = Column(String(36), ForeignKey("sesion.id_sesion"))
    fecha_hora = Column(DateTime, default=datetime.utcnow)
    transcripcion = Column(Text)
    intencion = Column(String(80))
    entidades = Column(Text)   # JSON serializado
    confianza = Column(String(20))
    exito = Column(Boolean, default=False)

    sesion = relationship("Sesion", back_populates="consultas_voz")

class Deteccion(Base):
    __tablename__ = "deteccion"
    id_deteccion = Column(Integer, primary_key=True, index=True)
    id_sesion = Column(String(36), ForeignKey("sesion.id_sesion"))
    fecha_hora = Column(DateTime, default=datetime.utcnow)
    prenda = Column(String(50))
    color = Column(String(30))
    rango_etario = Column(String(20))
    confianza = Column(Float)

    sesion = relationship("Sesion", back_populates="detecciones")
