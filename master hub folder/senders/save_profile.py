from playwright.sync_api import sync_playwright

p = sync_playwright().start()

context = p.chromium.launch_persistent_context(
    user_data_dir="jiosaavn_profile",
    channel="chrome",
    headless=False
)

page = context.new_page()
page.goto("https://www.jiosaavn.com")

input("Login to JioSaavn and press Enter...")

context.close()
p.stop()