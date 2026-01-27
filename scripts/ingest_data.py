from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.schemas import Customer, Product, CustomerProduct
from app.services.embeddings import get_embedding
from app.services.vectordb import collection

def ingest():
    db: Session = SessionLocal()

    results = (
        db.query(Customer, Product)
        .join(CustomerProduct, Customer.id == CustomerProduct.customer_id)
        .join(Product, Product.id == CustomerProduct.product_id)
        .all()
    )

    for idx, (customer, product) in enumerate(results):
        text = (
            f"Customer {customer.name} with email {customer.email} "
            f"purchased product {product.name} "
            f"from category {product.category} "
            f"priced at {product.price}."
        )

        embedding = get_embedding(text)

        collection.add(
            documents=[text],
            embeddings=[embedding],
            ids=[f"doc_{idx}"]
        )

    print("✅ Data successfully ingested into ChromaDB")

if __name__ == "__main__":
    ingest()
