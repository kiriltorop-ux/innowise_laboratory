from fastapi import FastAPI, HTTPException, status
from typing import Optional
from .model import get_all_book, add_new_book, delete_book, search_books, update_book_details
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Books API")


class BookCreate(BaseModel):
    """
    Pydantic model for creating a new book.
    
    Attributes:
        title: Title of the book
        author: Author of the book
        year: Publication year of the book (optional)
    """
    title: str
    author: str
    year: Optional[int] = None


class BookUpdate(BaseModel):
    """
    Pydantic model for updating an existing book.
    
    Attributes:
        title: New title for the book (optional)
        author: New author for the book (optional)
        year: New publication year for the book (optional)
    """
    title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None


class BookResponse(BaseModel):
    """
    Pydantic model for book responses from the API.
    
    Attributes:
        id: Unique identifier of the book
        title: Title of the book
        author: Author of the book
        year: Publication year of the book (optional)
    """
    id: int
    title: str
    author: str
    year: Optional[int] = None
    
    class Config:
        """Configuration for Pydantic model to work with SQLAlchemy ORM objects."""
        from_attributes = True


@app.get("/books/", response_model=List[BookResponse])
def get_books() -> List[BookResponse]:
    """
    Retrieve all books from the database.
    
    Returns:
        List[BookResponse]: A list of all books in the database
    
    Example:
        >>> GET /books/
        Returns: [{"id": 1, "title": "Book 1", "author": "Author 1", "year": 2020}, ...]
    """
    return get_all_book()


@app.post("/books/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate) -> BookResponse:
    """
    Create a new book in the database.
    
    Args:
        book (BookCreate): Book data including title, author, and optional year
    
    Returns:
        BookResponse: The newly created book with its assigned ID
    
    Raises:
        HTTPException: 400 Bad Request if there's an error creating the book
    
    Example:
        >>> POST /books/
        Request Body: {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925}
        Returns: {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925}
    """
    try:
        new_book = add_new_book(book.title, book.author, book.year)
        return BookResponse.model_validate(new_book)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating book: {str(e)}"
        )


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book_endpoint(book_id: int) -> None:
    """
    Delete a book by its ID.
    
    Args:
        book_id (int): ID of the book to delete
    
    Raises:
        HTTPException: 404 Not Found if the book with given ID doesn't exist
    
    Example:
        >>> DELETE /books/1
        Returns: 204 No Content (if successful)
    """
    deleted = delete_book(book_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    return None


@app.put("/books/{book_id}", response_model=BookResponse)
def update_book(book_id: int, book_update: BookUpdate) -> BookResponse:
    """
    Update an existing book's details.
    
    Args:
        book_id (int): ID of the book to update
        book_update (BookUpdate): Partial book data with fields to update
    
    Returns:
        BookResponse: The updated book data
    
    Raises:
        HTTPException: 404 Not Found if the book with given ID doesn't exist
    
    Example:
        >>> PUT /books/1
        Request Body: {"title": "Updated Title", "year": 2023}
        Returns: {"id": 1, "title": "Updated Title", "author": "Original Author", "year": 2023}
    """
    updated_book = update_book_details(
        book_id, 
        update_title=book_update.title,
        update_author=book_update.author,
        update_year=book_update.year
    )
    
    if not updated_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    
    return updated_book


@app.get("/books/search/", response_model=List[BookResponse])
def search_books_endpoint(
    title: Optional[str] = None,
    author: Optional[str] = None,
    year: Optional[int] = None
) -> List[BookResponse]:
    """
    Search for books by title, author, and/or year.
    
    Args:
        title (Optional[str]): Exact title to search for
        author (Optional[str]): Exact author to search for
        year (Optional[int]): Exact publication year to search for
    
    Returns:
        List[BookResponse]: List of books matching all provided search criteria.
        Returns empty list if no matches found.
    
    Note:
        This endpoint uses AND logic - books must match all provided criteria.
        At least one search parameter should be provided.
    
    Example:
        >>> GET /books/search/?author=F.%20Scott%20Fitzgerald&year=1925
        Returns: [{"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925}]
    """
    return search_books(search_title=title, search_author=author, search_year=year)