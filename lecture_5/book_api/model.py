from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from typing import List, Optional
from pydantic import BaseModel

# Database engine configuration
engine = create_engine("sqlite:///books_colection.db", echo=True)

# Session factory for database operations
Session = sessionmaker(bind=engine)
session = Session()


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""
    pass


class Book(Base):
    """
    SQLAlchemy model representing a book in the database.
    
    Attributes:
        id: Primary key identifier for the book
        title: Title of the book (required)
        author: Author of the book (required)
        year: Publication year of the book (optional)
    """
    __tablename__ = "Book"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    year = Column(Integer)


# Create all database tables based on the defined models
Base.metadata.create_all(engine)


class BookResponse(BaseModel):
    """
    Pydantic model for serializing book data in API responses.
    
    Attributes:
        id: Unique identifier of the book
        title: Title of the book
        author: Author of the book
        year: Publication year (optional)
    """
    id: int
    title: str
    author: str
    year: Optional[int] = None
    
    class Config:
        """Pydantic configuration for ORM compatibility."""
        from_attributes = True


def add_new_book(new_title: str, new_author: str, new_year: Optional[int] = None) -> Book:
    """
    Add a new book to the database.
    
    Args:
        new_title: Title of the new book
        new_author: Author of the new book
        new_year: Publication year of the new book (optional)
    
    Returns:
        Book: The newly created Book object with its database-generated ID
    
    Example:
        >>> add_new_book("The Great Gatsby", "F. Scott Fitzgerald", 1925)
    """
    new_book = Book(title=new_title, author=new_author, year=new_year)
    session.add(new_book)
    session.commit()
    session.refresh(new_book)
    return new_book


def get_all_book() -> List[BookResponse]:
    """
    Retrieve all books from the database.
    
    Returns:
        List[BookResponse]: List of all books serialized as BookResponse objects
    
    Example:
        >>> get_all_book()
        [BookResponse(id=1, title="Book 1", author="Author 1", year=2020), ...]
    """
    books = session.query(Book).all()
    return [BookResponse.model_validate(book) for book in books]


def delete_book(delete_id: int) -> bool:
    """
    Delete a book from the database by its ID.
    
    Args:
        delete_id: ID of the book to delete
    
    Returns:
        bool: True if the book was successfully deleted, False if no book was found
    
    Example:
        >>> delete_book(1)
        True
        >>> delete_book(999)
        False
    """
    book_to_be_deleted = session.query(Book).filter(Book.id == delete_id).first()
    if book_to_be_deleted:
        session.delete(book_to_be_deleted)
        session.commit()
        return True
    return False


def update_book_details(
    book_update_id: int,
    update_title: Optional[str] = None,
    update_author: Optional[str] = None,
    update_year: Optional[int] = None
) -> Optional[BookResponse]:
    """
    Update the details of an existing book.
    
    Args:
        book_update_id: ID of the book to update
        update_title: New title for the book (optional, if provided will update)
        update_author: New author for the book (optional, if provided will update)
        update_year: New publication year for the book (optional, if provided will update)
    
    Returns:
        Optional[BookResponse]: Updated book data as BookResponse object if found, 
        None if no book with the given ID exists
    
    Example:
        >>> update_book_details(1, update_title="New Title")
        BookResponse(id=1, title="New Title", author="Original Author", year=2020)
    """
    update_book = session.query(Book).filter(Book.id == book_update_id).first()
    
    if not update_book:
        return None
    
    # Apply updates only for provided parameters
    if update_title is not None:
        update_book.title = update_title
    if update_author is not None:
        update_book.author = update_author
    if update_year is not None:
        update_book.year = update_year
    
    session.commit()
    session.refresh(update_book)
    return BookResponse.model_validate(update_book)


def search_books(
    search_title: Optional[str] = None,
    search_author: Optional[str] = None,
    search_year: Optional[int] = None
) -> List[BookResponse]:
    """
    Search for books based on title, author, and/or year.
    
    Args:
        search_title: Exact title to search for (optional)
        search_author: Exact author to search for (optional)
        search_year: Exact publication year to search for (optional)
    
    Returns:
        List[BookResponse]: List of books matching all provided search criteria.
        Returns empty list if no criteria provided or no matches found.
    
    Note:
        This function performs AND filtering - all provided criteria must match.
        Returns empty list if no search criteria are provided.
    
    Example:
        >>> search_books(search_author="F. Scott Fitzgerald")
        [BookResponse(id=1, title="The Great Gatsby", author="F. Scott Fitzgerald", year=1925)]
    """
    
    # Return empty list if no search criteria provided
    if all(param is None for param in [search_title, search_author, search_year]):
        return []
    
    query = session.query(Book)
    
    # Build filter conditions based on provided parameters
    filters = []
    if search_title is not None:
        filters.append(Book.title == search_title)
    if search_author is not None:
        filters.append(Book.author == search_author)
    if search_year is not None:
        filters.append(Book.year == search_year)
    
    # Apply all filters (AND logic)
    if filters:
        query = query.filter(*filters)
    
    books = query.all()
    
    return [BookResponse.model_validate(book) for book in books]