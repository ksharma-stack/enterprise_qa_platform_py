
# # ---------------------------------------------------------
# # Root document (single page / window contract)
# # ---------------------------------------------------------
# class LocatorDocument(StrictModel):
#     meta: LocatorMeta
#     locators: Dict[str, LocatorDefinition]

#     @field_validator("locators")
#     @classmethod
#     def locator_keys_must_be_snake_case(cls, v):
#         for key in v.keys():
#             if "-" in key or " " in key:
#                 raise ValueError(
#                     f"Locator key '{key}' must be snake_case (API contract)"
#                 )
#         return v
