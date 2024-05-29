from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from bson.objectid import ObjectId

app = FastAPI()

# MongoDB setup
client = MongoClient("mongodb://localhost:27017")
db = client.students_db
collection = db.students_collection

# Pydantic models
class Student(BaseModel):
    name: str
    roll_no: int

class StudentInDB(Student):
    id: str

@app.post("/students/", response_model=StudentInDB)
def create_student(student: Student):
    # student_dict = student.dict()
    student_dict = student.model_dump()
    result = collection.insert_one(student_dict)
    student_in_db = StudentInDB(id=str(result.inserted_id), **student_dict)
    return student_in_db

@app.get("/students/", response_model=List[StudentInDB])
def read_students(skip: int = 0, limit: int = 10):
    students = collection.find().skip(skip).limit(limit)
    return [StudentInDB(id=str(student["_id"]), **student) for student in students]

@app.get("/students/{student_id}", response_model=StudentInDB)
def read_student(student_id: str):
    student = collection.find_one({"_id": ObjectId(student_id)})
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentInDB(id=str(student["_id"]), **student)

@app.put("/students/{student_id}", response_model=StudentInDB)
def update_student(student_id: str, student: Student):
    result = collection.update_one({"_id": ObjectId(student_id)}, {"$set": student.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    updated_student = collection.find_one({"_id": ObjectId(student_id)})
    return StudentInDB(id=str(updated_student["_id"]), **updated_student)

@app.delete("/students/{student_id}", response_model=StudentInDB)
def delete_student(student_id: str):
    student = collection.find_one({"_id": ObjectId(student_id)})
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    collection.delete_one({"_id": ObjectId(student_id)})
    return StudentInDB(id=str(student["_id"]), **student)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
