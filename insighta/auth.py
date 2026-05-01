import click
import requests
import secrets
import hashlib
import base64
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from insighta.credentials import (
    save_credentials,
    delete_credentials,
    load_credentials,
    is_logged_in
)
from insighta.http_client import make_request, BASE_URL
from insighta.display import (
    print_success,
    print_error,
    print_info,
    print_user_info,
    Loader
)


# ─── PKCE HELPERS ─────────────────────────────────────────────────────────────

def generate_code_verifier() -> str:
    return secrets.token_urlsafe(64)


def generate_code_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


# ─── LOCAL CALLBACK SERVER ────────────────────────────────────────────────────

class CallbackHandler(BaseHTTPRequestHandler):
    """
    Temporary local server that catches GitHub's redirect.
    GitHub redirects to http://localhost:8765/callback
    This handler captures the code and state from the URL.
    """
    code = None
    state = None

    def do_GET(self):
        # Parse the callback URL
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        # Extract code and state from query params
        CallbackHandler.code = params.get("code", [None])[0]
        CallbackHandler.state = params.get("state", [None])[0]

        # Send a response to the browser so it doesn't hang
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"""
            <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h2>Login successful!</h2>
                <p>You can close this tab and return to the terminal.</p>
            </body>
            </html>
        """)

    def log_message(self, format, *args):
        # Suppress default server logs
        pass


# ─── AUTH COMMANDS ────────────────────────────────────────────────────────────

@click.group(name="auth")
def auth_commands():
    """Authentication commands."""
    pass


@auth_commands.command(name="login")
def login():
    """Login with GitHub."""

    # Check if already logged in
    if is_logged_in():
        credentials = load_credentials()
        print_info(f"Already logged in as @{credentials['username']}")
        print_info("Run 'insighta auth logout' to logout first.")
        return

    # Generate PKCE values
    code_verifier = generate_code_verifier()
    code_challenge = generate_code_challenge(code_verifier)

    print_info("Opening GitHub login page in your browser...")

    # Open browser to start OAuth flow
    auth_url = f"{BASE_URL}/auth/github/cli?code_challenge={code_challenge}"
    webbrowser.open(auth_url)

    # Start local callback server
    # This catches GitHub's redirect after login
    print_info("Waiting for GitHub callback...")
    server = HTTPServer(("localhost", 8765), CallbackHandler)

    # Handle one request then stop
    server.handle_request()
    server.server_close()

    # Check we got the code back
    code = CallbackHandler.code
    print(code)
    if not code:
        print_error("Login failed. No code received from GitHub.")
        return

    # Send code + code_verifier to backend
    with Loader("Completing login..."):
        try:
            response = requests.post(
                f"{BASE_URL}/auth/github/callback",
                json={
                    "code": code,
                    "code_verifier": code_verifier,
                    "code_challenge": code_challenge
                }
            )
        except requests.exceptions.ConnectionError:
            print_error("Cannot connect to server. Make sure the backend is running.")
            return

    if response.status_code != 200:
        data = response.json()
        print_error(f"Login failed: {data.get('message', 'Unknown error')}")
        return

    data = response.json()
    user = data["user"]

    # Save tokens locally
    save_credentials(
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        username=user["username"],
        email=user.get("email", ""),
        role=user.get("role", ""),
        last_login_at = user.get('last_login_at')
    )

    print_success(f"Logged in as @{user['username']}")


@auth_commands.command(name="logout")
def logout():
    """Logout and invalidate tokens."""

    if not is_logged_in():
        print_error("You are not logged in.")
        return

    credentials = load_credentials()

    with Loader("Logging out..."):
        response = make_request(
            "POST",
            "/auth/logout",
            json={"refresh_token": credentials["refresh_token"]}
        )

    # Delete local credentials regardless of server response
    delete_credentials()
    print_success("Logged out successfully.")


@auth_commands.command(name="whoami")
def whoami():
    """Show current logged in user."""

    if not is_logged_in():
        print_error("You are not logged in. Run 'insighta auth login'")
        return

    credentials = load_credentials()
    print_user_info({
        "username": credentials.get("username"),
        "email": credentials.get("email"),
        "role": credentials.get('role'),
        'last_login_at': credentials.get('last_login_at')
    })