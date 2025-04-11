# Apartment Rental Management System

This project implements a relational database system to support apartment rental management for 270 Holding, LLC. It handles tenants, apartments, leases, monthly rent billing, and payments.

---

## Project Summary

The goal of this project is to build a database-backed system that simplifies the workflow of sending bills, recording payments, and generating tenant balance records. José, the manager, had been using spreadsheets manually, which was error-prone and hard to maintain. This database model supports automation and data integrity.

---

## Entity-Relationship (ER) Model

### Main Entities:
- **Apartment**
- **Tenant**
- **Lease**
- **Bill**
- **Payment**

### Relationships:
- One Apartment → 0 or more Leases
- One Tenant → 1 or more Leases
- One Lease → 0 or more Bills
- One Bill → 0 or more Payments

---

## Design Narrative: From E-R Model to Relational Schema

### Phase 1: Understanding the Domain

I started by analyzing the user's needs and carefully extracting the core entities and relationships. The real-world context involves managing apartment rentals, leases, rent bills, and payments — all linked through tenants and units. Based on this, I identified five main entities: `Apartment`, `Tenant`, `Lease`, `Bill`, and `Payment`.

### Phase 2: Initial E-R Modeling

I created an E-R diagram with the following key relationships:
- One **Apartment** can be associated with many **Leases** over time.
- One **Tenant** can sign multiple **Leases**.
- Each **Lease** can have many **Bills**.
- Each **Bill** can be paid via multiple **Payments**.

### Phase 3: Problems Encountered and Resolutions

#### Problem 1: Ambiguity in `other_charges` Structure

**What I encountered:**  
The application needs to support flexible, itemized charges beyond rent — such as utility fees, repairs, or penalties. At first, I considered creating a separate table like `OtherCharge(bill_id, type, amount)` to represent each item as its own row.

However, this introduced unnecessary complexity for the current use case. Each charge is only ever used within a single bill and not reused or queried independently. It also would have required multiple joins to render a single billing page.

**How I resolved it:**  
I decided to represent `other_charges` as a `JSON` column in the `Bill` table, using key-value pairs to hold charge names and amounts. For example:

```json
{
  "utilities": 75.00,
  "repair": 120.00,
  "late_fee": 50.00
}
```

This allowed me to store structured, flexible information without breaking normalization, and kept the schema simpler and easier to work with from the frontend.

**Why this worked:**  
MySQL supports native JSON fields, so this approach preserved atomicity and allowed efficient queries when necessary. It also matched the front-end behavior, where the manager manually inputs custom charge items.

---

#### Problem 2: First Bill Has No Prior Balance

**What I encountered:**  
To compute a bill's `total_amount`, I use the formula:

```
total = rent + other_charges - balance
```

The `balance` is calculated based on payments made minus the total due from all previous bills. However, for a tenant's **first bill**, no prior bill exists, which caused calculation errors or unexpected results.

**How I resolved it:**  
I implemented a special case in the backend:  
If no prior bill exists for the lease, the system assumes `balance = 0` by default. This logic is enforced in the application code when generating a bill.

**Why this worked:**  
This approach allowed first-time tenants to receive accurate bills without forcing manual corrections. It reflects the real-world expectation that tenants begin with no outstanding balance unless otherwise recorded.

---

#### Problem 3: Redundancy Between `Lease` and `Payment`

**What I encountered:**  
Initially, the `Payment` table included both `lease_id` and `bill_id` as foreign keys. My thought was to allow direct access to both levels of information when querying payments.

But I realized this creates **data redundancy** and opens the door to **inconsistency**, such as a payment referencing a `lease_id` that does not match its associated `bill_id`.

**How I resolved it:**  
I removed the `lease_id` column from the `Payment` table and kept only the `bill_id` foreign key. Through a join (`Payment → Bill → Lease`), the lease and tenant details can still be retrieved as needed.

**Why this worked:**  
This improved normalization (satisfying 3NF) by removing transitive dependencies. It also eliminated the risk of data mismatch between `bill_id` and `lease_id`, simplifying data integrity checks.

---

### Phase 4: Functional Dependencies

Before normalization, We identified the following functional dependencies based on the real-world meaning of each entity:

- **Apartment.id → unit_number, unit_size, ownership_type, is_special**  
  (Each apartment has a unique ID and fixed attributes)

- **Tenant.id → first_name, last_name, full_name, email**  
  (Each tenant's ID determines their name and email)

- **Lease.id → tenant_id, apartment_id, start_date, end_date, monthly_rent**  
  (Each lease uniquely determines which tenant leases which apartment and at what price)

- **Bill.id → lease_id, billing_month, rent_amount, other_charges, balance_used, total_amount, sent_at**  
  (Each bill is uniquely defined by its ID, and includes amounts and metadata)

- **Payment.id → bill_id, amount, payment_date, check_number, remitter_name**  
  (Each payment uniquely determines all details of that payment)

These functional dependencies guided my decisions in the normalization process, ensuring each attribute is placed in the appropriate table and avoids partial or transitive dependencies.

---

### Phase 5: Normalization by Relation

We normalized each relation individually based on the functional dependencies previously outlined. All five relations satisfy **Third Normal Form (3NF)**. Below, we explain how each relation meets 1NF, 2NF, and 3NF requirements, and describe the specific considerations and design choices made to support those forms.

---

#### Apartment (3NF)
This relation satisfies Third Normal Form (3NF), meaning it also satisfies 1NF and 2NF.
**Relation:**  
`Apartment(*id*, unit_number, unit_size, ownership_type, is_special)`

- **1NF:** We ensured all attributes are atomic and indivisible. For instance, `ownership_type` is a single categorical value rather than a composite or list. We chose to use an enumerated type (`ENUM`) to enforce valid values without violating atomicity.

- **2NF:** All non-key attributes (`unit_number`, `unit_size`, `ownership_type`, `is_special`) fully depend on the primary key `id`. Since `id` is the only key, there is no risk of partial dependency. We deliberately avoided composite keys to simplify integrity enforcement and ensure clarity in joins and queries.

- **3NF:** There are no transitive dependencies among non-key attributes. Each attribute directly describes the apartment and does not rely on another non-key field. We decided not to include building-level or address-level information here, to prevent future transitive dependencies in case of multi-building support.

---

#### Tenant (3NF)
This relation satisfies Third Normal Form (3NF), meaning it also satisfies 1NF and 2NF.
**Relation:**  
`Tenant(*id*, first_name, last_name, full_name, email)`

- **1NF:** We stored only atomic values in each field. For example, `email` contains only a single email address, and we avoided multi-valued fields such as "preferred emails." We considered normalizing `first_name` and `last_name` into a `Name` entity, but decided to retain simplicity since names are rarely reused or updated in isolation.

- **2NF:** All non-key attributes depend entirely on `id`, which is the sole primary key. We verified that `email`, `full_name`, and name fields are unique to the tenant and do not rely on any part of a composite key. We chose to store `full_name` as a separate field rather than computing it dynamically, due to the need for displaying custom name formats in billing output.

- **3NF:** There are no transitive dependencies. For example, `email` does not depend on `full_name`, and vice versa. We intentionally did not include derived information such as account status or login credentials, as those belong in a separate authentication module. This decision prevents the need to update multiple records when contact information changes.

---

#### Lease (3NF)
This relation satisfies Third Normal Form (3NF), meaning it also satisfies 1NF and 2NF.
**Relation:**  
`Lease(*id*, tenant_id, apartment_id, start_date, end_date, monthly_rent)`

- **1NF:** Each attribute is atomic and non-repeating. For example, `monthly_rent` stores a fixed numeric value, not a formula or list. We considered storing an array of rent history but decided instead to represent each contract period as a distinct `Lease` record to maintain 1NF and support time-based billing logic.

- **2NF:** All non-key attributes fully depend on `id`, the primary key. We explicitly chose a surrogate key (`id`) to simplify foreign key references from `Bill` and `Payment`. This ensures that values like `monthly_rent` are tied directly to a lease, not partially to a tenant or apartment.

- **3NF:** We excluded tenant or apartment details from this table to avoid transitive dependencies. For example, `tenant_email` or `unit_number` can be accessed via joins and should not be redundantly stored here. This decision simplifies updates and reduces the risk of inconsistency when external details change.

---

#### Bill (3NF)
This relation satisfies Third Normal Form (3NF), meaning it also satisfies 1NF and 2NF.
**Relation:**  
`Bill(*id*, lease_id, billing_month, rent_amount, other_charges, balance_used, total_amount, sent_at)`

- **1NF:** All fields are atomic. We used a JSON object for `other_charges`, which stores key-value pairs such as `"repair": 100`. While JSON fields might appear non-atomic, each key and value is interpreted as a distinct charge type and amount. We considered creating a separate `ChargeItem` table but decided against it due to minimal reuse and to streamline frontend integration.

- **2NF:** Every attribute depends entirely on `id`, the primary key. Fields such as `rent_amount`, `balance_used`, and `total_amount` relate to the unique billing instance, not partially to `lease_id` or `billing_month`. We ensured that derived fields like `total_amount` are computed and stored for reference consistency, rather than recalculated dynamically, in order to support audit and reporting requirements.

- **3NF:** We avoided storing tenant or apartment data in this table to eliminate transitive dependencies. For example, although it might seem convenient to include `tenant_name`, we intentionally excluded it to avoid inconsistency if a tenant’s name changes. All such data can be accessed via the `lease_id` foreign key.

---

#### Payment (3NF)
This relation satisfies Third Normal Form (3NF), meaning it also satisfies 1NF and 2NF.
**Relation:**  
`Payment(*id*, bill_id, amount, payment_date, check_number, remitter_name)`

- **1NF:** All fields are atomic, with no repeating groups. For instance, if a payment covers multiple charges, it is recorded as a single `amount`, and breakdowns are handled externally if needed. We explicitly disallowed multiple bill references per payment to preserve atomicity and simplify reconciliation.

- **2NF:** All non-key attributes depend on the primary key `id`. Initially, we considered using a composite key involving `bill_id` and `check_number`, but opted for a surrogate `id` to simplify referencing from receipt and audit systems.

- **3NF:** We avoided transitive dependencies by removing `lease_id` from this table. Since `bill_id` already links to a `Lease`, storing both would create a dependency chain (`bill_id → lease_id → ...`) that violates 3NF. This design choice also reduces the risk of foreign key mismatches and enforces single-source truth for bill-to-lease relationships.

---

### Summary

For each table, we applied normalization principles to remove redundancy, preserve data integrity, and ensure maintainability. The normalization process was guided by the functional dependencies identified earlier and the operational needs of the billing system. Every relation was verified to satisfy **1NF, 2NF, and 3NF**, and key design decisions were made to balance normalization with practicality in query performance and application logic.
---


---

### Final Thoughts

By applying normalization, I reduced redundancy, preserved data consistency, and ensured the database would scale gracefully. My final schema is modular, cleanly decomposed, and accurately reflects both the functional structure of the business and the theoretical goals of relational design.