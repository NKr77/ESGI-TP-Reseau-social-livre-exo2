# API Réseau social de livres (ESGI - Rendu Exercice 2)

API RESTful développée avec FastAPI simulant un réseau social de partage de livres.

## Spécifications techniques
- **Versionnement** : Préfixe `/api/v1/` pour toutes les routes.
- **Auto-incrémentation** : Les IDs des livres et des avis sont gérés par le serveur.
- **Validation Pydantic** : Notes limitées entre 1 et 5 (`Field(ge=1, le=5)`).
- **Rigueur métier** : Vérification de l'existence du livre avant ajout d'avis ou de favori.

## Lancement du projet
1. Installation : `pip install fastapi uvicorn pydantic`
2. Lancement : `python main.py`
3. URL API : http://127.0.0.1:8000/api/v1/
4. Swagger UI : http://127.0.0.1:8000/docs

## Guide des tests Postman

### Collection de partage
[Accéder à la collection Postman](https://krusicnicolas-8422704.postman.co/workspace/NK-Team's-Workspace~55c351b5-2b5b-41e0-823a-09f811529620/collection/51921457-82119953-5f5c-497f-af03-a96fd943c79b?action=share&creator=51921457)

### Exemples de requêtes
1. **POST http://127.0.0.1:8000/api/v1/books** : Créer un livre.
   - Body JSON : `{"title": "1984", "author": "George Orwell"}`
2. **GET http://127.0.0.1:8000/api/v1/books?search=1984** : Rechercher par titre.
3. **POST http://127.0.0.1:8000/api/v1/books/1/reviews** : Ajouter un avis.
   - Body JSON : `{"user_id": 10, "comment": "Excellent", "rating": 5}`
4. **POST http://127.0.0.1:8000/api/v1/users/10/bookmarks/1** : Ajouter aux favoris.

## Liste des Endpoints

| Méthode | Route | Action |
| :--- | :--- | :--- |
| GET | `/api/v1/books` | Liste des livres. |
| POST | `/api/v1/books` | Créer un livre. |
| GET | `/api/v1/books/{id}` | Détails d'un livre. |
| PUT | `/api/v1/books/{id}` | Modifier un livre. |
| DELETE | `/api/v1/books/{id}` | Supprimer un livre. |
| GET | `/api/v1/books/{id}/reviews` | Voir les avis. |
| POST | `/api/v1/books/{id}/reviews` | Laisser un avis. |
| POST | `/api/v1/users/{u_id}/bookmarks/{b_id}` | Ajouter un favori. |
| DELETE | `/api/v1/users/{u_id}/bookmarks/{b_id}` | Retirer un favori. |
