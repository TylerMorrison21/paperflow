"""Stripe integration for single-purchase payments."""

import os

import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

PRICE_SMALL = 300   # $3.00 for ≤300 pages
PRICE_LARGE = 500   # $5.00 for 300-600 pages


def create_checkout_session(page_count: int, success_url: str, cancel_url: str) -> str:
    """Create a Stripe Checkout session and return the URL.

    Args:
        page_count: Number of pages in the PDF (determines price).
        success_url: Redirect URL after successful payment.
        cancel_url: Redirect URL if user cancels.

    Returns:
        Stripe Checkout session URL.
    """
    price = PRICE_LARGE if page_count > 300 else PRICE_SMALL

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "PDF to EPUB Conversion"},
                    "unit_amount": price,
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.url
