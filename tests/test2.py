from green_river.llm.extractor import extract_product


MESSY_1 = """
AIRism Cotton Oversized Crew Neck T-Shirt
Bestseller
Color: 09 BLACK
S
M
L
XL
XXL
3XL

Description
Product ID: 493232

Features
AIRism fabric with the look of cotton.
Stay-fresh comfort. Instantly cool and comfortable.
Relaxed silhouette with half-length sleeves,
an oversized cut, and dropped shoulders.

Material / Care

53% Cotton, 30% Polyester, 17% Elastomultiester

Washing instructions
Machine wash cold, Dry Clean, Do not tumble dry.

Reviews
4.8
(999+)

Shopping Guide
Membership
Privacy policy
Cookie Settings
"""


MESSY_2 = """
Sony WH-1000XM5 Wireless Headphones

Wireless noise cancelling headphones.
Battery life up to 30 hours.
Color: Black

Price: $349.99

Bluetooth
USB-C charging
"""


MESSY_3 = """
Running Shoes
Brand: Example Sports

Men's running shoes designed for daily training.
Sizes 7, 8, 9, 10, 11.
Lightweight mesh upper.
Rubber outsole.

No price information listed.
"""


MESSY_4 = """
Handmade Ceramic Coffee Mug

Stoneware ceramic mug.
Dishwasher safe.
Microwave safe.

Blue glaze.
Capacity: 350 ml.
"""

MESSY_5 = """
Premium Laptop Stand

Aluminium construction.
Adjustable height.
Compatible with laptops up to 16 inches.

Shipping available worldwide.

No brand, price, SKU, review count, or rating shown.
"""


def test_uniqlo():
    result = extract_product(MESSY_1)

    assert result["product_name"] is not None
    assert result["product_id"] == "493232"

    assert result["brand"] is None

    assert result["source_site"] in {
        None,
        "UNIQLO",
        "Uniqlo",
    }

    assert result["color"] == "09 BLACK"
    assert "L" in result["sizes"]


def test_headphones():
    result = extract_product(MESSY_2)

    assert "WH-1000XM5" in result["product_name"]
    assert result["price"] == "$349.99"
    assert result["color"] == "Black"


def test_missing_price_is_null():
    result = extract_product(MESSY_3)

    assert result["price"] is None


def test_missing_brand_is_null():
    result = extract_product(MESSY_4)

    assert result["brand"] is None


def test_missing_rating_is_null():
    result = extract_product(MESSY_5)

    assert result["rating"] is None
    assert result["review_count"] is None


def test_product_line_is_not_brand():
    text = """
    AIRism Cotton Oversized Crew Neck T-Shirt

    AIRism fabric with the look of cotton.

    Uniqlo U

    Product ID: 493232
    """

    result = extract_product(text)

    assert result["product_name"] == (
        "AIRism Cotton Oversized Crew Neck T-Shirt"
    )

    assert result["brand"] is None

def test_manufacturer_is_not_brand():
    text = """
    Premium T-Shirt

    Manufacturer - Example Apparel Pvt Ltd

    Product ID: 12345
    """

    result = extract_product(text)

    assert result["brand"] is None
    assert (
        result["manufacturer"]
        == "Example Apparel Pvt Ltd"
    )