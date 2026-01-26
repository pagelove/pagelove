# Developing in Pagelove

Pagelove is a platform for building web applications using standard HTML and CSS, with a unique server-side component (DOMFs) that persists state directly in the DOM.

This document serves as the reference for LLMs and developers building applications on Pagelove.


## Core Concepts

PageLove Server is a Rust HTTP server implementing the CSS Selector Range Unit RFC specification, with DOM filesystem (DOMFs) persistence and HTML microdata extraction.

### Features

- **CSS Selector Range Requests**: Use CSS selectors in HTTP Range headers to request specific DOM elements
- **CRUD Operations**: GET, HEAD, PUT, POST, DELETE with Range support
- **Content Negotiation**: Accept header support for text/html, application/xml, and application/ld+json
- **Microdata Extraction**: Automatic extraction of HTML microdata and conversion to JSON-LD
- **Multi-host Support**: Host header-based routing with complete isolation
- **Resource Budgets**: Configurable operation, memory, and time limits per host
- **ETag Support**: Generation-based ETags for concurrency control
- **Conditional Requests**: If-None-Match and If-Match headers


## Configuration

The server uses HTML microdata for configuration. See `config.example.html` for a complete example.

### Basic Configuration Structure

```html
<!DOCTYPE html>
<html>
<body>
    <section itemscope itemtype="https://pagelove.org/ServerConfig">
        <h1>Server Configuration</h1>

        <meta itemprop="bind-address" content="127.0.0.1:8080"/>

        <div itemprop="budget" itemscope itemtype="https://pagelove.org/TransactionBudget">
            <dl>
                <dt>Operations</dt>
                <dd itemprop="operations">1000000</dd>

                <dt>Memory (bytes)</dt>
                <dd itemprop="memory">10485760</dd>

                <dt>Duration (Milliseconds)</dt>
                <dd itemprop="duration">900</dd>
            </dl>
        </div>

        <meta itemprop="fs-root" content="./data/server.domfs"/>

        <ul>
            <li itemprop="host" itemscope itemtype="https://pagelove.org/HostConfig">
                <h2>The <span itemprop="hostname">example.com</span> host</h2>

                <!-- Optional budget override -->
                <div itemprop="budget" itemscope itemtype="https://pagelove.org/TransactionBudget">
                    <dl>
                        <dt>Duration (Milliseconds)</dt>
                        <dd itemprop="duration">1500</dd>
                    </dl>
                </div>
            </li>
        </ul>
    </section>
</body>
</html>
```

### Configuration Properties

- **bind-address**: IP and port to listen on (e.g., "127.0.0.1:8080")
- **fs-root**: Root directory for host databases
- **budget**: Resource limits
  - **operations**: Maximum number of operations per transaction
  - **memory**: Maximum memory usage in bytes
  - **duration**: Maximum duration in milliseconds
- **host**: Per-host configuration
  - **hostname**: Virtual host name
  - **budget**: Optional budget overrides for this host

The database path for each host is inferred as: `{fs-root}/{hostname}.domfs`


## HTTP API

### GET: Retrieve Documents or Elements

#### Full Document

```bash
curl -H "Host: example.com" http://localhost:8080/document.html
```

#### Element Selection with Range

```bash
curl -H "Host: example.com" \
     -H "Range: selector=.content" \
     http://localhost:8080/document.html
```

#### Content Negotiation

Request JSON-LD (microdata extraction):

```bash
curl -H "Host: example.com" \
     -H "Accept: application/ld+json" \
     http://localhost:8080/document.html
```

Response:

```json
{
  "@context": "http://schema.org",
  "@graph": [
    {
      "@type": "Person",
      "name": "John Doe",
      "email": "john@example.com"
    }
  ]
}
```

### PUT: Replace Documents or Elements

#### Replace Full Document

```bash
curl -X PUT -H "Host: example.com" \
     -H "Content-Type: text/html" \
     -d '<html><body><h1>New Content</h1></body></html>' \
     http://localhost:8080/document.html
```

#### Replace Element with Range

```bash
curl -X PUT -H "Host: example.com" \
     -H "Range: selector=.content" \
     -H "Content-Type: text/html" \
     -d '<div class="content">Updated content</div>' \
     http://localhost:8080/document.html
```

### POST: Append Elements

```bash
curl -X POST -H "Host: example.com" \
     -H "Range: selector=body" \
     -H "Content-Type: text/html" \
     -d '<p>New paragraph</p>' \
     http://localhost:8080/document.html
```

### DELETE: Remove Documents or Elements

#### Delete Full Document

```bash
curl -X DELETE -H "Host: example.com" \
     http://localhost:8080/document.html
```

#### Delete Element with Range

```bash
curl -X DELETE -H "Host: example.com" \
     -H "Range: selector=.obsolete" \
     http://localhost:8080/document.html
```

### Conditional Requests

#### If-None-Match (GET)

```bash
curl -H "Host: example.com" \
     -H "If-None-Match: \"12345\"" \
     http://localhost:8080/document.html
```

Returns 304 Not Modified if ETag matches.

#### If-Match (PUT/POST/DELETE)

```bash
curl -X PUT -H "Host: example.com" \
     -H "If-Match: \"12345\"" \
     -H "Content-Type: text/html" \
     -d '<html><body><h1>Updated</h1></body></html>' \
     http://localhost:8080/document.html
```

Returns 412 Precondition Failed if ETag doesn't match.


## Response Codes

- **200 OK**: Successful GET of full document
- **201 Created**: Successful PUT creating new document
- **204 No Content**: Successful DELETE
- **206 Partial Content**: Successful GET/PUT/POST with Range
- **304 Not Modified**: ETag matches If-None-Match
- **400 Bad Request**: Invalid Range header syntax
- **404 Not Found**: Document not found
- **412 Precondition Failed**: ETag doesn't match If-Match
- **416 Range Not Satisfiable**: Selector doesn't match any elements
- **500 Internal Server Error**: Server error
- **501 Not Implemented**: Unsupported HTTP method
- **503 Service Unavailable**: Budget exceeded

