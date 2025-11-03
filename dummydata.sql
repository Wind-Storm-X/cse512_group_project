-- dummydata.sql

-- Switch to the library_system database
USE library_system;

-- Insert 5 patrons into patrons_A
INSERT INTO patrons_A (first_name, last_name) VALUES
('Alice', 'Johnson'),
('Bob', 'Smith'),
('Carol', 'Williams'),
('David', 'Brown'),
('Eva', 'Davis');

-- Insert 5 patrons into patrons_B
INSERT INTO patrons_B (first_name, last_name) VALUES
('Frank', 'Miller'),
('Grace', 'Wilson'),
('Henry', 'Moore'),
('Ivy', 'Taylor'),
('Jack', 'Anderson');

-- Insert 5 patrons into patrons_C
INSERT INTO patrons_C (first_name, last_name) VALUES
('Karen', 'Thomas'),
('Leo', 'Jackson'),
('Mia', 'White'),
('Nathan', 'Harris'),
('Olivia', 'Martin');

-- Insert 5 books into books_A (some checked out, some available)
INSERT INTO books_A (isbn, book_name, book_author_fn, book_author_ln, checked_out, patron_checked_out) VALUES
(9780451524935, '1984', 'George', 'Orwell', true, (SELECT card_id FROM patrons_A WHERE first_name = 'Alice' AND last_name = 'Johnson')),
(9780141439518, 'Pride and Prejudice', 'Jane', 'Austen', false, NULL),
(9780061120084, 'To Kill a Mockingbird', 'Harper', 'Lee', true, (SELECT card_id FROM patrons_A WHERE first_name = 'Bob' AND last_name = 'Smith')),
(9780439023481, 'The Hunger Games', 'Suzanne', 'Collins', false, NULL),
(9780544003415, 'The Lord of the Rings', 'J.R.R.', 'Tolkien', true, (SELECT card_id FROM patrons_A WHERE first_name = 'Carol' AND last_name = 'Williams'));

-- Insert 5 books into books_B (some checked out, some available)
INSERT INTO books_B (isbn, book_name, book_author_fn, book_author_ln, checked_out, patron_checked_out) VALUES
(9780439358071, 'Harry Potter and the Prisoner of Azkaban', 'J.K.', 'Rowling', true, (SELECT card_id FROM patrons_B WHERE first_name = 'Frank' AND last_name = 'Miller')),
(9780385472579, 'The Things They Carried', 'Tim', 'OBrien', false, NULL),
(9780316769174, 'The Catcher in the Rye', 'J.D.', 'Salinger', true, (SELECT card_id FROM patrons_B WHERE first_name = 'Grace' AND last_name = 'Wilson')),
(9780140283334, 'The Great Gatsby', 'F. Scott', 'Fitzgerald', false, NULL),
(9780684830421, 'Brave New World', 'Aldous', 'Huxley', true, (SELECT card_id FROM patrons_B WHERE first_name = 'Henry' AND last_name = 'Moore'));

-- Insert 5 books into books_C (some checked out, some available)
INSERT INTO books_C (isbn, book_name, book_author_fn, book_author_ln, checked_out, patron_checked_out) VALUES
(9780142437264, 'Moby Dick', 'Herman', 'Melville', true, (SELECT card_id FROM patrons_C WHERE first_name = 'Karen' AND last_name = 'Thomas')),
(9780486415864, 'The Adventures of Huckleberry Finn', 'Mark', 'Twain', false, NULL),
(9780140449266, 'Crime and Punishment', 'Fyodor', 'Dostoevsky', true, (SELECT card_id FROM patrons_C WHERE first_name = 'Leo' AND last_name = 'Jackson')),
(9780486280615, 'The Scarlet Letter', 'Nathaniel', 'Hawthorne', false, NULL),
(9780141439600, 'Wuthering Heights', 'Emily', 'Brontë', true, (SELECT card_id FROM patrons_C WHERE first_name = 'Mia' AND last_name = 'White'));