"""
Locator resolver during test execution
"""


class LocatorResolver:
    """Locator resolver during test execution"""

    # PREFERRED = ["role", "css", "xpath"]

    def __init__(self, page):
        self.page = page

    def resolve(self, page_locators: dict, element: str):
        """returns resolved locator"""
        PREFERRED = ["role", "css", "xpath"]

        data = page_locators.get(element)
        if not data:
            print("[ERROR]: No locator found")

        for key in PREFERRED:
            print(f"Key from Preferred list is: {key}")
            if key in data:
                match key:
                    case "css":
                        if self.page.locator(data[key]).is_visible():
                            return self.page.locator(data[key])
                        else:
                            None
                    case "role":
                        if self.page.get_by_role(
                            data[key], name=data.get("name")
                        ).is_visible():
                            return self.page.get_by_role(
                                data[key], name=data.get("name")
                            )
                        else:
                            None
                    case "xpath":
                        if self.page.locator(data[key]).is_visible():
                            return self.page.locator(data[key])
                        else:
                            None
                    case _:
                        print("[TODO]: Need to impliment MCP/AI for self healing.")
                        return None
