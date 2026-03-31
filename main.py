from fastapi import FastAPI, HTTPException, status  
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

# --- MODÈLES ---

class Book(BaseModel):
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)

class BookResponse(Book):
    id: int

class ReviewCreate(BaseModel):
    user_id: int
    comment: str
    rating: int = Field(..., ge=1, le=5)

class ReviewResponse(ReviewCreate):
    id: int
    book_id: int

# --- BASE DE DONNÉES EN MÉMOIRE ---

books_db = []
reviews_db = []
bookmarks_db = {} 

# Compteurs pour l'auto-incrémentation
book_id_counter = 1
review_id_counter = 1

# --- FONCTION UTILITAIRE ---

def check_book_exists(book_id: int):
    if not any(b["id"] == book_id for b in books_db):
        raise HTTPException(status_code=404, detail=f"Livre {book_id} non trouvé")

# --- ROUTES ---

@app.get("/api/v1/books", response_model=List[BookResponse])
def get_books(search: Optional[str] = None):
    if search:
        return [b for b in books_db if search.lower() in b["title"].lower()]
    return books_db

@app.get("/api/v1/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    check_book_exists(book_id)
    return next(b for b in books_db if b["id"] == book_id)

@app.post("/api/v1/books", response_model=BookResponse, status_code=201)
def create_book(book: Book):
    global book_id_counter
    new_book = {"id": book_id_counter, **book.model_dump()}
    books_db.append(new_book)
    book_id_counter += 1
    return new_book

@app.put("/api/v1/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, updated_book: Book):
    check_book_exists(book_id)
    for i, b in enumerate(books_db):
        if b["id"] == book_id:
            books_db[i] = {"id": book_id, **updated_book.model_dump()}
            return books_db[i]

@app.delete("/api/v1/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    check_book_exists(book_id)
    global books_db
    books_db = [b for b in books_db if b["id"] != book_id]
    return

@app.get("/api/v1/books/{book_id}/reviews", response_model=List[ReviewResponse])
def get_book_reviews(book_id: int):
    check_book_exists(book_id)
    return [r for r in reviews_db if r["book_id"] == book_id]

@app.post("/api/v1/books/{book_id}/reviews", response_model=ReviewResponse, status_code=201)
def add_review(book_id: int, review: ReviewCreate):
    global review_id_counter
    check_book_exists(book_id)
    
    new_review = {"id": review_id_counter, "book_id": book_id, **review.model_dump()}
    reviews_db.append(new_review)
    review_id_counter += 1
    return new_review

# 2. Validation Bookmarks
@app.post("/api/v1/users/{user_id}/bookmarks/{book_id}")
def add_bookmark(user_id: int, book_id: int):
    # Vérification de l'existence du livre avant de le bookmarker
    check_book_exists(book_id)
    if user_id not in bookmarks_db: bookmarks_db[user_id] = []
    if book_id not in bookmarks_db[user_id]:
        bookmarks_db[user_id].append(book_id)
    return {"message": f"Livre {book_id} ajouté aux favoris de l'utilisateur {user_id}"}

@app.delete("/api/v1/users/{user_id}/bookmarks/{book_id}")
def remove_bookmark(user_id: int, book_id: int):
    if user_id in bookmarks_db and book_id in bookmarks_db[user_id]:
        bookmarks_db[user_id].remove(book_id)
        return {"message": "Livre retiré des favoris"}
    raise HTTPException(status_code=404, detail="Relation de favori non trouvée")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)