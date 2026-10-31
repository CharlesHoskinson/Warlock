"""Exercise both switcher entry paths through the shipped Elm adapters.

Requires Playwright and the shared Chromium CDP endpoint on port 9222.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread

from playwright.sync_api import sync_playwright


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    stage = Path(__file__).resolve().parents[2]
    with TemporaryDirectory() as directory:
        (Path(directory) / 'Warlock').symlink_to(stage)
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Quiet, directory=directory))
        Thread(target=server.serve_forever, daemon=True).start()
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.connect_over_cdp('http://127.0.0.1:9222')
                context = browser.new_context(viewport={'width': 1440, 'height': 900})
                try:
                    page = context.new_page()
                    page.goto(f'http://127.0.0.1:{server.server_port}/Warlock/test-drive/')
                    page.wait_for_timeout(2500)
                    bar = page.frame_locator('#bar')
                    switcher = bar.locator('button').filter(has_text='Switch windows')
                    for entry in ('button', 'keyboard'):
                        if entry == 'button':
                            switcher.click()
                            page.wait_for_function("!document.querySelector('#popup').hidden")
                        else:
                            page.wait_for_timeout(500)
                            switcher.focus()
                        page.keyboard.down('Alt')
                        page.keyboard.press('Tab')
                        page.wait_for_function("!document.querySelector('#popup').hidden")
                        page.wait_for_timeout(500)
                        page.keyboard.up('Alt')
                        page.wait_for_function("document.querySelector('#popup').hidden", timeout=5000)
                        print(f'{entry}-opened switcher commits on Alt release')
                finally:
                    context.close()
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    main()
