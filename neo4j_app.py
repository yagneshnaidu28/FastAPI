from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from neo4j import GraphDatabase
from typing import List
import uuid

# Database Setup
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "password")
driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

# Pydantic Schemas (Serialization)
class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: str

# App & CORS Middleware
app = FastAPI(title="FastAPI + Neo4j CRUD")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
def shutdown_event():
    driver.close()

# CRUD Endpoints
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    user_id = str(uuid.uuid4())
    query = """
    CREATE (u:User {id: $id, name: $name, email: $email})
    RETURN u.id AS id, u.name AS name, u.email AS email
    """
    with driver.session() as session:
        result = session.run(query, id=user_id, name=user.name, email=user.email).single()
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create user")
        return UserResponse(**result.data())

@app.get("/users", response_model=List[UserResponse])
def read_users():
    query = """
    MATCH (u:User)
    RETURN u.id AS id, u.name AS name, u.email AS email
    """
    with driver.session() as session:
        result = session.run(query)
        return [UserResponse(**record.data()) for record in result]

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: str):
    query = """
    MATCH (u:User {id: $id})
    RETURN u.id AS id, u.name AS name, u.email AS email
    """
    with driver.session() as session:
        result = session.run(query, id=user_id).single()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**result.data())

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user: UserCreate):
    query = """
    MATCH (u:User {id: $id})
    SET u.name = $name, u.email = $email
    RETURN u.id AS id, u.name AS name, u.email AS email
    """
    with driver.session() as session:
        result = session.run(query, id=user_id, name=user.name, email=user.email).single()
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**result.data())

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
    query = """
    MATCH (u:User {id: $id})
    DETACH DELETE u
    RETURN count(u) AS deleted_count
    """
    with driver.session() as session:
        result = session.run(query, id=user_id).single()
        if not result or result["deleted_count"] == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)