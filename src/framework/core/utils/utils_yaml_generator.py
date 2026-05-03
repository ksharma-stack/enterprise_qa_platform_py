"""Locator YAML generator utility"""

import os
import yaml
from playwright.sync_api import Page


def generate(page: Page, out_path: str, page_name: str):
    """Generates locator YAML"""
    locators = {}
    for inp in page.query_selector_all("input, button"):
        name = inp.get_attribute("name") or inp.text_content()
        if not name:
            continue
        locators[name.lower()] = {
            "css": page.evaluate("e=>e.tagName.toLowerCase()", inp)
        }

    data = {page_name: locators}
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)
