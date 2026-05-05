# Insighta Labs — CLI

A command line interface for interacting with the Insighta Labs+ platform. The CLI allows analysts and admins to manage profiles, search data, and export results directly from the terminal.

---

## Prerequisites

Python 3.8 or higher and the Insighta Labs backend running and accessible.

---

## Installation

```bash
git clone https://github.com/mazi-kunle/insighta-cli
cd insighta-cli
pip install -e .
```

After installation the `insighta` command is available globally from any directory.

---

## Configuration

The CLI connects to the backend via the `BASE_URL` defined in `insighta/http_client.py`. By default it points to `http://localhost:5000`. Update this to your deployed backend URL for production use.

Credentials are stored locally at `~/.insighta/credentials.json` after login. This file contains the access token, refresh token, username, and avatar URL. Never share this file.

---

## Authentication

### Login

```bash
insighta login
```

This opens your browser to the GitHub OAuth page. After approving access, the CLI catches the callback, exchanges the code with the backend, and saves your tokens locally. You will see "Logged in as @username" when complete.

### Logout

```bash
insighta logout
```

This invalidates your refresh token on the backend and deletes your local credentials file. Your session is terminated on all clients.

### Check Current User

```bash
insighta whoami
```

This calls the backend to verify your session and display your current user information including username, email, role, and last login time.

---

## Profile Commands

### List Profiles

```bash
insighta profiles list
```

Returns a paginated table of all profiles. Supports the following options:

```bash
insighta profiles list --gender male
insighta profiles list --country NG
insighta profiles list --age-group adult
insighta profiles list --min-age 25 --max-age 40
insighta profiles list --sort-by age --order desc
insighta profiles list --page 2 --limit 20
```

Options can be combined:

```bash
insighta profiles list --gender male --country NG --age-group adult --sort-by age --order desc
```

### Get Single Profile

```bash
insighta profiles get <id>
```

Returns detailed information about a single profile by its ID.

```bash
insighta profiles get 069f1ec5-4021-749a-8000-4edd3008b59c
```

### Search Profiles

```bash
insighta profiles search "<query>"
```

Accepts natural language queries and returns matching profiles.

```bash
insighta profiles search "young males from nigeria"
insighta profiles search "adults over 30 from the US"
insighta profiles search "female profiles from Ghana"
```

Supports pagination:

```bash
insighta profiles search "young males from nigeria" --page 2 --limit 20
```

### Create Profile

```bash
insighta profiles create --name "<name>"
```

Creates a new profile by fetching data from external APIs. Admin only.

```bash
insighta profiles create --name "Harriet Tubman"
```

### Export Profiles

```bash
insighta profiles export --format csv
```

Exports all profiles as a CSV file saved to the current working directory. Supports the same filters as the list command.

```bash
insighta profiles export --format csv --gender male --country NG
```

---

## Token Handling

The CLI uses two tokens — a short-lived access token (3 minutes) and a longer-lived refresh token (5 minutes). Both are stored in `~/.insighta/credentials.json` after login.

Every API request goes through a central HTTP client that automatically handles token expiry. When the access token expires the client detects the 401 response, calls the backend refresh endpoint with the stored refresh token, saves the new token pair, and retries the original request. The user never sees an interruption.

If the refresh token has also expired the CLI prints "Session expired. Please run: insighta login" and deletes the local credentials file. The user must log in again.

---

## PKCE Security

The CLI uses PKCE (Proof Key for Code Exchange) during login to protect against code interception attacks. Before opening the browser the CLI generates a random `code_verifier` and derives a `code_challenge` from it using SHA256. The challenge is sent to GitHub upfront. When the CLI sends the code to the backend it also sends the `code_verifier`. The backend verifies that the verifier matches the challenge before completing the exchange. This ensures only the CLI process that initiated the login can complete it.

---

## Output Format

All results are displayed as formatted tables with borders and colors. A loading spinner is shown while waiting for API responses. Errors are displayed in red with a clear message. Success messages are displayed in green.

---


## Deployment

The CLI runs locally and connects to the deployed backend.