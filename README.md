# AI-Assisted Box Selection System

A Django web application that recommends the **cheapest shipping box** for a customer order containing multiple products. Given each product's dimensions and weight, it finds the lowest-cost box that physically fits every item and can carry the total weight.

> "AI-assisted" refers to how the project was *built* (AI coding tools, documented in [AI_USAGE.md](AI_USAGE.md)). There is no machine-learning model inside the application.

## Screenshots

![Home page](docs/screenshots/home.png)
*Home page with recent orders.*

![Create order](docs/screenshots/create_order.png)
*Order form with dynamic product rows.*

![Result page](docs/screenshots/result.png)
*Recommendation result.*

## Features

- Multiple products per order, with a quantity for each
- Total weight calculation
- Weight-capacity check per box
- Dimensional fit check that tries all 6 axis-aligned orientations of each item
- Cheapest suitable box recommended, or a clear "no box found" message with reasons
- Dynamic order form (add/remove product rows) with server-side validation
- Django admin for managing boxes, products and orders
- Seed command for sample data
- Automated tests and a GitHub Actions workflow

## Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.12 | Language |
| Django | 6.1.3 | Web framework |
| SQLite | built-in | Database |
| Django ORM | – | All database access |
| Bootstrap | 5.3.3 (CDN) | UI styling |
| Django `TestCase` | – | Automated tests |

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
```

### 2. Create and activate a virtual environment

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

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Seed sample data (required)

`db.sqlite3` is not committed, so a fresh clone has no boxes or products and the product dropdown will be empty until you seed.

```bash
python manage.py seed_data
```

This loads 3 boxes and 4 products. It uses `get_or_create`, so it is safe to run more than once.

### 6. Create an admin user

```bash
python manage.py createsuperuser
```

### 7. Run the server

```bash
python manage.py runserver
```

| URL | Page |
|---|---|
| http://127.0.0.1:8000/ | Home, recent orders |
| http://127.0.0.1:8000/order/ | Create a new order |
| http://127.0.0.1:8000/order/`<pk>`/result/ | Recommendation for an order |
| http://127.0.0.1:8000/admin/ | Admin panel |

### 8. Run the tests

```bash
python manage.py test packaging --verbosity=2
```

All tests should pass. Test output is saved in [`test_output.txt`](test_output.txt), and CI runs the same command on every push (see Evidence below).

## Seed Data

| Box | L × W × H (cm) | Max weight (kg) | Cost |
|---|---|---|---|
| Small | 20 × 15 × 10 | 5 | 1.50 |
| Medium | 40 × 30 × 20 | 15 | 3.00 |
| Large | 60 × 40 × 40 | 30 | 5.50 |

| Product | L × W × H (cm) | Weight (kg) |
|---|---|---|
| Phone Case | 16 × 8 × 2 | 0.2 |
| Book | 24 × 17 × 4 | 0.8 |
| Shoes | 32 × 22 × 12 | 1.2 |
| Laptop | 36 × 25 × 3 | 2.0 |

(Source of truth: `packaging/management/commands/seed_data.py`. Keep this table in sync with it.)

## How the Algorithm Works

The logic is in `packaging/services.py`, function `select_box_for_order(order)`.

1. **Collect items.** Each `OrderItem` is expanded into individual units (quantity 3 becomes 3 units).
2. **Total weight.** Sum of `product.weight × quantity` across all lines.
3. **Evaluate boxes cheapest first.** `Box.Meta.ordering` sorts by cost ascending, so the first box that passes is the cheapest valid one. Each box gets two checks:
   - **Weight check:** reject the box if `total_weight > box.max_weight`.
   - **Fit check (single-row stacking):** for each unit, try all 6 orientations (`itertools.permutations` of its three dimensions). Keep orientations whose other two dimensions fit the box's width and height, and choose the one using the least length. Stack all units end to end:

     ```
     total_length_used = sum(chosen length of each unit)
     fits = total_length_used <= box.length
     ```
4. **Return the first box that passes both checks.** The box, total weight and a text explanation are saved on the `Order`.
5. **No box found.** `recommended_box` is saved as `None`, and the reasoning explains why each box was rejected.

### Worked examples (using the seed data)

**2 × Phone Case → Medium box.** Total weight 0.4 kg. In the Small box each case needs at least 16 cm of length, so two need 32 cm, which is more than 20 cm. The Medium box has 40 cm of length, so 32 cm fits. Cost 3.00.

**1 × Phone Case → Small box.** Total weight 0.2 kg. One case uses 16 cm of the Small box's 20 cm length. Cost 1.50.

**50 × Laptop → no box.** Total weight 100 kg exceeds every box's capacity, so the result page shows "No suitable box" with the reasons.

## Known Limitations

The fit check is a **heuristic**, not an optimal 3D bin-packing solver.

- **Conservative by design.** Items are placed in one row along the box length only. The algorithm can wrongly report "no box fits" for an order that could be packed by layering or placing items side by side. It cannot approve a packing that doesn't physically fit, because it only accepts when the stacked lengths fit.
- **No shared space.** Items are not modelled as nesting in gaps beside larger items.
- **Optimal packing is NP-hard.** Exact solutions need exhaustive search or advanced heuristics. For typical e-commerce orders with a few items, a simple conservative check is fast and predictable.
- **Rigid items only.** No padding, rounding or tolerance is applied, and items are treated as axis-aligned boxes.

## Design Decisions

- `DecimalField` for dimensions, weight and cost, so there are no floating-point rounding surprises.
- `Order.recommended_box` uses `on_delete=SET_NULL`, so deleting a box keeps historical orders.
- `OrderItem` is a custom through-model so each order line stores a quantity.
- POST/Redirect/GET after submitting an order, so refreshing the result page never resubmits the form.
- Service-layer logic (`services.py`) is separate from views, so the algorithm is easy to test.

## Project Structure

```
.
├── manage.py
├── requirements.txt
├── README.md
├── AI_USAGE.md
├── test_output.txt
├── .gitignore
├── .github/workflows/tests.yml        # CI: runs the test suite
├── box_selection/                     # Project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── packaging/                         # Main app
    ├── models.py                      # Box, Product, Order, OrderItem
    ├── services.py                    # Box selection algorithm
    ├── views.py                       # home, create_order, order_result
    ├── forms.py                       # OrderItemForm (used in a formset)
    ├── urls.py
    ├── admin.py
    ├── tests.py
    ├── migrations/
    ├── management/commands/seed_data.py
    ├── static/packaging/style.css     # (if present after the UI redesign)
    └── templates/packaging/
        ├── base.html
        ├── home.html
        ├── create_order.html
        └── order_result.html
```

## Testing

Tests use Django's `TestCase`, so each test runs in a rolled-back transaction against a temporary test database and never touches `db.sqlite3`. Coverage:

- Models: `__str__`, `volume()`, default ordering, `line_weight()`
- Service: example order, weight too heavy, dimension too large, rotation, quantity multiplication, empty order, no inventory, cheapest box chosen, result persisted
- Views: home, create order (GET, valid POST, invalid POST, empty-state warning), order result (including 404)
- `seed_data` command: creates rows, idempotent

> Passing tests did not initially mean a usable app: the tests created their own data, while the real database was unseeded and the dropdown was empty. That is why `seed_data` exists and why setup step 5 is required. See [AI_USAGE.md](AI_USAGE.md).

## Evidence and Submission Files

| Item | Link |
|---|---|
| GitHub Actions test run | `PASTE-ACTIONS-RUN-URL` |
| Test run output | [test_output.txt](test_output.txt) |
| AI usage log | [AI_USAGE.md](AI_USAGE.md) |
| Chat transcript | [docs/chat_transcript.md](docs/chat_transcript.md) |
| What I learned | [LEARNINGS.md](LEARNINGS.md) |

## What I Learned

I revised Python basics and OOP concepts.
I revised Django models, views, URLs and templates.
I understood how Django connects with a database.
I practised creating a project and Django application.
I learned how to test and debug errors.
