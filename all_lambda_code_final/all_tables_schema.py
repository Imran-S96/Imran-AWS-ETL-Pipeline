CREATE TABLE products (
    product_id INT NOT NULL IDENTITY(1,1),	
    product_name VARCHAR(250) NOT NULL,	
    product_price DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (product_id)
);

CREATE TABLE transactions (
    transaction_id INT IDENTITY(1,1) PRIMARY KEY,
    date_time TIMESTAMP NOT NULL,
    location VARCHAR(255) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(255) NOT NULL
);

CREATE TABLE orders(
    order_id INT NOT NULL IDENTITY(1,1),	
    transaction_id INT NOT NULL,	
    product_id INT NOT NULL,
    PRIMARY KEY (order_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);