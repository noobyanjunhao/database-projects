-- tests/data.sql

-- Apartments
INSERT INTO Apartment (id, unit_number, unit_size, ownership_type, is_special)
VALUES
  (1, '101', '500 sqft', 'sold', 0),
  (2, '102', '600 sqft', 'rent_controlled', 1);

-- Tenants
INSERT INTO Tenant (id, full_name, email)
VALUES
  (1, 'Alice', 'alice@example.com'),
  (2, 'Bob',   'bob@example.com');

-- Leases
INSERT INTO Lease (id, apartment_id, tenant_id, start_date, end_date, monthly_rent)
VALUES
  (1, 1, 1, '2025-01-01', '2025-12-31', 1200),
  (2, 2, 2, '2025-01-01', '2025-12-31', 1300);
