import threading
import time
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import Base, engine, get_db, SessionLocal
from models import Product, Variant
from schemas import VariantListItem, ProductBase, VariantBase
from flashsale_service import FlashSaleService
from shopee_client import ShopeeClient
from notifier import TelegramNotifier
from config import FLASHSALE_JOB_INTERVAL
import crud

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shopee Flash Sale Tracker")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    variants = crud.get_current_flashsale_variants(db)
    result = []
    for v in variants:
        p = v.product
        result.append(
            VariantListItem(
                product=ProductBase(
                    id=p.id,
                    name=p.name,
                    image_url=p.image_url,
                    url=p.url,
                ),
                variant=VariantBase(
                    id=v.id,
                    name=v.name,
                    original_price=v.original_price,
                    flash_price=v.flash_price,
                    discount_percent=v.discount_percent,
                    stock=v.stock,
                    flash_end_time=v.flash_end_time,
                    url=p.url or "",
                ),
            )
        )
    return templates.TemplateResponse(
        "index.html", {"request": request, "variants": result}
    )


def scheduler_loop():
    shopee_client = ShopeeClient()
    notifier = TelegramNotifier()

    while True:
        db = SessionLocal()
        try:
            service = FlashSaleService(
                db=db,
                shopee_client=shopee_client,
                notifier=notifier
            )
            service.update_flashsale_data()
        except Exception as e:
            print("Scheduler error:", e)
        finally:
            db.close()

        time.sleep(FLASHSALE_JOB_INTERVAL)


# Start background scheduler thread
threading.Thread(target=scheduler_loop, daemon=True).start()
