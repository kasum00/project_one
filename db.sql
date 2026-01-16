DROP DATABASE IF EXISTS fashion_db;
CREATE DATABASE fashion_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE fashion_db;



CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  full_name VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


ALTER TABLE users
ADD COLUMN has_profile BOOLEAN DEFAULT FALSE;

CREATE TABLE user_profiles (
  user_id INT PRIMARY KEY,
  gender ENUM('male', 'female', 'other'),
  height_cm INT,
  style_preference ENUM('casual','sport','formal','street','minimal'),
  favorite_color VARCHAR(100),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


CREATE TABLE categories (
  id INT AUTO_INCREMENT PRIMARY KEY,
  code VARCHAR(50) NOT NULL UNIQUE,
  display_name VARCHAR(100)
);


INSERT INTO categories (code, display_name) VALUES
('tops', 'Tops'),
('bottoms', 'Bottoms'),
('dress', 'Dresses'),
('shoes', 'Shoes'),
('bag', 'Bags'),
('accessories', 'Accessories'),
('others', 'Others');


CREATE TABLE wardrobe_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  category_id INT,
  image_path VARCHAR(255) NOT NULL,
  embedding_path VARCHAR(255) NOT NULL,

  ai_label VARCHAR(100),        -- nhãn model dự đoán
  confidence FLOAT,             -- độ tin cậy của model
  user_label VARCHAR(100),      -- nhãn người dùng sửa (nếu có)

  is_deleted BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE outfits (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  name VARCHAR(100),
  source ENUM('ai','user') DEFAULT 'ai',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


CREATE TABLE outfit_items (
  outfit_id INT NOT NULL,
  wardrobe_item_id INT NOT NULL,
  PRIMARY KEY (outfit_id, wardrobe_item_id),
  FOREIGN KEY (outfit_id) REFERENCES outfits(id) ON DELETE CASCADE,
  FOREIGN KEY (wardrobe_item_id) REFERENCES wardrobe_items(id) ON DELETE CASCADE
);


CREATE TABLE recommendation_logs (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  source_item_id INT NOT NULL,
  recommended_item_id INT NOT NULL,
  similarity_score FLOAT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (source_item_id) REFERENCES wardrobe_items(id),
  FOREIGN KEY (recommended_item_id) REFERENCES wardrobe_items(id)
);

CREATE TABLE model_evaluations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT,
  total_items INT,
  correct_items INT,
  accuracy FLOAT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);


CREATE INDEX idx_user_items ON wardrobe_items(user_id);
CREATE INDEX idx_category_items ON wardrobe_items(category_id);
CREATE INDEX idx_user_created ON wardrobe_items(user_id, created_at);
CREATE INDEX idx_recommend_user ON recommendation_logs(user_id);

DROP USER IF EXISTS 'fashion_user'@'localhost';
FLUSH PRIVILEGES;

CREATE USER 'fashion_user'@'localhost'
IDENTIFIED WITH mysql_native_password BY 'fashion_pass';


GRANT ALL PRIVILEGES ON fashion_db.* TO 'fashion_user'@'localhost';
FLUSH PRIVILEGES;

SELECT user, host, plugin
FROM mysql.user
WHERE user = 'fashion_user';
SET SQL_SAFE_UPDATES = 0;
UPDATE wardrobe_items
SET image_path = REPLACE(
  image_path,
  'D:\\project1test\\backend\\src\\',
  ''
)
WHERE image_path LIKE 'D:%';
UPDATE wardrobe_items
SET image_path = REPLACE(
  image_path,
  'backend\\src\\',
  ''
)
WHERE image_path LIKE '%backend%';

SET SQL_SAFE_UPDATES = 1;

SELECT id, image_path
FROM wardrobe_items
LIMIT 10;

UPDATE wardrobe_items
SET image_path = REPLACE(image_path, '\\', '/');

SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE wardrobe_items;
TRUNCATE TABLE outfit_items;

SET FOREIGN_KEY_CHECKS = 1;

