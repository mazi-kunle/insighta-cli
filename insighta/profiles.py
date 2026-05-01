import click
import os
from insighta.http_client import make_request
from insighta.credentials import is_logged_in
from insighta.display import (
    Loader,
    print_success,
    print_error,
    print_info,
    print_profiles_table,
    print_profile_detail,
    print_pagination_info
)


# ─── PROFILES GROUP ───────────────────────────────────────────────────────────

@click.group(name="profiles")
def profiles_commands():
    """Profile management commands."""
    pass


# ─── LIST PROFILES ────────────────────────────────────────────────────────────

@profiles_commands.command(name="list")
@click.option("--gender", default=None, help="Filter by gender (male/female)")
@click.option("--country", default=None, help="Filter by country code e.g NG")
@click.option("--age-group", default=None, help="Filter by age group e.g adult")
@click.option("--min-age", default=None, type=int, help="Filter by minimum age")
@click.option("--max-age", default=None, type=int, help="Filter by maximum age")
@click.option("--sort-by", default=None, help="Sort by field e.g age, name")
@click.option("--order", default="asc", help="Sort order: asc or desc")
@click.option("--page", default=1, type=int, help="Page number")
@click.option("--limit", default=10, type=int, help="Number of profiles per page")
def list_profiles(gender, country, age_group, min_age, max_age, sort_by, order, page, limit):
    """List all profiles with optional filters."""

    if not is_logged_in():
        print_error("You are not logged in. Run 'insighta auth login'")
        return

    # Build query params from options
    # Only include params that were actually provided
    params = {"page": page, "limit": limit}

    if gender:
        params["gender"] = gender
    if country:
        params["country_id"] = country
    if age_group:
        params["age_group"] = age_group
    if min_age:
        params["min_age"] = min_age
    if max_age:
        params["max_age"] = max_age
    if sort_by:
        params["sort_by"] = sort_by
        params["order"] = order

    with Loader("Fetching profiles..."):
        response = make_request("GET", "/api/profiles", params=params)

    if not response:
        return

    if response.status_code != 200:
        data = response.json()
        print_error(data.get("message", "Failed to fetch profiles"))
        return

    data = response.json()
    profiles = data.get("data", [])
    
    print_profiles_table(profiles)
    print_pagination_info(
        data.get("page", 1),
        data.get("total_pages", 1),
        data.get("total", 0)
    )


# ─── GET SINGLE PROFILE ───────────────────────────────────────────────────────

@profiles_commands.command(name="get")
@click.argument("id")
def get_profile(id):
    """Get a single profile by ID."""

    if not is_logged_in():
        print_error("You are not logged in. Run 'insighta auth login'")
        return

    with Loader(f"Fetching profile {id}..."):
        response = make_request("GET", f"/api/profiles/{id}")

    if not response:
        print_error(f"Profile with ID {id} not found.")
        return

    if response.status_code == 404:
        print_error(f"Profile with ID {id} not found.")
        return

    if response.status_code != 200:
        data = response.json()
        print_error(data.get("message", "Failed to fetch profile"))
        return

    data = response.json()

    print_profile_detail(data.get("data", {}))


# ─── SEARCH PROFILES ──────────────────────────────────────────────────────────

@profiles_commands.command(name="search")
@click.argument("query")
@click.option("--page", default=1, type=int, help="Page number")
@click.option("--limit", default=10, type=int, help="Number of results per page")
def search_profiles(query, page, limit):
    """Search profiles using natural language."""

    if not is_logged_in():
        print_error("You are not logged in. Run 'insighta auth login'")
        return

    params = {"q": query, "page": page, "limit": limit}

    with Loader(f"Searching for '{query}'..."):
        response = make_request("GET", "/api/profiles/search", params=params)

    if not response:
        return

    if response.status_code != 200:
        data = response.json()
        print_error(data.get("message", "Search failed"))
        return

    data = response.json()
    profiles = data.get("data", [])

    print_profiles_table(profiles)
    print_pagination_info(
        data.get("page", 1),
        data.get("total_pages", 1),
        data.get("total", 0)
    )


# ─── CREATE PROFILE ───────────────────────────────────────────────────────────

@profiles_commands.command(name="create")
@click.option("--name", required=True, help="Name to create profile for")
def create_profile(name):
    """Create a new profile. Admin only."""

    if not is_logged_in():
        print_error("You are not logged in. Run 'insighta auth login'")
        return

    with Loader(f"Creating profile for {name}..."):
        response = make_request("POST", "/api/profiles", json={"name": name})

    if not response:
        return

    if response.status_code == 403:
        print_error("Access denied. Only admins can create profiles.")
        return

    if response.status_code not in [200, 201]:
        data = response.json()
        print_error(data.get("message", "Failed to create profile"))
        return

    data = response.json()
    print_success(f"Profile created successfully.")
    print_profile_detail(data.get("data", {}))


# ─── EXPORT PROFILES ──────────────────────────────────────────────────────────

@profiles_commands.command(name="export")
@click.option("--format", default="csv", help="Export format (csv)")
@click.option("--gender", default=None, help="Filter by gender")
@click.option("--country", default=None, help="Filter by country code")
@click.option("--age-group", default=None, help="Filter by age group")
def export_profiles(format, gender, country, age_group):
    """Export profiles as CSV file."""

    if not is_logged_in():
        print_error("You are not logged in. Run 'insighta auth login'")
        return

    params = {"format": format}

    if gender:
        params["gender"] = gender
    if country:
        params["country_id"] = country
    if age_group:
        params["age_group"] = age_group

    with Loader("Exporting profiles..."):
        response = make_request("GET", "/api/profiles/export", params=params)

    if not response:
        return

    if response.status_code != 200:
        data = response.json()
        print_error(data.get("message", "Export failed"))
        return

    # Save CSV to current working directory
    filename = f"profiles_export.csv"
    filepath = os.path.join(os.getcwd(), filename)

    with open(filepath, "w") as f:
        f.write(response.text)

    print_success(f"Profiles exported to {filepath}")