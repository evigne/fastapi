from fastapi import FastAPI, Path, Query
from pydantic import BaseModel, Field
from typing import Optional


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_date: int

    def __init__(self, id, title, author, description, rating, published_date):
        self.id = id
        self.author = author
        self.title = title
        self.description = description
        self.rating = rating
        self.published_date = published_date


class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not needed on creation", default=None)
    title: str = Field(min_len=3)
    author: str = Field(min_length=1)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=0, lt=6)
    published_date: int = Field(gt=1999, lt=2031)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "fastapi advance",
                "author": "vignesh",
                "description": "this is fastapi book",
                "rating": 5,
                "published_date": 2024,
            }
        }
    }


app = FastAPI()

books = [
    Book(1, "Computer Science Pro", "codingwithroby", "A very nice book!", 5, 2030),
    Book(2, "Be Fast with FastAPI", "codingwithroby", "A great book!", 5, 2030),
    Book(3, "Master Endpoints", "codingwithroby", "A awesome book!", 5, 2029),
    Book(4, "HP1", "Author 1", "Book Description", 2, 2028),
    Book(5, "HP2", "Author 2", "Book Description", 3, 2027),
    Book(6, "HP3", "Author 3", "Book Description", 1, 2026),
]


@app.get("/books")
async def get_books():
    return books


@app.get("/books/{book_id}")
async def red_book(book_id: int = Path(gt=0)):
    for book in books:
        if book.id == book_id:
            return book
    # else:
    return {"message": "Book not found"}


@app.get("/books/rating/")
async def read_rating(rating: int = Query(gt=0, lt=6)):
    books_return = []
    for book in books:
        if book.rating == rating:
            books_return.append(book)
    return books_return


@app.get("/books/published/")
async def read_rating(published: int = Query(gt=1999, lt=2031)):
    books_return = []
    for book in books:
        if book.published_date == published:
            books_return.append(book)
    return books_return


@app.post("/create-book")
async def create_books(books_request: BookRequest):
    new_book = Book(**books_request.dict())
    books.append(find_book_id(new_book))


@app.put("/update-bood")
async def update_book(book_req: BookRequest):
    for i in range(len(books)):
        if books[i].id == book_req.id:
            books[i] = book_req
    return books


@app.delete("/books/{book_id}")
async def delete_book(book_id: int = Path(gt=0)):
    for i in range(len(books)):
        if books[i].id == book_id:
            books.pop(i)
            break


def find_book_id(book: Book):
    book.id = 1 if len(books) == 0 else books[-1].id + 1
    return book
