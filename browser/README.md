# Walls Browser (PySide6)

A minimal Qt6 WebEngine browser with a GUI and a CLI, integrated with the shared_server system under the app name "browser".

- GUI: address bar + back/forward/reload with theme from gui_core, plus Adblock toggle.
- CLI: open URLs, navigate, click elements, add bookmarks, fetch HTML, summarize pages to JSON, manage Adblock (enable/disable/load rules), and fetch bookmarks JSON.

## Requirements

- Python 3.12 (already used by your existing venv)
- Dependencies (installed into the existing venv):
  - PySide6
  - beautifulsoup4
  - lxml

Install (once):

```bash
source <REPO_ROOT>/venv/bin/activate
pip install -r <REPO_ROOT>/browser/requirements.txt
```

## Start the Browser (and its shared server)

The browser app starts a GUI window and registers itself with the shared_server as the app "browser".

```bash
source <REPO_ROOT>/venv/bin/activate
python -m browser.shared_server_integration
```

Keep this process running in its own terminal. Use a second terminal to send commands.

Optional: verify the shared server can see the app

```bash
source <REPO_ROOT>/venv/bin/activate
python -m shared_server.cli status
```

## Sending Commands (recommended)

Use the shared_server CLI to send commands to the running browser app:

```bash
source <REPO_ROOT>/venv/bin/activate
python -m shared_server.cli send browser <command> [key=value ...]
```

List available commands:

```bash
python -m shared_server.cli commands browser
```

## Commands and Examples

- open url=<url>
  - Open a webpage. If no scheme provided, https is assumed.
  - Example:
    - `python -m shared_server.cli send browser open url=https://example.com`

- back
  - Navigate back.
  - Example:
    - `python -m shared_server.cli send browser back`

- forward
  - Navigate forward.
  - Example:
    - `python -m shared_server.cli send browser forward`

- reload
  - Reload the current page.
  - Example:
    - `python -m shared_server.cli send browser reload`

- bookmark_add [url=<url>] [name=<name>]
  - Add a bookmark. If no url is given, uses the current page URL; if no name, uses the url.
  - Bookmarks are stored at: `~/.walls_browser_bookmarks.json`.
  - Examples:
    - `python -m shared_server.cli send browser bookmark_add name=Example url=https://example.com`
    - `python -m shared_server.cli send browser bookmark_add`

- bookmarks_json
  - Returns the bookmarks file as JSON.
  - Example:
    - `python -m shared_server.cli send browser bookmarks_json`

- click selector=<css>
  - Click an element using a CSS selector.
  - Quote your selector properly for your shell.
  - Examples:
    - `python -m shared_server.cli send browser click selector='a[href="/about"]'`
    - `python -m shared_server.cli send browser click selector="#submit"`

- click_text text=<text>
  - Click a link/button whose visible text contains the given value.
  - Example:
    - `python -m shared_server.cli send browser click_text text='Sign in'`

- get_html_sync
  - Returns the current page HTML in the response data (blocking briefly while retrieving).
  - Example:
    - `python -m shared_server.cli send browser get_html_sync`
  - Response (shape):
    - `{ "status": "success", "data": { "html": "<html>..." } }`

- summarize
  - Fetch the current page HTML, then return a JSON summary with title, a content excerpt, and links (with resolved destinations).
  - Example:
    - `python -m shared_server.cli send browser summarize`

### Adblock controls

The browser includes a simple EasyList-compatible blocker. You can enable it via GUI (toggle in the top bar with a shield icon) or via CLI.

- adblock_enable / adblock_disable / adblock_toggle / adblock_status
  - Examples:
    - `python -m shared_server.cli send browser adblock_enable`
    - `python -m shared_server.cli send browser adblock_status`

- adblock_load path=<easylist.txt>
  - Load a single EasyList-format filter text file from disk.

- adblock_load_dir path=<folder>
  - Load all .txt filter files recursively from a directory (e.g., a cloned easylist repo).

- adblock_fetch_easylist [url=<zip_url>]
  - Convenience command to download the EasyList GitHub repository ZIP and load all the .txt rules from it (default master).
  - Example:
    - `python -m shared_server.cli send browser adblock_fetch_easylist`

Note: The current implementation supports network request blocking based on URL rules; full cosmetic filtering is not implemented.

## Alternate CLI Wrapper

You can also use the lightweight wrapper:

```bash
python -m browser.cli <command> [key=value ...]
```

It forwards commands to the same shared_server endpoint. Examples:

```bash
python -m browser.cli open url=https://example.com
python -m browser.cli summarize
python -m browser.cli adblock_fetch_easylist
```

## Tips

- Always keep the GUI process running in a terminal while sending commands from another terminal.
- If you see connection errors, make sure the browser app is still running and registered (check with `python -m shared_server.cli status`).
- CSS selectors often need quotes to avoid shell expansion. For zsh/bash, single quotes are usually easiest.
- get_html_sync waits briefly for the page content; if the page is still loading, you can retry after a moment.
- Some console warnings (e.g., CORS noise) are emitted by webpages and are harmless to the browser itself.

## GUI-only Launch (no CLI)

If you just want the GUI without shared_server integration, you can launch:

```bash
python -m browser.main
```