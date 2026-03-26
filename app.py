# importing necessary modules
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
import uuid

# MySQL and Database modules
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base

# ----------------- DATABASE SETUP ----------------- #
# Replace with your actual MySQL username, password, localhost/ip, and database name
# format: "mysql+pymysql://<user>:<password>@<host>:<port>/<database_name>"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Mallarapu#28@@localhost:3306/fastapi_db"

# Create Database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get the Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Define the Database Table Structure (SQLAlchemy Model)
class DBItem(Base):
    __tablename__ = "items"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(String(255), nullable=True)

# Create the tables in MySQL automatically if they do not exist
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print("Warning: Could not connect to mysql database immediately. Please ensure mysql server is running and credentials match SQLALCHEMY_DATABASE_URL.")

# --------------------------------------------------- #

# create FastAPI instance
app = FastAPI()

# create data models (Pydantic Models)
class ItemCreate(BaseModel):
    name: str
    description: str | None = None

class Item(BaseModel):
    id: str
    name: str
    description: str | None = None
    
# define crud endpoints

# create - Post
@app.post("/items/")
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    item_id = str(uuid.uuid4())
    # Create new item for the Database
    new_item = DBItem(id=item_id, name=item.name, description=item.description)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    # Return as our Pydantic Item shape
    return {"message": "Item Created", "item": Item(id=new_item.id, name=new_item.name, description=new_item.description)}

# read - GET all items
@app.get("/items/")
def read_items(db: Session = Depends(get_db)):
    # Query all items from the database
    items = db.query(DBItem).all()
    # Convert DB items into a list of Pydantic Items
    result = [Item(id=i.id, name=i.name, description=i.description) for i in items]
    return {"items": result}

# read - GET one item
@app.get("/items/{item_id}")
def read_item(item_id: str, db: Session = Depends(get_db)):
    # Query database for one item matching the exact ID
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="item not found")
    
    return {"item": Item(id=db_item.id, name=db_item.name, description=db_item.description)}

# update - PUT
@app.put("/items/{item_id}")
def update_item(item_id: str, item: Item, db: Session = Depends(get_db)):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="item not found")
    
    # Update the item in the database
    db_item.name = item.name
    db_item.description = item.description
    db.commit()
    db.refresh(db_item)
    
    return {"message": "item updated", "item": Item(id=db_item.id, name=db_item.name, description=db_item.description)}

# delete - DELETE
@app.delete("/items/{item_id}")
def delete_item(item_id: str, db: Session = Depends(get_db)):
    db_item = db.query(DBItem).filter(DBItem.id == item_id).first()
    if db_item is None:
         raise HTTPException(status_code=404, detail="item not found")
         
    # Remove from database
    db.delete(db_item)
    db.commit()
    
    # Send what was deleted back
    return {"message": "item deleted", "item": Item(id=db_item.id, name=db_item.name, description=db_item.description)}

# run api
if __name__ == "__main__":
    uvicorn.run(
        "main1:app",
        host="localhost",
        port=8000,
        reload=True
    )
