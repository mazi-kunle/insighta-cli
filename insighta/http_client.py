import requests
import click
from insighta.credentials import *


BASE_URL = 'http://localhost:5000'


def get_headers():
    """
    Builds the headers for every API request.
    Includes the access token and API version.
    """
    access_token = get_access_token()
    return {
        "Authorization": f"Bearer {access_token}",
        "X-API-Version": "1",
        "Content-Type": "application/json"
    }

def refresh_tokens():
    """
    Attempts to refresh the access token using the refresh token.
    Returns True if successful, False if refresh failed.
    """
    refresh_token = get_refresh_token()
    if not refresh_token:
        return False

    try:
        response = requests.post(
            f"{BASE_URL}/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        if response.status_code == 200:
            data = response.json()

            # Load existing credentials to preserve username and avatar
            credentials = load_credentials()

            # Save new tokens
            save_credentials(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                username=credentials.get("username", ""),
                email=credentials.get('email'),
                role=credentials.get("role", ''),
                last_login_at=credentials.get('last_login_at', '')
            )
            return True

        return False

    except requests.exceptions.ConnectionError:
        return False
    


def make_request(method, endpoint, **kwargs):
    """
    Central HTTP client function.
    All CLI commands use this instead of calling requests directly.

    Handles:
    - Attaching auth headers
    - Detecting 401 expired token
    - Auto refreshing and retrying
    - Prompting re-login if refresh fails
    - Connection errors

    Usage:
        response = request("GET", "/api/profiles")
        response = request("POST", "/api/profiles", json={"name": "John"})
        response = request("DELETE", f"/api/profiles/{id}")
    """
    url = f"{BASE_URL}{endpoint}"
    try:
        # Make the initial request
        response = requests.request(
            method,
            url,
            headers=get_headers(),
            **kwargs
        )
         # If token expired → try to refresh and retry
        if response.status_code == 401:
            refreshed = refresh_tokens()

            if refreshed:
                # Retry the original request with new token
                response = requests.request(
                    method,
                    url,
                    headers=get_headers(),
                    **kwargs
                )
            else:
                # Refresh failed → user must log in again
                click.echo(
                    click.style(
                        "\n Session expired. Please run: insighta login",
                        fg="red"
                    )
                )
                delete_credentials()
                return None
        return response
    
    except requests.exceptions.Timeout:
        click.echo(
            click.style(
                "\n Request timed out. Please try again.",
                fg="red"
            )
        )
        return None