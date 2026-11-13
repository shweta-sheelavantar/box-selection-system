# AI-Assisted Box Selection System

A Django-based web application that automatically recommends the most suitable and cost-effective shipping box for customer orders containing multiple products.

The application considers product dimensions, quantities, total weight, box capacity, product rotation, and shipping box cost to identify a suitable packaging option.

## Project Overview

In e-commerce businesses, selecting the correct shipping box is important for reducing packaging costs and ensuring safe product transportation.

This project provides a simple solution that evaluates available shipping boxes and recommends the cheapest box that satisfies the order's weight and dimensional constraints.

**Note:** AI-assisted refers to the use of AI coding tools during development. The application itself uses a Python-based packing algorithm and does not contain a machine-learning model.

## Features

### Product Management

- Add and manage products.
- Store product dimensions and weight.
- Validate product information.

### Shipping Box Management

- Manage available shipping boxes.
- Store internal box dimensions.
- Define maximum weight capacity and box cost.

### Order Management

- Create orders containing multiple products.
- Select product quantities.
- Calculate total order weight.
- View order details.

### Intelligent Box Selection

- Calculate total product weight.
- Check shipping box weight capacity.
- Consider different product orientations.
- Check combined product dimensions using a packing heuristic.
- Compare suitable boxes based on cost.
- Recommend the cheapest suitable box.
- Display an explanation when no suitable box is available.

### Additional Features

- Responsive Bootstrap interface.
- Django Admin integration.
- Sample data management command.
- Automated Django tests.
- GitHub Actions workflow for automated testing.

## Technology Stack

| Technology      | Purpose                   |
| --------------- | ------------------------- |
| Python 3.12     | Programming language      |
| Django 6.1.3    | Backend web framework     |
| SQLite          | Database                  |
| Django ORM      | Database operations       |
| HTML5           | Page structure            |
| CSS3            | Styling                   |
| Bootstrap 5.3.3 | Responsive UI             |
| JavaScript      | Dynamic form interactions |
| Django TestCase | Automated testing         |
| GitHub Actions  | Continuous integration    |

## Project Structure

```text
box-selection-system/
│
├── box_selection/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── packaging/
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py
│   ├── templates/
│   │   └── packaging/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── create_order.html
│   │       └── order_result.html
│   ├── static/
│   ├── models.py
│   ├── admin.py
│   ├── forms.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── .github/
│   └── workflows/
│       └── tests.yml
│
├── manage.py
├── requirements.txt
├── README.md
├── AI_USAGE.md
└── .gitignore
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/shweta-sheelavantar/box-selection-system.git
cd box-selection-system
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```cmd
venv\Scripts\activate
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Load sample data

```bash
python manage.py seed_data
```

This command creates sample shipping boxes and products for testing the application.

### 7. Create an administrator account

```bash
python manage.py createsuperuser
```

### 8. Start the development server

```bash
python manage.py runserver
```

Open the following address in your browser:

[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Application Pages

| URL                   | Description                 |
| --------------------- | --------------------------- |
| `/`                   | Dashboard and recent orders |
| `/order/`             | Create a new order          |
| `/order/<id>/result/` | View box recommendation     |
| `/admin/`             | Django administration       |

## Box Selection Algorithm

The core selection logic is implemented separately from Django views in:

`packaging/services.py`

The algorithm follows these steps:

1. Retrieve all products and their quantities from an order.
2. Calculate the total weight of the order.
3. Sort available shipping boxes by cost.
4. Check whether each box can carry the total order weight.
5. Try different orientations of each product.
6. Check whether all products can fit using the implemented packing strategy.
7. Reject boxes that fail either the weight or dimensional check.
8. Recommend the cheapest box that passes both checks.
9. If no box is suitable, return a clear explanation.

### Packing Strategy and Limitations

The current implementation uses a conservative single-row packing heuristic.

It tries the six possible axis-aligned orientations of each rectangular product and selects an orientation that minimises the length required along the box's length.

The products are then arranged one after another along that length.

This approach checks more than total volume and does not approve a box based only on volume calculations.

**Known limitations:**

- Products are arranged in a single row along the box length.
- Layering and side-by-side arrangements are not supported.
- Empty spaces between products are not reused.
- Irregular product shapes and flexible packaging are not considered.
- The algorithm is a heuristic and does not guarantee an optimal 3D packing arrangement.

Therefore, some boxes that could accommodate an order using a more advanced 3D packing algorithm may be rejected by the current implementation.

## Sample Data

The application includes sample shipping boxes and products.

### Shipping Boxes

| Box    | Dimensions (cm) | Max Weight (kg) | Cost |
| ------ | --------------: | --------------: | ---: |
| Small  |    20 × 15 × 10 |               5 | 1.50 |
| Medium |    40 × 30 × 20 |              15 | 3.00 |
| Large  |    60 × 40 × 40 |              30 | 5.50 |

### Products

| Product    | Dimensions (cm) | Weight (kg) |
| ---------- | --------------: | ----------: |
| Phone Case |      16 × 8 × 2 |         0.2 |
| Book       |     24 × 17 × 4 |         0.8 |
| Shoes      |    32 × 22 × 12 |         1.2 |
| Laptop     |     36 × 25 × 3 |         2.0 |

### Example

**Order:** 2 Phone Cases

- Total weight: 0.4 kg.
- Small box: Cannot fit both products in the implemented single-row arrangement.
- Medium box: Can accommodate both products.
- Recommended box: Medium.
- Box cost: 3.00.

## Running Automated Tests

Run the Django test suite using:

```bash
python manage.py test packaging --verbosity=2
```

The test suite covers:

- Product and box models.
- Weight calculations.
- Product quantities.
- Product rotation.
- Dimensional constraints.
- Weight capacity validation.
- Cheapest suitable box selection.
- Orders with no suitable box.
- Empty orders.
- Django views and forms.
- Sample data command.

GitHub Actions is configured to run automated tests when changes are pushed to the repository.

## Documentation

| File             | Description                                |
| ---------------- | ------------------------------------------ |
| `README.md`      | Project overview and setup instructions    |
| `AI_USAGE.md`    | Record of AI tools and their contributions |
| `TEST_OUTPUT.md` | Actual automated test execution output     |
| `LEARNINGS.md`   | Personal learning reflection               |

The learning reflection and AI usage details should be completed based on actual development experience.

## Future Improvements

- Implement advanced 3D bin-packing algorithms.
- Support side-by-side and multi-layer product arrangements.
- Add packaging material and padding considerations.
- Improve packing visualisation.
- Support more complex product shapes.

##

GitHub: [https://github.com/shweta-sheelavantar](https://github.com/shweta-sheelavantar)

---

**Project:** AI-Assisted Box Selection System
**Purpose:** Python and Django hiring assignment
