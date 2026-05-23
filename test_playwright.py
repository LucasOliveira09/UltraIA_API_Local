import asyncio
import sys
from playwright.async_api import async_playwright

async def test_playwright():
    print("Testing Playwright...")
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://example.com")
            print(f"Title: {await page.title()}")
            await browser.close()
            print("Playwright is working perfectly!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

asyncio.run(test_playwright())
