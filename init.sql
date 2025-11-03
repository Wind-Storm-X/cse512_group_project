-- init.sql

-- Create the main database
CREATE DATABASE IF NOT EXISTS library_system;

-- Switch to it
USE library_system;

CREATE TABLE IF NOT EXISTS patrons_A (
    card_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name STRING,
    last_name STRING
);

CREATE TABLE IF NOT EXISTS patrons_B (
    card_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name STRING,
    last_name STRING
);

CREATE TABLE IF NOT EXISTS patrons_C (
    card_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name STRING,
    last_name STRING
);

-- library_id is the unique internal id for the book
-- I chose this as the PK instead of isbn so that you can have multiple copies of the same book 
-- Also, library_id should be set up to have a value automatically assigned (????)
CREATE TABLE IF NOT EXISTS books_A (
    library_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    isbn int,
    book_name STRING NOT NULL,
    book_author_fn STRING,
    book_author_ln STRING,
    checked_out BOOLEAN,
    patron_checked_out UUID REFERENCES patrons_A(card_id)
);

CREATE TABLE IF NOT EXISTS books_B (
    library_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    isbn int,
    book_name STRING NOT NULL,
    book_author_fn STRING,
    book_author_ln STRING,
    checked_out BOOLEAN,
    patron_checked_out UUID REFERENCES patrons_B(card_id)
);

CREATE TABLE IF NOT EXISTS books_C (
    library_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    isbn int,
    book_name STRING NOT NULL,
    book_author_fn STRING,
    book_author_ln STRING,
    checked_out BOOLEAN,
    patron_checked_out UUID REFERENCES patrons_C(card_id)
);