from datetime import datetime
from app.core.state import last_ingested_at
from app.core.database import SessionLocal
from app.models.schemas import Customer, Product, CustomerProduct
from app.services.embeddings import get_embedding
from app.services.vectordb import collection

def ingest_incremental_data():
    global last_ingested_at

    db = SessionLocal()

    query = (
        db.query(Customer, Product)
        .join(CustomerProduct, Customer.id == CustomerProduct.customer_id)
        .join(Product, Product.id == CustomerProduct.product_id)
    )

    if last_ingested_at:
        query = query.filter(
            Customer.updated_at > last_ingested_at
        )

    rows = query.all()

    for customer, product in rows:
        text = (
            f"Customer {customer.name} purchased product {product.name} "
            f"from category {product.category} priced at {product.price}."
        )

        embedding = get_embedding(text)

        # deterministic ID → prevents duplicates
        doc_id = f"{customer.id}_{product.id}"

        collection.upsert(
            documents=[text],
            embeddings=[embedding],
            ids=[doc_id]
        )

    last_ingested_at = datetime.utcnow()
