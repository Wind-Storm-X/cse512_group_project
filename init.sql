-- init.sql

-- Create the main database
CREATE DATABASE IF NOT EXISTS library_system;

-- Switch to it
USE library_system;

-- library_id is the unique internal id for the book
-- I chose this as the PK instead of isbn so that you can have multiple copies of the same book 
-- Also, library_id should be set up to have a value automatically assigned (????)
CREATE TABLE IF NOT EXISTS books_A (
    library_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    isbn int,
    book_name STRING NOT NULL,
    book_author_fn STRING,
    book_author_ln STRING,
    checked_out BOOLEAN
);

CREATE TABLE IF NOT EXISTS books_B (
    library_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    isbn int,
    book_name STRING NOT NULL,
    book_author_fn STRING,
    book_author_ln STRING,
    checked_out BOOLEAN
);

CREATE TABLE IF NOT EXISTS books_C (
    library_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    isbn int,
    book_name STRING NOT NULL,
    book_author_fn STRING,
    book_author_ln STRING,
    checked_out BOOLEAN
);

/*INSERT INTO authors (name, birth_year) VALUES ('George Orwell', 1903);
INSERT INTO books (title, author_id, published_year, genre)
SELECT '1984', id, 1949, 'Dystopian' FROM authors WHERE name = 'George Orwell';*/