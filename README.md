# AI-Assisted Box Selection System

A Django web application that recommends the cheapest available shipping box
for a customer order containing multiple products. Given product dimensions
and weights, the system finds the smallest-cost box whose internal dimensions
can fit all items and whose weight capacity is not exceeded.

---

## Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.12 | Language |
| Django | 6.1.3 | Web framework |
| SQLite | built-in | Database |
| Django ORM | — | All database operations |
| Bootstrap 5 | 5.3.3 (CDN) | UI styling |
| Django TestCase | — | Automated tests |

No machine learning libraries are used. The term "AI-assisted" refers to the
development process (AI coding assistant), not a model inside the application.

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd box_selection_system
```

### 2. Create and activate the virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Seed sample data

Loads 3 boxes (Small, Medium, Large) and 4 products (Phone Case, Book, Shoes, Laptop).
Safe to run multiple times — uses `get_or_create` so it never creates duplicates.

```bash
python manage.py seed_data
```

### 6. Create an admin superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

The application will be available at **http://127.0.0.1:8000/**

| URL | Page |
|---|---|
| http://127.0.0.1:8000/ | Home — recent orders |
| http://127.0.0.1:8000/order/ | Create a new order |
| http://127.0.0.1:8000/admin/ | Django admin panel |

### 8. Run the test suite

```bash
python manage.py test packaging --verbosity=2
```

Expected output: **35 tests, all passing.**

---

## How the Box Selection Algorithm Works

The algorithm lives in `packaging/services.py` in the function `select_box_for_order(order)`.

### Step-by-step

1. **Collect items** — read all `OrderItem` rows for the order. For each row, expand
   into individual product units (e.g. quantity=3 → 3 separate entries).

2. **Calculate total weight** — sum `product.weight × quantity` across all order lines.

3. **Evaluate boxes cheapest-first** — `Box.objects.all()` returns boxes ordered by `cost`
   ascending (set via `Meta.ordering`). The algorithm iterates this list and applies two checks
   to each box:

   **Check A — Weight capacity**
   ```
   if total_weight > box.max_weight → reject this box
   ```

   **Check B — Dimensional fit (single-row stacking with 6 orientations)**

   For each individual product unit, try all 6 axis-aligned orientations
   (all permutations of length × width × height). For each orientation, check
   whether the item fits within the box's cross-section (width and height).
   Among valid orientations, pick the one that uses the least length along
   the box's main axis. Stack all items end-to-end:

   ```
   total_length_used = sum of chosen lengths for each item
   fits = total_length_used <= box.length
   ```

4. **Return first passing box** — because boxes are evaluated cheapest-first,
   the first box that passes both checks is by definition the cheapest suitable one.
   The result (box, total weight, text reasoning) is saved back to the `Order` record.

5. **No box found** — if no box passes both checks, `recommended_box` is saved as
   `None` and the reasoning field explains which boxes were rejected and why.

### Example (from the assignment spec)

| Product | Dimensions | Weight |
|---|---|---|
| Laptop | 30 × 20 × 5 cm | 2.0 kg |
| Mouse | 10 × 6 × 4 cm | 0.2 kg |

Available boxes (cheapest first):

| Box | Dimensions | Max weight | Cost |
|---|---|---|---|
| Small | 35 × 25 × 10 cm | 5 kg | ₹20 |
| Medium | 40 × 30 × 15 cm | 10 kg | ₹30 |
| Large | 50 × 40 × 30 cm | 20 kg | ₹50 |

**Result:** Small box recommended.
- Total weight: 2.2 kg ≤ 5 kg ✓
- Dimensional fit: Laptop placed in its natural orientation uses 30 cm along the length axis
  (20 cm width and 5 cm height both fit within 25×10 cm cross-section). Mouse is rotated
  to 4×10×6 cm so it uses only 4 cm along the length axis (10 cm width and 6 cm height
  fit within 25×10 cm). Total length used: 30 + 4 = 34 cm ≤ 35 cm ✓

---

## Known Limitations of the Algorithm

The packing check is a **heuristic**, not an optimal 3D bin-packing solver.

- **Single-row assumption** — items are placed end-to-end along one axis only.
  It does not attempt to stack items in layers or arrange them side-by-side.
  This means some valid packings may be rejected — for example, two flat items
  placed side-by-side would be rejected if their combined widths exceed the box width,
  even though stacking one on top of the other might work.

- **No item interaction** — items are considered independently. The algorithm
  does not model items sharing space in 2D or 3D (e.g. fitting a small item
  in the gap beside a larger one).

- **Optimal 3D bin-packing is NP-hard** — a provably optimal solution for
  arbitrary sets of items requires exhaustive search or advanced heuristics
  (e.g. guillotine cutting, skyline algorithms). For the typical use case of
  a small number of products in an e-commerce order, the single-row heuristic
  is accurate and fast.

---

## Project Structure

```
box_selection_system/
│
├── manage.py                        # Django CLI entry point
├── requirements.txt                 # Pinned dependencies
├── README.md                        # This file
├── AI_USAGE.md                      # AI usage log (required by assignment)
├── .gitignore
│
├── .github/
│   └── workflows/
│       └── tests.yml                # GitHub Actions CI — runs test suite
│
├── box_selection/                   # Django project config package
│   ├── settings.py                  # All Django settings
│   ├── urls.py                      # Root URL router
│   ├── wsgi.py
│   └── asgi.py
│
└── packaging/                       # Main application
    ├── models.py                    # Box, Product, Order, OrderItem
    ├── services.py                  # Box selection algorithm
    ├── views.py                     # home, create_order, order_result
    ├── forms.py                     # OrderItemForm (used in formset)
    ├── urls.py                      # 3 URL patterns
    ├── admin.py                     # Admin registrations with ModelAdmin
    ├── tests.py                     # 35 tests (models, service, views)
    ├── migrations/
    │   └── 0001_initial.py
    ├── management/
    │   └── commands/
    │       └── seed_data.py         # `python manage.py seed_data`
    └── templates/
        └── packaging/
            ├── base.html            # Shared layout, Bootstrap 5, navbar
            ├── home.html            # Landing page, recent orders table
            ├── create_order.html    # Order form (formset + JS add/remove rows)
            └── order_result.html    # Recommendation result page
```
