USE oa_production;

CREATE TABLE IF NOT EXISTS secrets (
  id INT PRIMARY KEY,
  name VARCHAR(100),
  value TEXT
);

INSERT INTO secrets (id, name, value) VALUES
(1, 'master_key', '__FLAG__'),
(2, 'api_token', 'sk-prod-28f7a91c3d4e5f6g7h8i9j0k');
