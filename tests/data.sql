-- 创建 Customers 表
CREATE TABLE IF NOT EXISTS Customers (
    CustomerID TEXT PRIMARY KEY,
    CompanyName TEXT NOT NULL,
    ContactName TEXT NOT NULL,
    ContactTitle TEXT NOT NULL,
    Address TEXT NOT NULL,
    City TEXT NOT NULL,
    Region TEXT,
    PostalCode TEXT,
    Country TEXT NOT NULL,
    Phone TEXT NOT NULL,
    Fax TEXT
);

-- 插入测试数据
INSERT INTO Customers (CustomerID, CompanyName, ContactName, ContactTitle, Address, City, Country, Phone)
VALUES
    ('CUST1', 'Tech Solutions', 'Alice Johnson', 'Manager', '123 Tech St', 'New York', 'USA', '123-456-7890'),
    ('CUST2', 'Gadget Store', 'Bob Smith', 'CEO', '456 Market Ave', 'Los Angeles', 'USA', '987-654-3210');

---------------------------------------------------------------

-- 创建 Employees 表
CREATE TABLE IF NOT EXISTS Employees (
    EmployeeID INTEGER PRIMARY KEY AUTOINCREMENT,
    LastName TEXT NOT NULL,
    FirstName TEXT NOT NULL,
    Title TEXT NOT NULL,
    TitleOfCourtesy TEXT NOT NULL,
    BirthDate DATE NOT NULL,
    HireDate DATE NOT NULL,
    Address TEXT NOT NULL,
    City TEXT NOT NULL,
    Region TEXT,
    PostalCode TEXT,
    Country TEXT NOT NULL,
    HomePhone TEXT NOT NULL,
    Extension TEXT,
    Photo BLOB,
    PhotoPath TEXT,
    Notes TEXT,
    ReportsTo INTEGER
);

-- 插入测试数据
INSERT INTO Employees (
    LastName, FirstName, Title, TitleOfCourtesy, 
    BirthDate, HireDate, Address, City, Country, HomePhone
) VALUES 
    ('Doe', 'John', 'Sales Manager', 'Mr.',
     '1985-06-15', '2010-03-10', '789 Office Park', 'San Francisco', 'USA', '111-222-3333'),
    ('Smith', 'Jane', 'HR Manager', 'Ms.',
     '1990-07-20', '2012-05-14', '456 HR Blvd', 'Chicago', 'USA', '555-666-7777');

-- Also add the special WEB employee that's required by the application
INSERT OR IGNORE INTO Employees (
    EmployeeID, LastName, FirstName, Title, TitleOfCourtesy,
    BirthDate, HireDate, Address, City, Country, HomePhone
) VALUES (
    999999, 'WEB', 'WEB', 'NULL', 'NULL',
    'NULL', 'NULL', 'NULL', 'NULL', 'NULL', 'NULL'
);

---------------------------------------------------------------

-- 创建 Orders 表
CREATE TABLE IF NOT EXISTS Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    CustomerID TEXT NOT NULL,
    EmployeeID INTEGER NOT NULL,
    OrderDate DATETIME NOT NULL,
    RequiredDate DATETIME NOT NULL,
    ShippedDate DATETIME,
    ShipVia INTEGER NOT NULL,
    Freight NUMERIC DEFAULT 0,
    ShipName TEXT NOT NULL,
    ShipAddress TEXT NOT NULL,
    ShipCity TEXT NOT NULL,
    ShipRegion TEXT,
    ShipPostalCode TEXT,
    ShipCountry TEXT NOT NULL,
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID),
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

-- 插入测试数据
INSERT INTO Orders (CustomerID, EmployeeID, OrderDate, RequiredDate, ShipVia, ShipName, ShipAddress, ShipCity, ShipCountry)
VALUES
    ('CUST1', 1, '2024-02-01', '2024-02-10', 1, 'Alice Johnson', '123 Tech St', 'New York', 'USA'),
    ('CUST2', 2, '2024-02-02', '2024-02-12', 2, 'Bob Smith', '456 Market Ave', 'Los Angeles', 'USA');

---------------------------------------------------------------

-- 创建 Products 表
CREATE TABLE IF NOT EXISTS Products (
    ProductID INTEGER PRIMARY KEY AUTOINCREMENT,
    ProductName TEXT NOT NULL,
    SupplierID INTEGER NOT NULL,
    CategoryID INTEGER NOT NULL,
    QuantityPerUnit TEXT NOT NULL,
    UnitPrice NUMERIC DEFAULT 0,
    UnitsInStock INTEGER DEFAULT 0,
    UnitsOnOrder INTEGER DEFAULT 0,
    ReorderLevel INTEGER DEFAULT 0,
    Discontinued TEXT DEFAULT '0'
);

-- 插入测试数据
INSERT INTO Products (ProductName, SupplierID, CategoryID, QuantityPerUnit, UnitPrice, UnitsInStock, Discontinued)
VALUES
    ('Wireless Mouse', 1, 1, '1 unit', 25.99, 100, '0'),
    ('Keyboard', 1, 1, '1 unit', 45.99, 50, '0');

---------------------------------------------------------------

-- 创建 Authentication 表
CREATE TABLE IF NOT EXISTS Authentication (
    UserID TEXT PRIMARY KEY,
    PasswordHash TEXT NOT NULL,
    SessionID TEXT NOT NULL
);

-- 插入测试数据
INSERT INTO Authentication (UserID, PasswordHash, SessionID)
VALUES
    ('testuser', 'hashedpassword123', 'session12345'),
    ('admin', 'securepass456', 'session67890');

---------------------------------------------------------------

-- 创建 Shopping_cart 表
CREATE TABLE IF NOT EXISTS Shopping_cart (
    ShopperID INTEGER NOT NULL,
    ProductID INTEGER NOT NULL,
    Quantity INTEGER DEFAULT 1,
    AddedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ShopperID, ProductID),
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID)
);

-- 插入测试数据
INSERT INTO Shopping_cart (ShopperID, ProductID, Quantity)
VALUES
    (1, 1, 2),
    (2, 2, 1);

