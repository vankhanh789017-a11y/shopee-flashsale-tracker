from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Float,
    Text,
)
from sqlalchemy.orm import relationship

from database import Base


class Product(Base):
    __tablename__ = "products"

    # item id trên Shopee
    id = Column(Integer, primary_key=True, index=True)
    # shop id
    shop_id = Column(Integer, index=True)

    name = Column(String, index=True)
    image_url = Column(Text, nullable=True)
    url = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Quan hệ 1-nhiều: 1 Product có nhiều Variant
    variants = relationship(
        "Variant",
        back_populates="product",
        cascade="all, delete-orphan",
    )


class Variant(Base):
    __tablename__ = "variants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)

    name = Column(String, index=True)

    original_price = Column(Float)
    flash_price = Column(Float)
    discount_percent = Column(Float)

    stock = Column(Integer)
    flash_sale_stock = Column(Integer, nullable=True)

    flash_start_time = Column(Integer, nullable=True)
    flash_end_time = Column(Integer, nullable=True)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Quan hệ ngược lại: nhiều Variant thuộc về 1 Product
    product = relationship("Product", back_populates="variants")
