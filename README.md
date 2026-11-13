# AI-Assisted Box Selection System

A Django-based web application that recommends the most suitable and lowest-cost shipping box for a customer order.

The system considers product dimensions, weight, quantity, box dimensions and maximum weight capacity to find a suitable shipping box.

**Note:** AI-assisted refers to the development process using AI coding tools. The application itself does not use a machine learning model.

## Features

- Add and manage products.
- Add and manage shipping boxes.
- Create orders with multiple products.
- Specify product quantities.
- Calculate the total order weight.
- Check box dimensions and weight capacity.
- Try different product orientations to improve fitting.
- Recommend the cheapest suitable box.
- Display a message when no suitable box is available.
- Manage products, boxes and orders through Django Admin.
- Automated test cases for important functionality.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.12 | Programming language |
| Django 6.1.3 | Backend framework |
| SQLite | Database |
| HTML and CSS | Frontend |
| Bootstrap 5.3.3 | UI design |
| Django ORM | Database operations |
| Django TestCase | Automated testing |
| Git and GitHub | Version control |

## Project Setup

### 1. Clone the repository

```bash
git clone https://github.com/shweta-sheelavantar/box-selection-system.git
cd box-selection-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

For macOS/Linux:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Add sample data

```bash
python manage.py seed_data
```

This command adds sample products and shipping boxes to the database. It can be run multiple times without creating duplicate sample records.

### 6. Create an admin account

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open the application:

http://127.0.0.1:8000/

## Application URLs

| URL | Description |
|---|---|
| `/` | Home page and recent orders |
| `/order/` | Create a new order |
| `/order/<pk>/result/` | View box recommendation |
| `/admin/` | Django administration |

## Sample Data

The following sample data is used for testing.

### Shipping Boxes

| Box | Dimensions (L × W × H) | Max Weight | Cost |
|---|---|---|---|
| Small | 20 × 15 × 10 cm | 5 kg | ₹1.50 |
| Medium | 40 × 30 × 20 cm | 15 kg | ₹3.00 |
| Large | 60 × 40 × 40 cm | 30 kg | ₹5.50 |

### Products

| Product | Dimensions (L × W × H) | Weight |
|---|---|---|
| Phone Case | 16 × 8 × 2 cm | 0.2 kg |
| Book | 24 × 17 × 4 cm | 0.8 kg |
| Shoes | 32 × 22 × 12 cm | 1.2 kg |
| Laptop | 36 × 25 × 3 cm | 2.0 kg |

## Box Selection Algorithm

The box selection logic is implemented in:

`packaging/services.py`

The main function is:

`select_box_for_order(order)`

The algorithm follows these steps:

1. Collect all products and their quantities from the order.
2. Calculate the total weight of the order.
3. Sort available boxes by cost, from lowest to highest.
4. Check whether the total weight is within the box's maximum capacity.
5. Try different orientations of each product to check whether it fits.
6. Use a single-row stacking approach along the length of the box.
7. Select the cheapest box that passes both dimension and weight checks.
8. If no box is suitable, display a message explaining why the boxes were rejected.

### Example

Suppose a customer orders two phone cases.

- Total weight: 0.4 kg.
- Each phone case requires 16 cm of box length in the selected orientation.
- Total required length: 32 cm.
- Small box length: 20 cm.
- Medium box length: 40 cm.

The Small box cannot accommodate both products using this packing strategy.

Therefore, the Medium box is recommended at a cost of ₹3.00.

## Testing

The project uses Django TestCase to test application functionality.

The test cases cover:

- Product and box models.
- Weight capacity checking.
- Product dimension checking.
- Product rotation.
- Multiple products and quantities.
- Empty orders.
- No suitable box scenarios.
- Cheapest suitable box selection.
- Order creation and result pages.
- Sample data management.

Run the tests using:

```bash
python manage.py test packaging --verbosity=2
```

The actual test execution output is available in `TEST_OUTPUT.md`.

## Known Limitations

- The current algorithm uses a single-row stacking approach.
- Products are placed along the length of the box.
- It does not support complex 3D packing or placing products side by side.
- It does not consider protective packaging or padding.
- It uses a heuristic approach rather than an optimal 3D bin-packing algorithm.

## Project Structure

```text
box-selection-system/
│
├── box_selection/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── packaging/
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py
│   ├── templates/
│   ├── static/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── services.py
│   ├── admin.py
│   ├── urls.py
│   └── tests.py
│
├── docs/
│   └── chat_transcript.pdf
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── manage.py
├── requirements.txt
├── README.md
├── AI_USAGE.md
├── LEARNINGS.md
├── TEST_CASES.md
└── TEST_OUTPUT.md
```

## AI Usage

AI tools were used during development for understanding requirements, discussing implementation approaches, debugging and improving code.

Details of the tools, prompts, accepted suggestions, rejected suggestions and verification steps are documented in [AI_USAGE.md](AI_USAGE.md).

## Learning Outcomes

During this assignment, I revised Python and Django concepts and applied them in a practical project.

I also learned about Django database models, relationships, form handling, business logic, testing and debugging.

My detailed learning experience is documented in [LEARNINGS.md](LEARNINGS.md).

## Assignment Deliverables

- GitHub Repository: [Box Selection System](https://github.com/shweta-sheelavantar/box-selection-system)
- [AI Usage Documentation](AI_USAGE.md)
- [Learning Outcomes](LEARNINGS.md)
- [Test Cases](TEST_CASES.md)
- [Test Output](TEST_OUTPUT.md)
- Chat Transcript: `docs/chat_transcript.pdf`

