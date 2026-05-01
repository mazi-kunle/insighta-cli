from rich.console import Console
from rich.table import Table
from rich.spinner import Spinner
from rich.live import Live
from rich import box
import time

console = Console()


# ─── MESSAGES ─────────────────────────────────────────────────────────────────

def print_success(message):
    """Prints a green success message."""
    console.print(f"✓ {message}", style="bold green")


def print_error(message):
    """Prints a red error message."""
    console.print(f"✗ {message}", style="bold red")


def print_info(message):
    """Prints a blue info message."""
    console.print(f"→ {message}", style="bold blue")


# ─── LOADER ───────────────────────────────────────────────────────────────────

class Loader:
    """
    Shows a spinning loader while a task is running.

    Usage:
        with Loader("Fetching profiles..."):
            response = make_request("GET", "/api/profiles")
    """
    def __init__(self, message: str):
        self.message = message
        self.live = Live(
            Spinner("dots", text=message, style="bold blue"),
            refresh_per_second=10,
            transient=True       # clears the spinner after it stops
        )

    def __enter__(self):
        self.live.__enter__()
        return self

    def __exit__(self, *args):
        self.live.__exit__(*args)


# ─── TABLES ───────────────────────────────────────────────────────────────────

def print_profiles_table(profiles: list):
    """
    Displays a list of profiles as a formatted table.
    """
    if not profiles:
        print_info("No profiles found.")
        return

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="bright_black"
    )

    # Define columns
    table.add_column("ID", style="dim", width=30)
    table.add_column("Name", style="bold white")
    table.add_column("Gender", style="cyan")
    table.add_column("Age", style="green")
    table.add_column("Age Group", style="green")
    table.add_column("Country ID", style="yellow")
    table.add_column("Created At", style="dim")

    # Add rows
    for profile in profiles:
        table.add_row(
            str(profile.get("id", "")),
            str(profile.get("name", "")),
            str(profile.get("gender", "")),
            str(profile.get("age", "")),
            str(profile.get("age_group", "")),
            str(profile.get("country_id", "")),
            str(profile.get("created_at", ""))
        )

    console.print(table)


def print_profile_detail(profile: dict):
    """
    Displays a single profile in a detailed format.
    """
    table = Table(
        box=box.ROUNDED,
        show_header=False,
        border_style="bright_black"
    )

    table.add_column("Field", style="bold cyan", width=20)
    table.add_column("Value", style="white")

    fields = [
        ("ID", "id"),
        ("Name", "name"),
        ("Gender", "gender"),
        ("Gender Probability", "gender_probability"),
        ("Age", "age"),
        ("Age Group", "age_group"),
        ("Country ID", "country_id"),
        ("Country Name", "country_name"),
        ("Country Probability", "country_probability"),
        ("Created At", "created_at")
    ]

    for label, key in fields:
        table.add_row(label, str(profile.get(key, "")))

    console.print(table)


def print_pagination_info(page: int, total_pages: int, total: int):
    """
    Displays pagination info below the table.
    """
    console.print(
        f"\n  Page [bold cyan]{page}[/bold cyan] of "
        f"[bold cyan]{total_pages}[/bold cyan] "
        f"([dim]{total} total profiles[/dim])\n"
    )


def print_user_info(user: dict):
    """
    Displays logged in user info for whoami command.
    """
    table = Table(
        box=box.ROUNDED,
        show_header=False,
        border_style="bright_black"
    )

    table.add_column("Field", style="bold cyan", width=15)
    table.add_column("Value", style="white")

    table.add_row("Username", f"@{user.get('username', '')}")
    table.add_row("Email", user.get("email", ""))
    table.add_row("Role", user.get("role", ""))
    table.add_row("Last Login", user.get("last_login_at", ""))

    console.print(table)