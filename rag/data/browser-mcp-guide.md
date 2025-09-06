# Browser MCP Server Documentation

The Browser MCP Server provides comprehensive web browsing automation capabilities through a set of powerful tools. This server enables AI assistants to interact with web pages, manage bookmarks, control navigation, and handle ad-blocking functionality.

## Server Configuration

- **Name**: browser
- **Description**: Browser automation and web interaction server
- **Port**: 8001
- **Capabilities**: tools

## Available Tools

### Navigation Tools

#### 1. open_url
Opens a specified URL in the browser.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "url": {
      "type": "string",
      "description": "The URL to open"
    }
  },
  "required": ["url"]
}
```

**Example Usage:**
```json
{
  "name": "open_url",
  "arguments": {
    "url": "https://www.example.com"
  }
}
```

**Use Cases:**
- Opening websites for research
- Navigating to specific web applications
- Loading documentation pages

#### 2. go_back
Navigates back to the previous page in browser history.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "go_back",
  "arguments": {}
}
```

**Use Cases:**
- Returning to previous pages during browsing sessions
- Undoing navigation mistakes
- Browsing through page history

#### 3. go_forward
Navigates forward to the next page in browser history.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "go_forward",
  "arguments": {}
}
```

**Use Cases:**
- Moving forward after going back
- Navigating through browser history
- Restoring navigation flow

#### 4. reload_page
Reloads the current page.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "reload_page",
  "arguments": {}
}
```

**Use Cases:**
- Refreshing dynamic content
- Reloading after page errors
- Getting updated information

#### 5. get_current_url
Retrieves the URL of the currently active page.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "get_current_url",
  "arguments": {}
}
```

**Use Cases:**
- Confirming current page location
- Logging navigation history
- Sharing current page information

### Bookmark Management Tools

#### 6. add_bookmark
Adds a bookmark for the current page or a specified URL.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "The title for the bookmark"
    },
    "url": {
      "type": "string",
      "description": "The URL to bookmark (optional, uses current page if not provided)"
    }
  },
  "required": ["title"]
}
```

**Example Usage:**
```json
{
  "name": "add_bookmark",
  "arguments": {
    "title": "OpenAI Documentation",
    "url": "https://platform.openai.com/docs"
  }
}
```

**Use Cases:**
- Saving important pages for later reference
- Building a collection of useful resources
- Organizing research materials

#### 7. remove_bookmark
Removes a bookmark by title or URL.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "identifier": {
      "type": "string",
      "description": "The title or URL of the bookmark to remove"
    }
  },
  "required": ["identifier"]
}
```

**Example Usage:**
```json
{
  "name": "remove_bookmark",
  "arguments": {
    "identifier": "OpenAI Documentation"
  }
}
```

**Use Cases:**
- Cleaning up outdated bookmarks
- Removing duplicate entries
- Managing bookmark collections

#### 8. list_bookmarks
Retrieves a list of all saved bookmarks.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "list_bookmarks",
  "arguments": {}
}
```

**Use Cases:**
- Reviewing saved bookmarks
- Finding previously bookmarked pages
- Managing bookmark organization

### Page Interaction Tools

#### 9. click_element
Clicks on a specified element on the current page.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "selector": {
      "type": "string",
      "description": "CSS selector or XPath for the element to click"
    }
  },
  "required": ["selector"]
}
```

**Example Usage:**
```json
{
  "name": "click_element",
  "arguments": {
    "selector": "#submit-button"
  }
}
```

**Use Cases:**
- Submitting forms
- Clicking buttons and links
- Interacting with web applications

#### 10. fill_form
Fills out form fields on the current page.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "form_data": {
      "type": "object",
      "description": "Key-value pairs where keys are field selectors and values are the data to fill"
    }
  },
  "required": ["form_data"]
}
```

**Example Usage:**
```json
{
  "name": "fill_form",
  "arguments": {
    "form_data": {
      "#username": "john_doe",
      "#email": "john@example.com",
      "#message": "Hello, this is a test message."
    }
  }
}
```

**Use Cases:**
- Automating form submissions
- Filling out contact forms
- Entering search queries

#### 11. get_page_content
Extracts text content from the current page.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "selector": {
      "type": "string",
      "description": "CSS selector to extract specific content (optional, extracts all text if not provided)"
    }
  },
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "get_page_content",
  "arguments": {
    "selector": ".article-content"
  }
}
```

**Use Cases:**
- Extracting article text
- Reading page content
- Gathering information from web pages

#### 12. take_screenshot
Captures a screenshot of the current page.

**Schema:**
```json
{
  "type": "object",
  "properties": {
    "filename": {
      "type": "string",
      "description": "Optional filename for the screenshot"
    }
  },
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "take_screenshot",
  "arguments": {
    "filename": "homepage_capture.png"
  }
}
```

**Use Cases:**
- Documenting web pages
- Capturing visual information
- Creating visual records

### Ad-blocking Tools

#### 13. enable_adblock
Enables ad-blocking functionality.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "enable_adblock",
  "arguments": {}
}
```

**Use Cases:**
- Improving page load times
- Reducing distractions
- Enhancing browsing experience

#### 14. disable_adblock
Disables ad-blocking functionality.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "disable_adblock",
  "arguments": {}
}
```

**Use Cases:**
- Supporting websites that require ads
- Testing ad-supported content
- Troubleshooting page loading issues

#### 15. get_adblock_status
Checks the current status of ad-blocking.

**Schema:**
```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example Usage:**
```json
{
  "name": "get_adblock_status",
  "arguments": {}
}
```

**Use Cases:**
- Verifying ad-block settings
- Debugging browsing issues
- Monitoring ad-blocking status

## Implementation Details

The Browser MCP Server is implemented with the following handler classes:

- **NavigationHandler**: Manages URL navigation, page reloading, and browser history
- **BookmarkHandler**: Handles bookmark creation, deletion, and listing
- **PageHandler**: Manages page interactions like clicking, form filling, and content extraction
- **AdblockHandler**: Controls ad-blocking functionality

## Common Workflows

### Research Workflow
1. Use `open_url` to navigate to a research topic
2. Use `get_page_content` to extract relevant information
3. Use `add_bookmark` to save important pages
4. Use `take_screenshot` to capture visual information

### Form Automation Workflow
1. Use `open_url` to navigate to a form page
2. Use `fill_form` to populate form fields
3. Use `click_element` to submit the form
4. Use `take_screenshot` to confirm submission

### Content Extraction Workflow
1. Use `open_url` to navigate to target page
2. Use `get_page_content` with specific selectors
3. Use `go_back` and `go_forward` to navigate between pages
4. Use `list_bookmarks` to manage saved resources

## Error Handling

The browser server includes robust error handling for:
- Invalid URLs
- Missing page elements
- Network connectivity issues
- Browser automation failures

All commands return appropriate error messages and status codes to help diagnose issues.

## Security Considerations

- The server operates within browser security constraints
- Cross-origin requests are subject to CORS policies
- Ad-blocking helps reduce exposure to malicious ads
- Screenshot functionality respects privacy settings

This comprehensive browser automation server enables powerful web interaction capabilities while maintaining security and reliability.