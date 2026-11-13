"""
Test suite for the AI-Assisted Box Selection System.

Covers three layers:
  1. Model unit tests  — __str__, volume(), line_weight()
  2. Service tests     — box selection algorithm scenarios
  3. View tests        — HTTP status codes and template rendering
"""

from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal

from .models import Box, Product, Order, OrderItem
from .services import select_box_for_order, run_selection_and_save


# ---------------------------------------------------------------------------
# Helpers — reusable fixtures
# ---------------------------------------------------------------------------

def make_boxes():
    """Create the three boxes from the assignment spec."""
    small  = Box.objects.create(name='Small',  length=35, width=25, height=10, max_weight=5,  cost=20)
    medium = Box.objects.create(name='Medium', length=40, width=30, height=15, max_weight=10, cost=30)
    large  = Box.objects.create(name='Large',  length=50, width=40, height=30, max_weight=20, cost=50)
    return small, medium, large


def make_products():
    """Create the two products from the assignment spec."""
    laptop = Product.objects.create(name='Laptop', length=30, width=20, height=5,  weight=2.0)
    mouse  = Product.objects.create(name='Mouse',  length=10, width=6,  height=4,  weight=0.2)
    return laptop, mouse


def make_order(*product_qty_pairs):
    """
    Create an Order with the given (product, quantity) pairs.
    Usage: make_order((laptop, 1), (mouse, 1))
    """
    order = Order.objects.create()
    for product, qty in product_qty_pairs:
        OrderItem.objects.create(order=order, product=product, quantity=qty)
    return order


# ---------------------------------------------------------------------------
# 1. Model tests
# ---------------------------------------------------------------------------

class BoxModelTest(TestCase):

    def setUp(self):
        self.box = Box.objects.create(
            name='Small', length=35, width=25, height=10,
            max_weight=5, cost=20
        )

    def test_str_representation(self):
        """__str__ should include the name and all three dimensions."""
        result = str(self.box)
        self.assertIn('Small', result)
        self.assertIn('35', result)
        self.assertIn('25', result)
        self.assertIn('10', result)

    def test_volume_calculation(self):
        """volume() should return length × width × height."""
        expected = Decimal('35') * Decimal('25') * Decimal('10')
        self.assertEqual(self.box.volume(), expected)

    def test_ordering_by_cost(self):
        """Boxes should be returned cheapest-first by default."""
        Box.objects.create(name='Large',  length=50, width=40, height=30, max_weight=20, cost=50)
        Box.objects.create(name='Medium', length=40, width=30, height=15, max_weight=10, cost=30)
        names = list(Box.objects.values_list('name', flat=True))
        self.assertEqual(names, ['Small', 'Medium', 'Large'])


class ProductModelTest(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name='Laptop', length=30, width=20, height=5, weight=2.0
        )

    def test_str_representation(self):
        result = str(self.product)
        self.assertIn('Laptop', result)
        self.assertIn('30', result)
        self.assertIn('2', result)

    def test_volume_calculation(self):
        expected = Decimal('30') * Decimal('20') * Decimal('5')
        self.assertEqual(self.product.volume(), expected)


class OrderItemModelTest(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name='Mouse', length=10, width=6, height=4, weight=Decimal('0.2')
        )
        self.order = Order.objects.create()
        self.item = OrderItem.objects.create(
            order=self.order, product=self.product, quantity=3
        )

    def test_line_weight(self):
        """line_weight() should return product.weight × quantity."""
        expected = Decimal('0.2') * 3
        self.assertEqual(self.item.line_weight(), expected)

    def test_str_representation(self):
        result = str(self.item)
        self.assertIn('3', result)
        self.assertIn('Mouse', result)


# ---------------------------------------------------------------------------
# 2. Service / algorithm tests
# ---------------------------------------------------------------------------

class BoxSelectionServiceTest(TestCase):
    """
    Tests for select_box_for_order() covering all key scenarios.
    Each test creates its own data so tests are fully isolated.
    """

    # --- Assignment spec scenario -------------------------------------------

    def test_assignment_example_recommends_small_box(self):
        """
        Laptop (30×20×5 cm, 2 kg) + Mouse (10×6×4 cm, 0.2 kg)
        should be recommended the Small box — cheapest box that fits.
        """
        small, medium, large = make_boxes()
        laptop, mouse = make_products()
        order = make_order((laptop, 1), (mouse, 1))

        box, total_weight, reasoning = select_box_for_order(order)

        self.assertIsNotNone(box, "Expected a box to be found.")
        self.assertEqual(box.name, 'Small')
        self.assertEqual(total_weight, Decimal('2.2'))
        self.assertIn('Small', reasoning)

    # --- Weight scenarios ----------------------------------------------------

    def test_order_too_heavy_for_all_boxes(self):
        """An order exceeding the heaviest box's capacity returns None."""
        make_boxes()  # max 20 kg (Large)
        heavy = Product.objects.create(
            name='HeavyItem', length=10, width=10, height=10, weight=25
        )
        order = make_order((heavy, 1))

        box, total_weight, reasoning = select_box_for_order(order)

        self.assertIsNone(box)
        self.assertEqual(total_weight, Decimal('25'))
        self.assertIn('No suitable box', reasoning)

    def test_weight_forces_upgrade_to_larger_box(self):
        """
        A light product that fits in Small but a heavy one that
        together exceed Small's capacity should land in Medium.
        """
        small, medium, large = make_boxes()
        # Combined weight: 4.5 kg — over Small's 5 kg? No.
        # Let's make it 5.5 kg — just over Small's limit.
        p1 = Product.objects.create(name='P1', length=5, width=5, height=5, weight=3)
        p2 = Product.objects.create(name='P2', length=5, width=5, height=5, weight=2.6)
        order = make_order((p1, 1), (p2, 1))

        box, total_weight, reasoning = select_box_for_order(order)

        self.assertIsNotNone(box)
        self.assertEqual(box.name, 'Medium')
        self.assertEqual(total_weight, Decimal('5.6'))

    # --- Dimension scenarios -------------------------------------------------

    def test_product_too_large_for_all_boxes(self):
        """A product bigger than the largest box returns None."""
        make_boxes()  # largest: 50×40×30
        giant = Product.objects.create(
            name='Giant', length=60, width=50, height=40, weight=1
        )
        order = make_order((giant, 1))

        box, _, reasoning = select_box_for_order(order)

        self.assertIsNone(box)
        self.assertIn('No suitable box', reasoning)

    def test_product_fits_via_rotation(self):
        """
        A product that doesn't fit in its default orientation but does
        when rotated should still be matched to a box.
        """
        # Box: 30×10×10. Product: 10×10×25 — fits rotated (25 along length axis).
        Box.objects.create(name='Tube', length=30, width=10, height=10, max_weight=5, cost=15)
        p = Product.objects.create(name='Tube item', length=10, width=10, height=25, weight=1)
        order = make_order((p, 1))

        box, _, _ = select_box_for_order(order)

        self.assertIsNotNone(box, "Product should fit via rotation.")
        self.assertEqual(box.name, 'Tube')

    # --- Multiple quantities -------------------------------------------------

    def test_quantity_multiplies_weight(self):
        """Ordering 3 mice should multiply weight × 3."""
        make_boxes()
        _, mouse = make_products()
        order = make_order((mouse, 3))

        _, total_weight, _ = select_box_for_order(order)

        self.assertEqual(total_weight, Decimal('0.2') * 3)

    def test_multiple_units_still_fit_small_box(self):
        """3 mice should still fit in the small box (they're tiny)."""
        make_boxes()
        _, mouse = make_products()
        order = make_order((mouse, 3))

        box, _, _ = select_box_for_order(order)

        self.assertIsNotNone(box)
        self.assertEqual(box.name, 'Small')

    # --- Edge cases ----------------------------------------------------------

    def test_empty_order_returns_none(self):
        """An order with no items should return None with an explanation."""
        make_boxes()
        order = Order.objects.create()  # no items

        box, total_weight, reasoning = select_box_for_order(order)

        self.assertIsNone(box)
        self.assertEqual(total_weight, Decimal('0'))

    def test_no_boxes_in_inventory(self):
        """If no boxes exist, return None with an explanation."""
        laptop, _ = make_products()
        order = make_order((laptop, 1))

        box, _, reasoning = select_box_for_order(order)

        self.assertIsNone(box)
        self.assertIn('No boxes are available', reasoning)

    def test_cheapest_suitable_box_chosen(self):
        """When multiple boxes fit, the cheapest one must be recommended."""
        small, medium, large = make_boxes()
        # A tiny product — fits in all three boxes
        tiny = Product.objects.create(
            name='Tiny', length=5, width=5, height=5, weight=0.1
        )
        order = make_order((tiny, 1))

        box, _, _ = select_box_for_order(order)

        self.assertEqual(box.name, 'Small',
            "Should always pick the cheapest box when multiple are valid.")

    def test_run_selection_and_save_persists_result(self):
        """run_selection_and_save() should write results back to the Order."""
        make_boxes()
        laptop, mouse = make_products()
        order = make_order((laptop, 1), (mouse, 1))

        updated_order = run_selection_and_save(order)
        order.refresh_from_db()

        self.assertEqual(order.recommended_box.name, 'Small')
        self.assertEqual(order.total_weight, Decimal('2.2'))
        self.assertNotEqual(order.reasoning, '')


# ---------------------------------------------------------------------------
# 3. View tests
# ---------------------------------------------------------------------------

class HomeViewTest(TestCase):

    def test_home_returns_200(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_uses_correct_template(self):
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'packaging/home.html')

    def test_home_shows_recent_orders(self):
        """recent orders list should appear in context."""
        make_boxes()
        laptop, mouse = make_products()
        order = make_order((laptop, 1), (mouse, 1))
        run_selection_and_save(order)

        response = self.client.get(reverse('home'))
        self.assertIn('recent', response.context)


class CreateOrderViewTest(TestCase):

    def setUp(self):
        make_boxes()
        self.laptop, self.mouse = make_products()

    def test_get_returns_200(self):
        response = self.client.get(reverse('create_order'))
        self.assertEqual(response.status_code, 200)

    def test_get_uses_correct_template(self):
        response = self.client.get(reverse('create_order'))
        self.assertTemplateUsed(response, 'packaging/create_order.html')

    def test_valid_post_creates_order_and_redirects(self):
        """A valid POST should create an Order and redirect to result page."""
        response = self.client.post(reverse('create_order'), data={
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '1',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-product': self.laptop.pk,
            'form-0-quantity': '1',
            'form-1-product': self.mouse.pk,
            'form-1-quantity': '1',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.count(), 1)

    def test_invalid_post_rerenders_form(self):
        """Submitting empty formset should return 200 (not redirect)."""
        response = self.client.post(reverse('create_order'), data={
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '0',
            'form-MIN_NUM_FORMS': '1',
            'form-MAX_NUM_FORMS': '1000',
            'form-0-product': '',
            'form-0-quantity': '',
            'form-1-product': '',
            'form-1-quantity': '',
        })
        self.assertEqual(response.status_code, 200)


class OrderResultViewTest(TestCase):

    def setUp(self):
        make_boxes()
        laptop, mouse = make_products()
        order = make_order((laptop, 1), (mouse, 1))
        self.order = run_selection_and_save(order)

    def test_result_returns_200(self):
        response = self.client.get(reverse('order_result', args=[self.order.pk]))
        self.assertEqual(response.status_code, 200)

    def test_result_uses_correct_template(self):
        response = self.client.get(reverse('order_result', args=[self.order.pk]))
        self.assertTemplateUsed(response, 'packaging/order_result.html')

    def test_result_contains_order_in_context(self):
        response = self.client.get(reverse('order_result', args=[self.order.pk]))
        self.assertEqual(response.context['order'].pk, self.order.pk)

    def test_invalid_pk_returns_404(self):
        response = self.client.get(reverse('order_result', args=[9999]))
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# 4. Empty-state warning, product dropdown, and seed_data idempotency tests
# ---------------------------------------------------------------------------

class EmptyStateWarningTest(TestCase):
    """
    Tests that the create_order page shows a warning when no products
    exist and shows the dropdown populated when they do.
    """

    def test_warning_shown_when_no_products_exist(self):
        """
        When the Product table is empty, the page should render a
        has_products=False context value and display the alert-warning block.
        """
        response = self.client.get(reverse('create_order'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_products'])
        # The alert text should mention seed_data
        self.assertContains(response, 'seed_data')
        # The alert should mention the admin add-product link
        self.assertContains(response, '/admin/packaging/product/add/')

    def test_warning_not_shown_when_products_exist(self):
        """
        When products exist, has_products should be True and the
        alert-warning block should not appear.
        """
        make_products()   # creates Laptop and Mouse
        response = self.client.get(reverse('create_order'))
        self.assertTrue(response.context['has_products'])
        # The seed_data warning text should be absent
        self.assertNotContains(response, 'seed_data')

    def test_product_options_appear_in_dropdown_when_products_exist(self):
        """
        Product names should appear as <option> values in the rendered
        dropdown when the database has products.
        """
        make_products()
        response = self.client.get(reverse('create_order'))
        self.assertContains(response, 'Laptop')
        self.assertContains(response, 'Mouse')


class SeedDataCommandTest(TestCase):
    """
    Tests that the seed_data management command is idempotent —
    running it twice produces the same number of rows as running it once.
    """

    def _call_seed(self):
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        call_command('seed_data', stdout=out)
        return out.getvalue()

    def test_seed_creates_boxes_and_products(self):
        """First run should create 3 boxes and 4 products."""
        self._call_seed()
        self.assertEqual(Box.objects.count(), 3)
        self.assertEqual(Product.objects.count(), 4)

    def test_seed_is_idempotent(self):
        """Running seed_data twice must not create duplicate rows."""
        self._call_seed()
        self._call_seed()
        self.assertEqual(Box.objects.count(), 3,
            "Running seed_data twice should not duplicate boxes.")
        self.assertEqual(Product.objects.count(), 4,
            "Running seed_data twice should not duplicate products.")

    def test_seed_output_reports_already_exists_on_second_run(self):
        """Second run stdout should say 'already exists' for every item."""
        self._call_seed()
        output = self._call_seed()
        already_count = output.count('already exists')
        # 3 boxes + 4 products = 7 items, all should say 'already exists'
        self.assertEqual(already_count, 7,
            f"Expected 7 'already exists' messages, got {already_count}.\nOutput:\n{output}")
