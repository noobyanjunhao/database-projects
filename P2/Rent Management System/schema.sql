CREATE TABLE Apartment (
  id INT PRIMARY KEY AUTO_INCREMENT,
  unit_number VARCHAR(10) NOT NULL,
  unit_size INT NOT NULL,
  ownership_type ENUM('sold', 'rent_controlled', 'rent_stabilized', 'market') NOT NULL,
  is_special BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE Tenant (
  id INT PRIMARY KEY AUTO_INCREMENT,
  first_name VARCHAR(50) NOT NULL,
  last_name VARCHAR(50) NOT NULL,
  full_name VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Lease (
  id INT PRIMARY KEY AUTO_INCREMENT,
  tenant_id INT NOT NULL,
  apartment_id INT NOT NULL,
  start_date DATE NOT NULL,
  end_date DATE,
  monthly_rent DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (tenant_id) REFERENCES Tenant(id),
  FOREIGN KEY (apartment_id) REFERENCES Apartment(id)
);

CREATE TABLE Bill (
  id INT PRIMARY KEY AUTO_INCREMENT,
  lease_id INT NOT NULL,
  billing_month DATE NOT NULL,
  rent_amount DECIMAL(10,2) NOT NULL,
  other_charges JSON,
  balance_used DECIMAL(10,2) NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (lease_id) REFERENCES Lease(id)
);

CREATE TABLE Payment (
  id INT PRIMARY KEY AUTO_INCREMENT,
  bill_id INT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  payment_date DATE NOT NULL,
  check_number VARCHAR(50),
  remitter_name VARCHAR(100) NOT NULL,
  FOREIGN KEY (bill_id) REFERENCES Bill(id)
);