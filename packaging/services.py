"""
Box selection service.

Core algorithm: given an Order, find the cheapest box whose internal
dimensions can physically contain all ordered products and whose weight
capacity is not exceeded.

Packing strategy (documented heuristic):
  For each product we try all six axis-aligned orientations of the
  rectangular product. We use a simple 3-D shelf/layer placement —
  products are stacked in a single row along the box's length axis.
  This is a heuristic: it may reject some valid packings where a
  smarter 3-D arrangement would succeed, but it is deterministic,
  easy to verify, and correct for the common case of a small number
  of similar-sized products.
"""

from decimal import Decimal
from itertools import permutations
from .models import Box, Order


# ---------------------------------------------------------------------------
# Orientation helpers
# ---------------------------------------------------------------------------

def _orientations(l, w, h):
    """
    Return all 6 unique axis-aligned orientations of a box with
    dimensions (l, w, h) as (length, width, height) tuples.
    Using a set removes duplicates when two dimensions are equal.
    """
    return list({perm for perm in permutations([l, w, h])})


# ---------------------------------------------------------------------------
# Core packing check
# ---------------------------------------------------------------------------

def _items_fit_in_box(items, box):
    """
    Try to pack all items (list of (l, w, h) tuples, one per unit quantity)
    into the box using a single-row stacking strategy.

    Strategy: place items end-to-end along the box's length axis.
    For each item we try every orientation and pick the one that uses
    the least length while fitting within the box's width and height.

    Returns True if all items fit, False otherwise.
    """
    b_l = Decimal(str(box.length))
    b_w = Decimal(str(box.width))
    b_h = Decimal(str(box.height))

    total_length_used = Decimal('0')

    for (il, iw, ih) in items:
        best_orientation = None
        best_item_length = None

        for (ol, ow, oh) in _orientations(il, iw, ih):
            # This orientation must fit within box width and height
            if ow <= b_w and oh <= b_h:
                if best_item_length is None or ol < best_item_length:
                    best_item_length = ol
                    best_orientation = (ol, ow, oh)

        if best_orientation is None:
            # No orientation of this single item fits the box cross-section
            return False

        total_length_used += best_orientation[0]

    return total_length_used <= b_l


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def select_box_for_order(order):
    """
    Given an Order instance (with OrderItems already saved), run the
    box selection algorithm and return (recommended_box, total_weight, reasoning).

    Steps:
      1. Collect all product units with their dimensions.
      2. Calculate total weight (sum of product.weight × quantity).
      3. For each box ordered by cost (cheapest first):
         a. Reject if total weight exceeds box.max_weight.
         b. Reject if items don't physically fit (packing check).
         c. First box that passes both checks is the recommendation.
      4. If no box passes, return (None, total_weight, explanation).
    """
    items = order.items.select_related('product').all()

    if not items.exists():
        return None, Decimal('0'), "Order has no items."

    # Build a flat list of (l, w, h) for every individual unit
    unit_dims = []
    total_weight = Decimal('0')
    item_summary_lines = []

    for item in items:
        p = item.product
        pl = Decimal(str(p.length))
        pw = Decimal(str(p.width))
        ph = Decimal(str(p.height))
        pw_unit = Decimal(str(p.weight))

        for _ in range(item.quantity):
            unit_dims.append((pl, pw, ph))

        line_weight = pw_unit * item.quantity
        total_weight += line_weight
        item_summary_lines.append(
            f"  • {item.quantity}× {p.name} "
            f"({p.length}×{p.width}×{p.height} cm, {p.weight} kg each) "
            f"= {line_weight} kg"
        )

    all_boxes = Box.objects.all()   # already ordered by cost (cheapest first)

    if not all_boxes.exists():
        reasoning = (
            "No boxes are available in inventory. "
            "Please add boxes via the admin panel."
        )
        return None, total_weight, reasoning

    rejected_lines = []

    for box in all_boxes:
        b_max_weight = Decimal(str(box.max_weight))

        # --- weight check ---
        if total_weight > b_max_weight:
            rejected_lines.append(
                f"  ✗ {box.name}: total weight {total_weight} kg "
                f"exceeds capacity {b_max_weight} kg."
            )
            continue

        # --- dimensional / packing check ---
        if not _items_fit_in_box(unit_dims, box):
            rejected_lines.append(
                f"  ✗ {box.name}: items do not fit inside "
                f"{box.length}×{box.width}×{box.height} cm."
            )
            continue

        # --- first passing box is the cheapest suitable one ---
        reasoning = (
            f"Order summary:\n" +
            "\n".join(item_summary_lines) +
            f"\n\nTotal weight: {total_weight} kg\n\n"
            f"Recommended box: {box.name} "
            f"({box.length}×{box.width}×{box.height} cm, "
            f"max {box.max_weight} kg, ₹{box.cost})\n\n"
            f"Selection logic:\n"
            f"  • Boxes are evaluated cheapest-first.\n"
            f"  • Weight check passed: {total_weight} kg ≤ {box.max_weight} kg.\n"
            f"  • Packing check passed: all items fit using single-row "
            f"orientation heuristic.\n"
        )
        if rejected_lines:
            reasoning += "\nBoxes rejected before this one:\n" + "\n".join(rejected_lines)

        return box, total_weight, reasoning

    # No box passed all checks
    reasoning = (
        f"Order summary:\n" +
        "\n".join(item_summary_lines) +
        f"\n\nTotal weight: {total_weight} kg\n\n"
        f"No suitable box was found.\n\n"
        f"Rejection details:\n" + "\n".join(rejected_lines)
    )
    return None, total_weight, reasoning


def run_selection_and_save(order):
    """
    Runs select_box_for_order and writes the results back onto the
    Order instance. Returns the updated Order.
    """
    box, total_weight, reasoning = select_box_for_order(order)
    order.recommended_box = box
    order.total_weight = total_weight
    order.reasoning = reasoning
    order.save()
    return order
