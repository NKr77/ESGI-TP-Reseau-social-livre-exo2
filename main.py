from fastapi import FastAPI, HTTPException, status  
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

# --- MODÈLES ---

# Données reçues à la création d'un livre
class Book(BaseModel):
    title: str = Field(..., min_length=1)   # Titre obligatoire
    author: str = Field(..., min_length=1)  # Auteur obligatoire

# Données renvoyées au client
class BookResponse(Book):
    id: int

# Données reçues à la création d'un avis
class ReviewCreate(BaseModel):
    user_id: int
    comment: str
    rating: int = Field(..., ge=1, le=5)  # Note entre 1 et 5 uniquement

# Données renvoyées au client pour un avis
class ReviewResponse(ReviewCreate):
    id: int
    book_id: int

# --- BASE DE DONNÉES EN MÉMOIRE ---

books_db = []       # Liste de tous les livres
reviews_db = []     # Liste de tous les avis
bookmarks_db = {}   # Dictionnaire {user_id: [book_id, ...]}

# Compteurs pour générer des IDs uniques côté serveur
book_id_counter = 1
review_id_counter = 1

# --- FONCTION UTILITAIRE ---

# Erreur 404 si le livre n'existe pas dans la base
def check_book_exists(book_id: int):
    if not any(b["id"] == book_id for b in books_db):
        raise HTTPException(status_code=404, detail=f"Livre {book_id} non trouvé")

# --- ROUTES ---

# Retourne tous les livres, avec filtre optionnel sur le titre
@app.get("/api/v1/books", response_model=List[BookResponse])
def get_books(search: Optional[str] = None):
    if search:
        # Recherche insensible à la casse
        return [b for b in books_db if search.lower() in b["title"].lower()]
    return books_db

# Retourne un seul livre par son ID
@app.get("/api/v1/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    check_book_exists(book_id)
    return next(b for b in books_db if b["id"] == book_id)

# Crée un nouveau livre avec un ID auto-généré
@app.post("/api/v1/books", response_model=BookResponse, status_code=201)
def create_book(book: Book):
    global book_id_counter
    new_book = {"id": book_id_counter, **book.model_dump()}
    books_db.append(new_book)
    book_id_counter += 1
    return new_book

# Remplace complètement les données d'un livre existant
@app.put("/api/v1/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, updated_book: Book):
    check_book_exists(book_id)
    for i, b in enumerate(books_db):
        if b["id"] == book_id:
            books_db[i] = {"id": book_id, **updated_book.model_dump()}
            return books_db[i]

# Supprime un livre de la base (conserve l'ID pour éviter les conflits)
@app.delete("/api/v1/books/{book_id}", status_code=204)
def delete_book(book_id: int):
    check_book_exists(book_id)
    global books_db
    books_db = [b for b in books_db if b["id"] != book_id]
    return

# Retourne tous les avis liés à un livre spécifique
@app.get("/api/v1/books/{book_id}/reviews", response_model=List[ReviewResponse])
def get_book_reviews(book_id: int):
    check_book_exists(book_id)
    return [r for r in reviews_db if r["book_id"] == book_id]

# Ajoute un avis sur un livre (le livre doit exister)
@app.post("/api/v1/books/{book_id}/reviews", response_model=ReviewResponse, status_code=201)
def add_review(book_id: int, review: ReviewCreate):
    global review_id_counter
    check_book_exists(book_id)
    new_review = {"id": review_id_counter, "book_id": book_id, **review.model_dump()}
    reviews_db.append(new_review)
    review_id_counter += 1
    return new_review

# Ajoute un livre aux favoris d'un utilisateur (pas de doublon)
@app.post("/api/v1/users/{user_id}/bookmarks/{book_id}")
def add_bookmark(user_id: int, book_id: int):
    check_book_exists(book_id)  # Le livre doit exister
    if user_id not in bookmarks_db:
        bookmarks_db[user_id] = []  # Initialise la liste si c'est un nouvel utilisateur
    if book_id not in bookmarks_db[user_id]:
        bookmarks_db[user_id].append(book_id)
    return {"message": f"Livre {book_id} ajouté aux favoris de l'utilisateur {user_id}"}

# Retire un livre des favoris d'un utilisateur
@app.delete("/api/v1/users/{user_id}/bookmarks/{book_id}")
def remove_bookmark(user_id: int, book_id: int):
    if user_id in bookmarks_db and book_id in bookmarks_db[user_id]:
        bookmarks_db[user_id].remove(book_id)
        return {"message": "Livre retiré des favoris"}
    raise HTTPException(status_code=404, detail="Relation de favori non trouvée")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="127.0.0.1", port=8000)