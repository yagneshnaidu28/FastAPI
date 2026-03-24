#importing necessary modules
from fastapi import FastAPI,HTTpException
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
    description:str |None=None


#In-Memory Storage
items={}

#define crud endpoints

#create -Post
@app.post("/items/")
def create_item(item:ItemCreate):
    item_id=str(uuid.uuid4())
    new_item=Item(id=item_id,**item.model_dump())
    items[item_id]=new_item
    return{"mossage":"Item Created","item":new_item}

#read-GET all items
@app.get("/items/")
def read_items():
    return{"items":list(items.values())}

#read-GET one items
@app.get("items/{item_id}")
def read_item(item_id:str):
    if item_id not in items:
        raise HTTpException(status_code=404,details="item not found")
    return{"item":items[item_id]}

#update-PUT
@app.put("/items/{item_id}")
def update_item(item_id:str,item:Item):
    if item_id not in items:
        raise HTTpException(status_code=404,details="item not found")
    items[item_id]=item
    return {"message":"item updated","item":item}

#delete-delete
@app.delete("/itmes/{item_id}")
def delete_item(item_id:str):
    if item_id not in items:
         raise HTTpException(status_code=404,details="item not found")
    delete_item=items.pop(item_id)
    return{"message":"item deleted","item":delete_item}

