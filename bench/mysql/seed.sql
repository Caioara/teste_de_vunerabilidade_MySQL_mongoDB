USE tcc_security;

INSERT INTO users (username, email, password_hash, role_name) VALUES
('admin', 'admin@tcc.local', 'hash_admin_demo', 'admin'),
('ana', 'ana@tcc.local', 'hash_ana_demo', 'user'),
('bruno', 'bruno@tcc.local', 'hash_bruno_demo', 'user');

INSERT INTO products (name, category, price, stock) VALUES
('Notebook', 'eletronicos', 3500.00, 12),
('Mouse', 'eletronicos', 80.00, 60),
('Cadeira', 'moveis', 620.00, 8),
('Mesa', 'moveis', 900.00, 5),
('Livro SQL', 'livros', 120.00, 25);

INSERT INTO access_logs (user_id, action_name, ip_address) VALUES
(1, 'login', '127.0.0.1'),
(2, 'search_product', '127.0.0.1'),
(3, 'view_product', '127.0.0.1');

