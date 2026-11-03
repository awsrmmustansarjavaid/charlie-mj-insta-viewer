"""Clearly labelled demo provider used to preview screens before API integration."""

from instagram_research_suite.providers.base import DataProvider, FetchResult


class DemoProvider(DataProvider):
    """Return fictional sample records; never represents them as live Instagram data."""

    name = "Demo data (fictional)"

    def fetch_relationships(self, handle: str, list_type: str) -> FetchResult:
        # A small fixture keeps the app demonstrable without scraping real accounts.
        records = [
            {"username": "sample_traveller", "display_name": "Sample Traveller", "is_private": False},
            {"username": "coffee.notes", "display_name": "Coffee Notes", "is_private": False},
            {"username": "design.archive", "display_name": "Design Archive", "is_private": True},
        ]
        return FetchResult(
            records=records,
            expected_count=None,
            completeness="unknown",
            message=f"Fictional preview for @{handle}; no live account was contacted.",
        )
