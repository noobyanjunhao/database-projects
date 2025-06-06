INSERT INTO Apartment (unit_number, unit_size, ownership_type, is_special) VALUES
('1A',  900, 'sold', 0),   ('1B',  880, 'sold', 0),   ('1C',  860, 'sold', 0),
('1D',  930, 'sold', 0),   ('1E',  910, 'sold', 0),
('2A',  905, 'sold', 0),   ('2B',  875, 'sold', 0),   ('2C',  845, 'sold', 0),
('2D',  920, 'sold', 0),   ('2E',  890, 'sold', 0),
('3A',  915, 'sold', 0),   ('3B',  885, 'sold', 0),   ('3C',  855, 'sold', 0),
('3D',  925, 'sold', 0),   ('3E',  895, 'sold', 0),
('4A',  920, 'sold', 0),   ('4B',  900, 'sold', 0),   ('4C',  870, 'sold', 0),
('4D',  940, 'sold', 0),   ('4E',  910, 'sold', 0),
('5A',  930, 'sold', 0),   ('5B',  900, 'sold', 0),   ('5C',  870, 'sold', 0),
('5D',  950, 'sold', 0),   ('5E',  920, 'sold', 0),
('6A',  935, 'sold', 0),   ('6B',  905, 'sold', 0),   ('6C',  875, 'sold', 0),
('6D',  945, 'rent_controlled', 1),  -- ★ special
('6E',  915, 'rent_controlled', 0),
('7A',  925, 'rent_controlled', 1),  -- ★ special
('7B',  895, 'rent_controlled', 0),
('7C',  865, 'rent_controlled', 1),  -- ★ special
('7D',  935, 'rent_controlled', 0),
('7E',  905, 'rent_controlled', 1),  -- ★ special
('8A',  915, 'rent_controlled', 0),
('8B',  885, 'rent_controlled', 0),
('8C',  855, 'rent_controlled', 1),  -- ★ special
('8D',  925, 'rent_controlled', 0),
('8E',  895, 'rent_controlled', 0),
('9A',  930, 'rent_controlled', 0),
('9B',  900, 'rent_controlled', 0),
('9C',  870, 'rent_stabilized', 0),
('9D',  940, 'rent_stabilized', 1),  -- ★ special
('9E',  910, 'rent_stabilized', 0),
('10A', 920, 'rent_stabilized', 1),  -- ★ special
('10B', 890, 'rent_stabilized', 0),
('10C', 860, 'rent_stabilized', 1),  -- ★ special
('10D', 930, 'rent_stabilized', 0),
('10E', 900, 'rent_stabilized', 0),
('11B', 875, 'rent_stabilized', 0),
('11C', 845, 'rent_stabilized', 0),
('11D', 915, 'rent_stabilized', 0),
('11E', 885, 'rent_stabilized', 0),
('11A', 1000, 'market', 0);

INSERT INTO Tenant (full_name, email) VALUES
('Alice Wong',      'alice@example.com'),
('Bob Smith',       'bob@example.com'),
('Charlie Zhang',   'charlie@example.com'),
('Dana Kim',        'dana@example.com'),
('Eve Lopez',       'eve@example.com'),
('Frank Johnson',   'frank@example.com'),
('Grace Lee',       'grace@example.com'),
('Henry Miller',    'henry@example.com'),
('Ivy Davis',       'ivy@example.com'),
('Jack Wilson',     'jack@example.com'),
('Karen Brown',     'karen@example.com'),
('Leo Garcia',      'leo@example.com'),
('Mia Martinez',    'mia@example.com'),
('Nate Clark',      'nate@example.com'),
('Olivia Lewis',    'olivia@example.com'),
('Peter Walker',    'peter@example.com'),
('Queen Young',     'queen@example.com'),
('Ryan Hall',       'ryan@example.com'),
('Sophie Allen',    'sophie@example.com'),
('Tom Wright',      'tom@example.com'),
('Uma King',        'uma@example.com'),
('Victor Scott',    'victor@example.com'),
('Wendy Green',     'wendy@example.com'),
('Xavier Adams',    'xavier@example.com'),
('Yara Baker',      'yara@example.com'),
('Zack Rivera',     'zack@example.com'),
('Harper Price',    'harper@example.com'),
('Sold Tenant 1',   'sold1@example.com'),
('Sold Tenant 2',   'sold2@example.com'),
('Sold Tenant 3',   'sold3@example.com'),
('Sold Tenant 4',   'sold4@example.com'),
('Sold Tenant 5',   'sold5@example.com'),
('Sold Tenant 6',   'sold6@example.com'),
('Sold Tenant 7',   'sold7@example.com'),
('Sold Tenant 8',   'sold8@example.com'),
('Sold Tenant 9',   'sold9@example.com'),
('Sold Tenant 10',  'sold10@example.com'),
('Sold Tenant 11',  'sold11@example.com'),
('Sold Tenant 12',  'sold12@example.com'),
('Sold Tenant 13',  'sold13@example.com'),
('Sold Tenant 14',  'sold14@example.com'),
('Sold Tenant 15',  'sold15@example.com'),
('Sold Tenant 16',  'sold16@example.com'),
('Sold Tenant 17',  'sold17@example.com'),
('Sold Tenant 18',  'sold18@example.com'),
('Sold Tenant 19',  'sold19@example.com'),
('Sold Tenant 20',  'sold20@example.com'),
('Sold Tenant 21',  'sold21@example.com'),
('Sold Tenant 22',  'sold22@example.com'),
('Sold Tenant 23',  'sold23@example.com'),
('Sold Tenant 24',  'sold24@example.com'),
('Sold Tenant 25',  'sold25@example.com'),
('Sold Tenant 26',  'sold26@example.com'),
('Sold Tenant 27',  'sold27@example.com'),
('Sold Tenant 28',  'sold28@example.com');

INSERT INTO Lease (tenant_id, apartment_id, start_date, end_date, monthly_rent) VALUES
( 1,  29, '2024-01-01', '2025-01-01',      0.00),
( 2,  30, '2023-11-01', '2024-11-01',   1150.00),
( 3,  31, '2024-02-15', '2025-02-15',      0.00),
( 4,  32, '2023-09-01', '2024-09-01', 1180.00),
( 5,  33, '2023-06-01', '2024-06-01',      0.00),
( 6,  34, '2024-03-10', '2025-03-10',   1225.00),
( 7,  35, '2022-05-01', '2023-05-01',      0.00),
( 8,  36, '2023-10-01', '2024-10-01',   1195.00),
( 9,  37, '2021-01-01', '2022-01-01',      0.00),
(10,  38, '2024-04-01', '2025-04-01',   0.00),
(11,  39, '2023-12-01', '2024-12-01',   1175.00),
(12,  40, '2024-05-01', '2025-05-01',   1160.00),
(13,  41, '2023-08-15', '2024-08-15',   1185.00),
(14,  42, '2024-02-01', '2025-02-01',   1155.00),
(15,  43, '2023-07-01', '2024-07-01',   1420.00),
(16,  44, '2022-11-01', '2023-11-01',      0.00),
(17,  45, '2024-01-10', '2025-01-10',   1435.00),
(18,  46, '2023-03-01', '2024-03-01',      0.00),
(19,  47, '2023-05-01', '2024-05-01',   1450.00),
(20,  48, '2021-12-01', '2022-12-01',      0.00),
(21,  49, '2024-06-01', '2025-06-01',   1440.00),
(22,  50, '2023-09-01', '2024-09-01',   1410.00),
(23,  51, '2024-03-25', '2025-03-25',   1425.00),
(24,  52, '2022-04-15', '2023-04-15',   1430.00),
(25,  53, '2024-05-05', '2025-05-05',   1400.00),
(26,  55, '2024-02-01', '2025-02-01',   2800.00),
(27,  54, '2023-10-01', '2024-10-01',   1460.00),
(28,   1, NULL, NULL, NULL),
(29,   2, NULL, NULL, NULL),
(30,   3, NULL, NULL, NULL),
(31,   4, NULL, NULL, NULL),
(32,   5, NULL, NULL, NULL),
(33,   6, NULL, NULL, NULL),
(34,   7, NULL, NULL, NULL),
(35,   8, NULL, NULL, NULL),
(36,   9, NULL, NULL, NULL),
(37,  10, NULL, NULL, NULL),
(38,  11, NULL, NULL, NULL),
(39,  12, NULL, NULL, NULL),
(40,  13, NULL, NULL, NULL),
(41,  14, NULL, NULL, NULL),
(42,  15, NULL, NULL, NULL),
(43,  16, NULL, NULL, NULL),
(44,  17, NULL, NULL, NULL),
(45,  18, NULL, NULL, NULL),
(46,  19, NULL, NULL, NULL),
(47,  20, NULL, NULL, NULL),
(48,  21, NULL, NULL, NULL),
(49,  22, NULL, NULL, NULL),
(50,  23, NULL, NULL, NULL),
(51,  24, NULL, NULL, NULL),
(52,  25, NULL, NULL, NULL),
(53,  26, NULL, NULL, NULL),
(54,  27, NULL, NULL, NULL),
(55,  28, NULL, NULL, NULL);
