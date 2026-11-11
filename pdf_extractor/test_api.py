"""
Quick test: Send a single page image to the API and see what comes back.
Use this FIRST to verify your API key and model work before processing full PDFs.

Usage:
    python test_api.py --image "path/to/any_image.jpg"
    python test_api.py --pdf "path/to/test.pdf" --page 1
"""

import os, sys, base64, json, argparse
from io import BytesIO
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from PIL import Image

API_KEY  = os.environ.get("OPENAI_API_KEY", "")
BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.freemodel.dev/v1")
MODEL    = os.environ.get("OPENAI_MODEL", "gpt-4o")

if not API_KEY:
    print("❌ Set OPENAI_API_KEY in your .env file")
    sys.exit(1)

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

def test_with_image(img: Image.Image):
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    print(f"🤖 Calling {MODEL} via {BASE_URL}...")
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe what you see on this page. If there are exam questions, list the first question and its answer choices."},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "high"}}
            ]
        }],
        max_tokens=500,
    )
    
    print("\n✅ API Response:")
    print("-" * 50)
    print(response.choices[0].message.content)
    print("-" * 50)
    print(f"\nTokens used: {response.usage}")

def main():
    parser = argparse.ArgumentParser(description="Test API connection with a sample image")
    parser.add_argument("--image", help="Path to an image file")
    parser.add_argument("--pdf",   help="Path to a PDF file")
    parser.add_argument("--page",  type=int, default=1, help="Page number to test (default: 1)")
    args = parser.parse_args()

    if args.pdf:
        try:
            from pdf2image import convert_from_path
        except ImportError:
            print("❌ pdf2image not installed. Run: pip install pdf2image")
            sys.exit(1)
        print(f"📄 Converting page {args.page} of {args.pdf}...")
        pages = convert_from_path(args.pdf, dpi=150, first_page=args.page, last_page=args.page)
        img = pages[0]
    elif args.image:
        img = Image.open(args.image)
    else:
        # Create a simple test image with text
        print("ℹ️  No image/pdf specified. Creating a test image...")
        img = Image.new('RGB', (400, 200), color='white')
        from PIL import ImageDraw
        d = ImageDraw.Draw(img)
        d.text((10, 80), "Test: 2 + 2 = ?  A) 3   B) 4   C) 5", fill='black')
    
    test_with_image(img)

if __name__ == "__main__":
    main()
