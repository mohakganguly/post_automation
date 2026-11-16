# Automated Multi-Platform Posting System

An asynchronous, API-driven social media publishing system that allows users to distribute content across multiple platforms through a unified interface.

The system uses platform-specific adapters, centralized configuration, asynchronous HTTP requests, and standardized response handling to simplify multi-platform content distribution.

## Features

- **Multi-platform publishing:** Publish content to five platforms through a unified service.
- **Asynchronous execution:** Uses Python's `asyncio` and `httpx` for efficient asynchronous API communication.
- **Platform-specific authentication:** Supports the authentication mechanisms required by each platform.
- **Input validation:** Validates messages using Pydantic, enforcing message length and URL requirements.
- **Fault isolation:** A failure on one platform does not prevent publishing attempts on other platforms.
- **Standardized responses:** Returns a consistent response structure across all platform integrations.
- **Environment-based configuration:** Keeps API credentials and configuration outside the source code.

## Supported Platforms

| Platform | Authentication | Publishing |
|---|---|---|
| Bluesky | App Password | Public posts |
| Telegram | Bot Token | Channel messages |
| Mastodon | Access Token | Public posts |
| DEV Community | API Key | Articles |
| Tumblr | OAuth 1.0a | Draft posts |

**Note:** Tumblr currently creates drafts rather than immediately publishing publicly. Other platforms use the publishing behavior configured in their respective adapters.

## Architecture

The application follows a modular adapter-based architecture.

```text
                  Client Request
                       |
                       v
                FastAPI Application
                       |
                       v
                 Input Validation
                   (Pydantic)
                       |
                       v
                 Posting Service
                       |
              asyncio.gather()
                       |
          +------------+------------+
          |            |            |
          v            v            v
       Bluesky      Telegram     Mastodon
          |            |            |
          v            v            v
       DEV.to        Tumblr      External APIs
          |            |
          +------------+
                       |
                       v
               Platform Results
                       |
                       v
                Unified Response
```

### Project Structure

```text
automated_posting_assignment/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── schemas.py
│   │
│   ├── platforms/
│   │   ├── __init__.py
│   │   ├── bluesky.py
│   │   ├── telegram.py
│   │   ├── mastodon.py
│   │   ├── devto.py
│   │   └── tumblr.py
│   │
│   └── services/
│       ├── __init__.py
│       └── posting_service.py
│
├── tests/
│   ├── __init__.py
│   ├── test_posting.py
│   ├── smoke_publish.py
│   └── check_credentials.py
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Technology Stack

- **Python 3.11+**
- FastAPI
- Pydantic
- Pydantic Settings
- HTTPX
- Asyncio
- OAuthLib
- Pytest

## Setup and Installation

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd automated_posting_assignment
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If dependencies have not yet been added to `requirements.txt`, install the required packages:

```bash
pip install fastapi uvicorn httpx pydantic pydantic-settings oauthlib pytest
```

## Environment Configuration

Create a `.env` file in the project root.

Add the following configuration:

```env
# Bluesky
BLUESKY_HANDLE=your_handle.bsky.social
BLUESKY_APP_PASSWORD=your_app_password

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=@your_channel

# Mastodon
MASTODON_BASE_URL=https://mastodon.social
MASTODON_ACCESS_TOKEN=your_access_token

# DEV Community
DEV_API_KEY=your_dev_api_key

# Tumblr - OAuth 1.0a
TUMBLR_CONSUMER_KEY=your_consumer_key
TUMBLR_CONSUMER_SECRET=your_consumer_secret
TUMBLR_OAUTH_TOKEN=your_oauth_token
TUMBLR_OAUTH_TOKEN_SECRET=your_oauth_token_secret
TUMBLR_BLOG_NAME=yourblog.tumblr.com
TUMBLR_REDIRECT_URI=http://localhost:8000/auth/tumblr/callback/
```

### Obtaining Platform Credentials

**Bluesky**
- Create a Bluesky account.
- Generate an App Password from account settings.
- Use your handle and App Password.

**Telegram**
- Create a bot using BotFather.
- Obtain the bot token.
- Add the bot to your channel with permission to publish messages.
- Configure the channel username or ID.

**Mastodon**
- Log in to your Mastodon instance.
- Create an application in development settings.
- Generate an access token with appropriate publishing permissions.

**DEV Community**
- Generate an API key from your DEV account settings.
- Configure the key in the environment file.

**Tumblr**
- Register an application in the Tumblr developer portal.
- Obtain the Consumer Key and Consumer Secret.
- Obtain the OAuth Token and OAuth Token Secret.
- Configure your Tumblr blog hostname.

Keep all credentials private. Never commit `.env` to version control.

## Running the Application

### 1. Start the FastAPI server

From the project root:

```bash
uvicorn app.main:app --reload
```

The server will typically be available at:

```text
http://127.0.0.1:8000
```

### 2. Access API documentation

Open:

```text
http://127.0.0.1:8000/docs
```

FastAPI Swagger UI provides an interactive interface to inspect and test the available API endpoints.

### 3. Publish content

Use the posting endpoint exposed by the application.

Example request body:

```json
{
  "message": "Testing my automated multi-platform posting system https://example.com"
}
```

The application validates the request and distributes the message through the configured platform adapters.

**Validation rules:**
- Message must not be empty.
- Maximum message length is 200 characters.
- Exactly one valid HTTP/HTTPS URL must be present.
- Messages containing multiple URLs are rejected.

Use the actual route shown in the Swagger documentation when making requests.

## Testing

The project includes tests for request validation and scripts for checking platform credentials and publishing.

### 1. Validate platform credentials

```bash
python -m tests.check_credentials
```

This checks authentication with Bluesky, Telegram, Mastodon, DEV Community, and Tumblr.

### 2. Test individual platform publishing

```bash
python -m tests.smoke_publish
```

This executes a smoke test against all five platform integrations.

**Warning:** This test can publish publicly on Bluesky, Telegram, Mastodon, and DEV Community. Tumblr is configured to create a draft.

### 3. Run unit tests

```bash
pytest tests/test_posting.py -v
```

Run the complete test suite:

```bash
pytest -v
```

## Response Format

Each platform returns a standardized `PlatformResult`.

Example:

```json
{
  "platform": "bluesky",
  "status": "success",
  "posted_url": "https://bsky.app/profile/example/post/123",
  "public_access": true,
  "date": "2026-11-17",
  "time": "12:30:00",
  "error": null
}
```

The overall publishing operation returns a `PostingResponse` containing the success indicator and individual platform results.

A platform failure is recorded independently, allowing other publishing operations to continue.

## Error Handling

The application handles:
- Authentication failures.
- Invalid API responses.
- Network and connection errors.
- Platform-specific publishing failures.
- Invalid user input.
- Unexpected exceptions during publishing.

The posting service isolates individual platform failures and collects the results of all publishing tasks.

## Security Considerations

- Store API credentials in environment variables.
- Never commit `.env` to GitHub.
- Use `.gitignore` to exclude sensitive configuration.
- Avoid logging access tokens, passwords, and API secrets.
- Use HTTPS for production API communication.
- Protect OAuth credentials and refresh tokens.
- Apply appropriate access controls to publishing endpoints.

## License

This project is developed as an automated multi-platform content publishing system. Add an appropriate license before distributing it publicly.
