DROP TABLE IF EXISTS Payment;
DROP TABLE IF EXISTS Bill;
DROP TABLE IF EXISTS Lease;
DROP TABLE IF EXISTS Tenant;
DROP TABLE IF EXISTS Apartment;

CREATE TABLE Apartment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  unit_number TEXT NOT NULL,
  unit_size INTEGER NOT NULL,
  ownership_type TEXT NOT NULL CHECK (ownership_type IN ('sold', 'rent_controlled', 'rent_stabilized', 'market')),
  is_special BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE Tenant (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE
);

CREATE TABLE Lease (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tenant_id INTEGER NOT NULL,
  apartment_id INTEGER NOT NULL,
  start_date DATE,
  end_date DATE,
  monthly_rent DECIMAL(10,2),
  FOREIGN KEY (tenant_id) REFERENCES Tenant(id),
  FOREIGN KEY (apartment_id) REFERENCES Apartment(id)
);

CREATE TABLE Bill (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  lease_id INTEGER NOT NULL,
  billing_month DATE NOT NULL,
  rent_amount DECIMAL(10,2) NOT NULL,
  other_charges TEXT, 
  balance_used DECIMAL(10,2) NOT NULL,
  total_amount DECIMAL(10,2) NOT NULL,
  sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (lease_id) REFERENCES Lease(id)
);

CREATE TABLE Payment (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  bill_id INTEGER NOT NULL,
  amount DECIMAL(10,2) NOT NULL CHECK (amount >= 0),
  payment_date DATE NOT NULL,
  check_number TEXT,
  remitter_name TEXT NOT NULL,
  FOREIGN KEY (bill_id) REFERENCES Bill(id)
);
