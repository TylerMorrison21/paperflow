"""Claude Vision enhancement — optional second pass over OCR output."""

import base64
import os

import anthropic


def enhance_page(page) -> "PageData":
    """Use Claude Vision to compare the page image against OCR text and fix errors.

    Args:
        page: A PageData object with image_bytes and raw_text.

    Returns:
        The same PageData object with raw_text improved.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or not page.image_bytes:
        return page  # Skip enhancement if no API key or no image

    client = anthropic.Anthropic(api_key=api_key)
    img_b64 = base64.b64encode(page.image_bytes).decode()

    response = client.messages.create(
        model="claude-sonnet-4-5-20250514",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img_b64,
                        },
                    },
                    {
                        "type": "text",
                        "text": (
                            "OCR extracted this text from the page image above:\n"
                            "---\n"
                            f"{page.raw_text}\n"
                            "---\n"
                            "Fix any OCR errors, merge broken lines into proper "
                            "paragraphs, and return clean Markdown. "
                            "Remove any headers/footers if OCR missed them."
                        ),
                    },
                ],
            }
        ],
    )
    page.raw_text = response.content[0].text
    return page
