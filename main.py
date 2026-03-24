#importing necessary modules
from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import uvicorn
import uuid

#create FastAPI instance
app=FastAPI()

#create data models
class ItemCreate(BaseModel):
    name:str
    description:str|None=None

class Item(BaseModel):
    id:str
    name:str
    description:str|None=None

#In-Memory Storage
items={}

#define crud endpoints

#create -Post
@app.post("/items/")
def create_item(item:ItemCreate):
    item_id=str(uuid.uuid4())
    new_item=Item(id=item_id,**item.model_dump())
    items[item_id]=new_item
    return{"message":"Item Created","item":new_item}

#read-GET all items
@app.get("/items/")
def read_items():
    return{"items":list(items.values())}

#read-GET one items
@app.get("/items/{item_id}")
def read_item(item_id:str):
    if item_id not in items:
        raise HTTPException(status_code=404,detail="item not found")
    return{"item":items[item_id]}

#update-PUT
@app.put("/items/{item_id}")
def update_item(item_id:str,item:Item):
    if item_id not in items:
        raise HTTPException(status_code=404,detail="item not found")
    items[item_id]=item
    return {"message":"item updated","item":item}

#delete-delete
@app.delete("/items/{item_id}")
def delete_item(item_id:str):
    if item_id not in items:
         raise HTTPException(status_code=404,detail="item not found")
    deleted_item=items.pop(item_id)
    return{"message":"item deleted","item":deleted_item}

#run api
if __name__=="__main__":
    # If your file is not named main.py, change "main:app" to "your_filename:app"
    uvicorn.run(
        app, 
        host="127.0.0.1",
        port=8000
    )