from green_river.cleaner import clean_page_text


MESSY_TEXT = """
Unisex AIRism Cotton Oversized Crew Neck T-Shirt | UNIQLO IN
Click and collect your order in store to get free shipping!
UNIQLO home page
women
men
kids
baby
AIRism Cotton Oversized Crew Neck T-Shirt
Bestseller
Color: 09 BLACK
S
M
L
XL
XXL
3XL
Add to cart
Add to wishlist
Description
Product ID: 493232
Features
AIRism fabric with the look of cotton.
Relaxed silhouette with half-length sleeves.
Details
- The fabric makes for a clean silhouette.
Material / Care
Fabric details
53% Cotton, 30% Polyester, 17% Elastomultiester
Washing instructions
Machine wash cold
Reviews
4.8
(999+)
Shopping Guide
Membership
Returns / exchange / refund
FAQs
Terms & conditions
Privacy policy
Accessibility
Cookie Settings
Close
Cancel
"""


def test_clean_page():
    page = clean_page_text(
        MESSY_TEXT,
        "https://example.com/product/123",
    )

    output = page.to_llm_text()

    assert "AIRism Cotton Oversized Crew Neck T-Shirt" in output
    assert "493232" in output
    assert "53% Cotton" in output

    assert "Cookie Settings" not in output
    assert "Privacy policy" not in output


def test_compact_output_is_smaller():
    page = clean_page_text(
        MESSY_TEXT,
        "https://example.com/product/123",
    )

    output = page.to_llm_text()

    assert len(output) < len(MESSY_TEXT)