from sqlalchemy import (
    Boolean, Column, Float, ForeignKey, Integer, String, Text, create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, relationship, sessionmaker

DATABASE_URL = "sqlite:///./data/vanity.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)       # makeup, perfume, nail_polish

    # Common fields
    brand = Column(String)
    name = Column(String)
    status = Column(String, default="new")           # new, open, finished
    quantity = Column(Integer, default=1)
    price_paid = Column(Float)
    upc = Column(String)
    image_path_1 = Column(String)
    image_path_2 = Column(String)
    notes = Column(Text)
    date_added = Column(String)
    is_deleted = Column(Boolean, default=False)

    # Makeup fields
    product_type = Column(String)                    # lipstick, foundation, mascara...
    shade = Column(String)                           # color/shade name
    finish = Column(String)                          # matte, glossy, satin, shimmer...

    # Perfume fields
    concentration = Column(String)                   # EDT, EDP, Parfum, Cologne, Body Mist
    volume_ml = Column(Float)                        # also used for nail polish
    scent_type = Column(String)                      # floral, woody, oriental, fresh...

    # Nail polish fields
    color_family = Column(String)                    # red, pink, nude, purple, blue...
    polish_type = Column(String)                     # regular, gel, dip, top coat, base coat


class UpcCache(Base):
    __tablename__ = "upc_cache"

    upc = Column(String, primary_key=True)
    title = Column(String)
    brand = Column(String)
    name = Column(String)
    category = Column(String)
    product_type = Column(String)
    shade = Column(String)
    volume_ml = Column(Float)
    image_path = Column(String)
    updated_at = Column(String)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(String)

    user = relationship("User", back_populates="sessions")


class Setting(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(String)


def _col_exists(db: Session, table: str, column: str) -> bool:
    result = db.execute(__import__("sqlalchemy").text(f"PRAGMA table_info({table})"))
    return any(row[1] == column for row in result)


def init_db():
    Base.metadata.create_all(bind=engine)
