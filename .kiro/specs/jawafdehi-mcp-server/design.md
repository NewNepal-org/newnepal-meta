# Design Document: Jawafdehi MCP Server

## Overview

The Jawafdehi MCP (Model Context Protocol) server is a Python-based MCP server that provides AI assistants with tools to query NewNepal.org data sources. The server exposes six tools across three data sources: NGM (Nepal Governance Modernization) judicial database, NES (Nepal Entity Service) entity database, and Jawafdehi corruption case API. The server is designed for frictionless installation by non-technical users using `uv` package manager and integrates seamlessly with IDEs like VS Code, Kiro, and Cursor.

## Architecture

```mermaid
graph TB
    subgraph "MCP Server Process"
        Server[Jawafdehi MCP Server<br/>Python + mcp library]
        ToolRegistry[Tool Registry]
        
        Server --> ToolRegistry
    end
    
    subgraph "Tool Implementations"
        NGMTool[NGM Query Tool<br/>Priority 0]
        NESTools[NES Tools<br/>Priority 1-3]
        JawafTools[Jawafdehi Tools<br/>Priority 1-2]
        
        ToolRegistry --> NGMTool
        ToolRegistry --> NESTools
        ToolRegistry --> JawafTools
    end
    
    subgraph "Data Sources"
        NGMDB[(NGM PostgreSQL<br/>Judicial Cases)]
        NESAPI[NES API<br/>nes.newnepal.org]
        JawafAPI[Jawafdehi API<br/>portal.jawafdehi.org]
        
        NGMTool --> NGMDB
        NESTools --> NESAPI
        JawafTools --> JawafAPI
    end
```

## Main Workflow

```mermaid
sequenceDiagram
    participant IDE as IDE (Kiro/VS Code)
    participant Server as MCP Server
    participant DataSource as Data Source (NGM/NES/Jawafdehi)
    
    Note over IDE,DataSource: Runtime Usage
    IDE->>Server: Call tool: search_entities(query="Ministry of Finance")
    Server->>DataSource: HTTP GET /api/entities?q=...
    DataSource-->>Server: Return entity results
    Server-->>IDE: Return formatted results
```

## Components and Interfaces

### Component 1: MCP Server Core

**Purpose**: Main server process that implements the Model Context Protocol and manages tool execution

**Interface**:
```python
class JawafMCPServer:
    def __init__(self, config: ConfigManager):
        """Initialize MCP server with configuration"""
        self.config = config
        self.mcp = Server("jawafdehi-mcp")
    
    async def run(self) -> None:
        """Start MCP server and listen for requests"""
```

**Responsibilities**:
- Initialize MCP server using the `mcp` library
- Load configuration from environment with defaults
- Register ALL tool functions decorated with `@mcp_tool` regardless of configuration
- Handle tool invocation requests from IDE
- Route requests to appropriate tool implementations
- Provide error handling and logging

**Tool Registration**:
All tools are registered automatically using the `@self.mcp.tool()` decorator pattern, regardless of whether their required configuration is present:

```python
@self.mcp.tool()
async def ngm_query_judicial(query: str) -> dict:
    """Tool implementation - will check for NGM_DATABASE_URL at runtime"""
    pass
```

The MCP library handles tool discovery and registration when the server starts. Tools check for required configuration at invocation time and return clear error messages if configuration is missing.

### Component 2: Configuration Manager

**Purpose**: Load and validate environment variables for data source connections

**Interface**:
```python
class ConfigManager:
    ngm_database_url: str | None
    jawafdehi_api_url: str  # Default: https://portal.jawafdehi.org
    nes_api_url: str        # Default: https://nes.newnepal.org
    
    @classmethod
    def from_env(cls) -> ConfigManager:
        """Load configuration from environment variables with defaults"""
    
    def get_tool_config(self, tool_name: str) -> dict | None:
        """Get configuration for a specific tool, returns None if not configured"""
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a tool has required configuration"""
```

**Responsibilities**:
- Load environment variables with defaults for API URLs
- NGM_DATABASE_URL is optional (no default)
- JAWAFDEHI_API_URL defaults to https://portal.jawafdehi.org
- NES_API_URL defaults to https://nes.newnepal.org
- Validate configuration per tool
- All tools are registered regardless of configuration
- Provide clear errors when tools are called without required config

### Component 3: NGM Query Tool (Priority 0)

**Purpose**: Execute SQL queries against NGM judicial database

**Required Environment Variables**:
- `NGM_DATABASE_URL`: PostgreSQL connection string

**Interface**:
```python
@mcp_tool(name="ngm_query_judicial")
async def ngm_query_judicial(query: str) -> dict:
    """
    Search judicial cases from Nepal's court system with SQL queries.
    
    Args:
        query: SQL query string (SELECT only, no mutations)
    
    Returns:
        {
            "success": bool,
            "data": {
                "columns": List[str],
                "rows": List[List[Any]],
                "row_count": int
            } | None,
            "error": str | None,
            "query_time_ms": int
        }
    """
```

**Responsibilities**:
- Check if NGM_DATABASE_URL is configured, return error if not
- Establish PostgreSQL connection using NGM_DATABASE_URL
- Validate SQL query (SELECT only, no mutations)
- Execute query with timeout and row limits
- Format results as JSON
- Handle database errors gracefully

**Security Constraints**:
- Only SELECT queries allowed
- No DROP, INSERT, UPDATE, DELETE, ALTER, CREATE
- Query timeout: 30 seconds
- Row limit: 1000 rows per query
- Connection pooling with max 5 connections

### Component 4: NES Entity Tools (Priority 1-3)

**Purpose**: Query and interact with Nepal Entity Service

**Required Environment Variables**:
- `NES_API_URL`: Base URL for NES API (e.g., https://nes.newnepal.org)

**Interface**:
```python
@mcp_tool(name="get_entity")
async def get_entity(entity_id: str) -> dict:
    """
    Get detailed profile of a specific NES entity.
    
    Args:
        entity_id: Entity identifier (e.g., "entity:person/sher-bahadur-deuba")
    
    Returns:
        Complete entity profile with names, relationships, metadata
    """

@mcp_tool(name="search_entities")
async def search_entities(
    query: str,
    entity_type: str = None,
    limit: int = 20
) -> dict:
    """
    Search for persons, organizations, or government bodies in NES.
    
    Args:
        query: Search query string
        entity_type: Filter by type (person, organization, location, project)
        limit: Maximum results to return (default 20, max 100)
    
    Returns:
        {
            "results": List[Dict],
            "total": int,
            "query": str
        }
    """

@mcp_tool(name="submit_nes_change")
async def submit_nes_change(
    action: str,
    payload: dict,
    change_description: str
) -> dict:
    """
    Submit a change to NES queue (Priority 3).
    
    Args:
        action: Action type (ADD_NAME, CREATE_ENTITY, UPDATE_ENTITY)
        payload: Action-specific data
        change_description: Human-readable description
    
    Returns:
        {
            "queue_item_id": int,
            "status": str,
            "message": str
        }
    """
```

**Responsibilities**:
- Check if NES_API_URL is configured, return error if not
- Make HTTP requests to NES API
- Handle authentication if required
- Parse and format entity data
- Implement retry logic for transient failures
- Cache frequently accessed entities (optional)

### Component 5: Jawafdehi Case Tools (Priority 1-2)

**Purpose**: Query Jawafdehi corruption case database

**Required Environment Variables**:
- `JAWAFDEHI_API_URL`: Base URL for Jawafdehi API (e.g., https://portal.jawafdehi.org)

**Interface**:
```python
@mcp_tool(name="get_jawafdehi_case")
async def get_jawafdehi_case(case_id: int) -> dict:
    """
    Get comprehensive details for a specific case.
    Wrapper for /api/cases/{id}
    
    Args:
        case_id: Jawafdehi case ID
    
    Returns:
        Complete case details including entities, timeline, documents
    """

@mcp_tool(name="search_jawafdehi_cases")
async def search_jawafdehi_cases(
    query: str = None,
    status: str = None,
    entity_id: str = None,
    limit: int = 20
) -> dict:
    """
    Search for corruption and accountability cases.
    Wrapper for /api/cases/
    
    Args:
        query: Text search query
        status: Filter by case status
        entity_id: Filter by related entity
        limit: Maximum results (default 20, max 100)
    
    Returns:
        {
            "results": List[Dict],
            "total": int,
            "filters": Dict
        }
    """
```

**Responsibilities**:
- Check if JAWAFDEHI_API_URL is configured, return error if not
- Make HTTP requests to Jawafdehi API
- Handle pagination for search results
- Format case data for AI consumption
- Implement retry logic
- Handle API rate limiting

### Component 6: HTTP Client Manager

**Purpose**: Centralized HTTP client with retry logic and error handling

**Interface**:
```python
class HTTPClientManager:
    def __init__(self, base_url: str, timeout: int = 30):
        """Initialize HTTP client for a specific API"""
    
    async def get(self, path: str, params: dict = None) -> dict:
        """Execute GET request with retry logic"""
    
    async def post(self, path: str, json: dict = None) -> dict:
        """Execute POST request with retry logic"""
```

**Responsibilities**:
- Manage HTTP sessions and connection pooling
- Implement exponential backoff retry logic
- Handle timeouts and network errors
- Log requests and responses
- Parse JSON responses

### Component 7: Database Connection Manager

**Purpose**: Manage PostgreSQL connections for NGM queries

**Interface**:
```python
class DatabaseManager:
    def __init__(self, database_url: str):
        """Initialize database connection pool"""
    
    async def execute_query(self, query: str) -> QueryResult:
        """Execute SELECT query with safety checks"""
    
    def validate_query(self, query: str) -> None:
        """Validate query is safe (SELECT only)"""
    
    async def close(self) -> None:
        """Close all connections"""
```

**Responsibilities**:
- Manage connection pool (asyncpg)
- Validate SQL queries for safety
- Execute queries with timeout
- Format results
- Handle connection errors

## Data Models

### Tool Response Format

All tools return responses in a consistent format:

```python
{
    "success": bool,
    "data": dict | list | None,
    "error": str | None,
    "query_time_ms": int
}
```

### NGM Query Result

```python
{
    "success": true,
    "data": {
        "columns": ["column1", "column2"],
        "rows": [
            ["value1", "value2"],
            ["value3", "value4"]
        ],
        "row_count": 2
    },
    "error": null,
    "query_time_ms": 45
}
```

**Rationale for rows as list of lists:**
- Minimizes payload size by avoiding repeated column names in each row
- With 1000 row limit and 10 columns, saves ~10,000 repeated key strings
- Standard format used by CSV and database wire protocols
- AI assistants can easily reconstruct dicts: `dict(zip(columns, row))`
- Faster serialization/deserialization

### NES Entity Result

```python
{
    "success": true,
    "data": {
        "id": "entity:person/sher-bahadur-deuba",
        "type": "person",
        "names": [
            {
                "kind": "PRIMARY",
                "en": {"full": "Sher Bahadur Deuba"},
                "ne": {"full": "शेरबहादुर देउबा"}
            }
        ],
        "relationships": [...],
        "metadata": {...}
    },
    "error": null,
    "query_time_ms": 120
}
```

### Jawafdehi Case Result

```python
{
    "success": true,
    "data": {
        "id": 42,
        "title": "Case Title",
        "status": "ACTIVE",
        "entities": [...],
        "timeline": [...],
        "documents": [...]
    },
    "error": null,
    "query_time_ms": 85
}
```

### Configuration Schema

```python
{
    "NGM_DATABASE_URL": "postgresql://user:password@host:5432/ngm_db",  # Optional, no default
    "JAWAFDEHI_API_URL": "https://portal.jawafdehi.org",                # Optional, has default
    "NES_API_URL": "https://nes.newnepal.org"                           # Optional, has default
}
```

**Tool-Specific Requirements**:

| Tool | Required Environment Variable | Default Value |
|------|------------------------------|---------------|
| `ngm_query_judicial` | `NGM_DATABASE_URL` | None (required) |
| `get_entity` | `NES_API_URL` | `https://nes.newnepal.org` |
| `search_entities` | `NES_API_URL` | `https://nes.newnepal.org` |
| `submit_nes_change` | `NES_API_URL` | `https://nes.newnepal.org` |
| `get_jawafdehi_case` | `JAWAFDEHI_API_URL` | `https://portal.jawafdehi.org` |
| `search_jawafdehi_cases` | `JAWAFDEHI_API_URL` | `https://portal.jawafdehi.org` |

**Validation Rules**:
- All tools are registered at server startup regardless of configuration
- NGM_DATABASE_URL has no default - tool fails at runtime if not provided
- JAWAFDEHI_API_URL defaults to `https://portal.jawafdehi.org`
- NES_API_URL defaults to `https://nes.newnepal.org`
- NGM_DATABASE_URL must be valid PostgreSQL connection string (if provided)
- JAWAFDEHI_API_URL and NES_API_URL must be valid HTTPS URLs
- Tools return clear error messages when called without required configuration
- Server starts successfully and registers all tools even if NGM_DATABASE_URL is not configured

## Error Handling

### Error Scenario 1: Missing Configuration

**Condition**: Tool called without required environment variable
**Response**: Tool returns clear error message indicating missing configuration
**Recovery**: User adds required environment variable to MCP config and restarts IDE

**Example for NGM tool**:
```python
{
    "success": false,
    "data": null,
    "error": "NGM_DATABASE_URL environment variable not configured. This tool requires NGM_DATABASE_URL to be set in your MCP settings.",
    "query_time_ms": 0
}
```

**Example for NES tool**:
```python
{
    "success": false,
    "data": null,
    "error": "NES_API_URL environment variable not configured. This tool requires NES_API_URL to be set in your MCP settings.",
    "query_time_ms": 0
}
```

### Error Scenario 2: Database Connection Failure

**Condition**: Cannot connect to NGM PostgreSQL database
**Response**: Return error with connection details (sanitized)
**Recovery**: Check database URL, network connectivity, credentials

```python
{
    "success": false,
    "data": null,
    "error": "Failed to connect to NGM database. Please verify NGM_DATABASE_URL is correct and database is accessible.",
    "query_time_ms": 0
}
```

### Error Scenario 3: Invalid SQL Query

**Condition**: User attempts non-SELECT query or malformed SQL
**Response**: Reject query with validation error
**Recovery**: User corrects query syntax

```python
{
    "success": false,
    "data": null,
    "error": "Invalid query: Only SELECT queries are allowed. Detected forbidden keyword: DROP",
    "query_time_ms": 0
}
```

### Error Scenario 4: API Request Failure

**Condition**: HTTP request to NES or Jawafdehi API fails
**Response**: Return error with retry information
**Recovery**: Automatic retry with exponential backoff (3 attempts)

```python
{
    "success": false,
    "data": null,
    "error": "Failed to fetch entity after 3 attempts. API may be temporarily unavailable.",
    "query_time_ms": 0
}
```

### Error Scenario 5: Query Timeout

**Condition**: Database query or API request exceeds timeout
**Response**: Cancel operation and return timeout error
**Recovery**: User simplifies query or retries

```python
{
    "success": false,
    "data": null,
    "error": "Query timeout after 30 seconds. Please simplify your query or add more specific filters.",
    "query_time_ms": 30000
}
```

## Testing Strategy

### Unit Testing Approach

Test each component in isolation with mocked dependencies:

**Configuration Manager Tests** (`tests/unit/test_config.py`):
- Test loading environment variables (all combinations of present/missing)
- Test `is_tool_enabled()` for each tool
- Test `get_tool_config()` returns correct config or None
- Test validation of URL formats
- Test validation of PostgreSQL connection strings

**SQL Validator Tests** (`tests/unit/test_validators.py`):
- Test SELECT queries are allowed
- Test forbidden keywords are rejected (DROP, INSERT, UPDATE, DELETE, ALTER, CREATE, TRUNCATE)
- Test case-insensitive keyword detection
- Test queries with comments
- Test multi-statement queries (should be rejected)
- Test SQL injection patterns
- Test edge cases (empty query, whitespace only, etc.)

**HTTP Client Manager Tests** (`tests/unit/test_http_client.py`):
- Mock httpx responses
- Test successful GET/POST requests
- Test retry logic with exponential backoff
- Test timeout handling
- Test connection error handling
- Test JSON parsing errors
- Test rate limiting behavior

**Database Manager Tests** (`tests/unit/test_database.py`):
- Mock asyncpg connections
- Test query execution with valid SELECT
- Test query validation before execution
- Test connection pool management
- Test timeout handling
- Test result formatting
- Test connection error handling

**Tool Function Tests** (`tests/unit/test_tools/`):
- Mock all external dependencies (database, HTTP clients)
- Test each tool with valid inputs
- Test each tool with missing configuration
- Test each tool with invalid inputs
- Test error response formatting
- Test metadata generation

**Coverage Goals**: 
- 80%+ line coverage overall
- 100% for critical security functions (SQL validation)
- 100% for configuration validation

**Test Framework**: pytest with pytest-asyncio for async tests

**Example Unit Test**:
```python
# tests/unit/test_validators.py
import pytest
from jawafdehi_mcp.utils.validators import validate_sql_query

def test_select_query_allowed():
    validate_sql_query("SELECT * FROM cases")  # Should not raise

def test_drop_query_rejected():
    with pytest.raises(ValueError, match="forbidden keyword: DROP"):
        validate_sql_query("DROP TABLE cases")

def test_case_insensitive_detection():
    with pytest.raises(ValueError, match="forbidden keyword: DELETE"):
        validate_sql_query("DeLeTe FROM cases WHERE id=1")
```

### Integration Testing Approach

Test tool interactions with real or containerized data sources at low request rates:

**NGM Tool Integration Tests** (`tests/integration/test_ngm.py`):
- Test against PostgreSQL test database with sample judicial data
- Use Docker container with test data
- Test actual query execution
- Test connection pooling
- Test query timeout enforcement
- Test row limit enforcement
- **Rate Limiting**: Not applicable (local database)

**NES Tools Integration Tests** (`tests/integration/test_nes.py`):
- Test against NES production API at low request rate
- Test `get_entity` with known entity IDs
- Test `search_entities` with various queries
- Test error handling for non-existent entities
- Test response parsing and formatting
- **Rate Limiting**: Max 5 requests per minute to avoid overwhelming production API
- Use `pytest-ratelimit` or manual delays between tests

**Jawafdehi Tools Integration Tests** (`tests/integration/test_jawafdehi.py`):
- Test against Jawafdehi production API at low request rate
- Test `get_jawafdehi_case` with known case IDs
- Test `search_jawafdehi_cases` with various filters
- Test pagination handling
- Test error handling for non-existent cases
- **Rate Limiting**: Max 5 requests per minute to avoid overwhelming production API
- Use `pytest-ratelimit` or manual delays between tests

**Test Environment**: 
- Docker Compose with PostgreSQL container for NGM tests
- Real API endpoints for NES and Jawafdehi (with rate limiting)
- Environment variables configured via `.env.test` file

**Example Integration Test**:
```python
# tests/integration/test_nes.py
import pytest
import asyncio
from jawafdehi_mcp.tools.nes import get_entity

@pytest.mark.integration
@pytest.mark.asyncio
async def test_get_entity_real_api():
    """Test get_entity against real NES API (rate limited)"""
    result = await get_entity("entity:person/sher-bahadur-deuba")
    
    assert result["success"] is True
    assert result["data"]["id"] == "entity:person/sher-bahadur-deuba"
    assert result["data"]["type"] == "person"
    assert len(result["data"]["names"]) > 0
    
    # Rate limiting: wait 12 seconds before next test (5 req/min)
    await asyncio.sleep(12)

@pytest.mark.integration
@pytest.mark.asyncio
async def test_search_entities_real_api():
    """Test search_entities against real NES API (rate limited)"""
    result = await search_entities("Ministry of Finance")
    
    assert result["success"] is True
    assert "results" in result["data"]
    assert result["data"]["total"] > 0
    
    # Rate limiting: wait 12 seconds before next test
    await asyncio.sleep(12)
```

**Running Integration Tests**:
```bash
# Run only unit tests (fast, no external dependencies)
uv run pytest tests/unit/

# Run integration tests (slow, requires network and rate limiting)
uv run pytest tests/integration/ -v --tb=short

# Run all tests
uv run pytest
```

### End-to-End Testing Approach

Test complete workflow from IDE to data source:

- **Installation Test**: Verify `uvx` can fetch and run server from GitHub
- **Configuration Test**: Test various MCP config scenarios
- **Tool Invocation Test**: Simulate IDE calling each tool via MCP protocol
- **Error Handling Test**: Verify graceful degradation with missing config
- **Update Test**: Verify automatic updates work correctly

**Note**: E2E tests are manual or semi-automated due to IDE integration requirements

## Performance Considerations

### Query Performance

- **NGM Queries**: 30-second timeout, 1000-row limit
- **API Requests**: 30-second timeout per request
- **Connection Pooling**: Max 5 concurrent database connections
- **HTTP Sessions**: Reuse connections for multiple requests

### Caching Strategy (Optional)

- **Entity Cache**: Cache frequently accessed NES entities (TTL: 1 hour)
- **Case Cache**: Cache Jawafdehi case details (TTL: 30 minutes)
- **Cache Size**: Max 100 MB in-memory cache
- **Cache Invalidation**: LRU eviction policy

### Resource Limits

- **Memory**: Target <100 MB for server process
- **CPU**: Minimal CPU usage when idle
- **Network**: Respect API rate limits (if any)
- **Database**: Limit concurrent connections to avoid overwhelming NGM database

## Security Considerations

### SQL Injection Prevention

- **Query Validation**: Strict whitelist of allowed SQL keywords
- **Parameterization**: Use parameterized queries where possible
- **Read-Only**: Only SELECT queries allowed, no mutations
- **Timeout**: 30-second query timeout to prevent resource exhaustion

### API Security

- **HTTPS Only**: All API requests use HTTPS
- **Credential Storage**: Database credentials in environment variables only
- **No Logging**: Never log sensitive credentials or query results with PII
- **Rate Limiting**: Respect API rate limits to avoid abuse

### Data Privacy

- **Local Processing**: All data processing happens locally
- **No Telemetry**: No usage data sent to external services
- **User Control**: Users control which data sources to enable via config

### Dependency Security

- **Minimal Dependencies**: Use only well-maintained libraries
- **Dependency Scanning**: Regular security audits with `pip-audit`
- **Version Pinning**: Pin dependency versions for reproducibility

## Dependencies

### Core Dependencies

- **mcp**: Model Context Protocol SDK for Python
- **asyncpg**: Async PostgreSQL driver for NGM queries
- **httpx**: Modern async HTTP client for API requests
- **pydantic**: Data validation and settings management
- **python-dotenv**: Environment variable loading (development only)

### Development Dependencies

- **pytest**: Testing framework
- **pytest-asyncio**: Async test support
- **pytest-cov**: Code coverage reporting
- **black**: Code formatting
- **ruff**: Fast Python linter
- **mypy**: Static type checking

### Installation Method

Users install via `uv` without manual dependency management:

```bash
# Automatic installation via MCP config
uvx --from git+https://github.com/NewNepal-org/jawafdehi-mcp jawafdehi-mcp
```

Developers working on the server:

```bash
# Clone and install for development
cd services
git clone https://github.com/NewNepal-org/jawafdehi-mcp.git
cd jawafdehi-mcp
uv sync
uv run pytest
```

## Installation and Setup Process

### For Non-Technical Users

**Step 1**: Install prerequisites (Git and uv)

**Windows**:
```powershell
winget install --id Git.Git -e
winget install --id=astral-sh.uv -e
```

**macOS**:
```bash
brew install uv
```

**Linux**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Step 2**: Get database credentials from NewNepal.org team

**Step 3**: Add MCP configuration to IDE settings file

**Kiro**: `~/.kiro/settings/mcp.json`
**VS Code/Cursor**: Check AI extension documentation

```json
{
  "mcpServers": {
    "newnepal": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/NewNepal-org/jawafdehi-mcp", "jawafdehi-mcp"],
      "env": {
        "NGM_DATABASE_URL": "postgresql://user:password@host:5432/ngm_db"
        // JAWAFDEHI_API_URL and NES_API_URL use defaults if not provided
      }
    }
  }
}
```

**Step 4**: Restart IDE

**Step 5**: Verify tools are available by asking AI assistant

### For Developers

**Step 1**: Clone repository into newnepal-meta

```bash
cd newnepal-meta/services
git clone https://github.com/NewNepal-org/jawafdehi-mcp.git
cd jawafdehi-mcp
```

**Step 2**: Install dependencies

```bash
uv sync
```

**Step 3**: Run tests

```bash
uv run pytest
```

**Step 4**: Update MCP config to use local version

```json
{
  "mcpServers": {
    "newnepal": {
      "command": "uv",
      "args": ["run", "jawafdehi-mcp"],
      "cwd": "/absolute/path/to/newnepal-meta/services/jawafdehi-mcp",
      "env": {
        "NGM_DATABASE_URL": "postgresql://...",
        "JAWAFDEHI_API_URL": "https://portal.jawafdehi.org",
        "NES_API_URL": "https://nes.newnepal.org"
      }
    }
  }
}
```

### Automatic Updates

The server updates automatically on IDE restart:

1. User restarts IDE
2. IDE executes `uvx --from git+https://...`
3. `uv` checks GitHub for latest version
4. If newer version exists, downloads and caches it
5. Starts latest version

No manual update process required for end users.

## Project Structure

```
jawafdehi-mcp/
├── src/
│   └── jawafdehi_mcp/
│       ├── __init__.py
│       ├── server.py           # Main MCP server
│       ├── config.py           # Configuration management
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── ngm.py          # NGM query tool (P0)
│       │   ├── nes.py          # NES tools (P1-P3)
│       │   └── jawafdehi.py   # Jawafdehi tools (P1-P2)
│       ├── clients/
│       │   ├── __init__.py
│       │   ├── http.py         # HTTP client manager
│       │   └── database.py     # Database manager
│       └── utils/
│           ├── __init__.py
│           ├── validators.py   # SQL validation
│           └── formatters.py   # Response formatting
├── tests/
│   ├── unit/
│   │   ├── test_config.py
│   │   ├── test_validators.py
│   │   ├── test_http_client.py
│   │   ├── test_database.py
│   │   └── test_tools/
│   ├── integration/
│   │   ├── test_ngm.py
│   │   ├── test_nes.py
│   │   └── test_jawafdehi.py
│   └── e2e/
├── scripts/
│   └── format.sh               # Code formatting script
├── pyproject.toml              # uv project configuration
├── README.md
├── LICENSE
└── .github/
    └── workflows/
        └── ci.yml              # CI/CD pipeline
```

## CI/CD Pipeline

### GitHub Actions Workflow

The CI pipeline runs on every push and pull request to `main` and `develop` branches.

**Workflow File**: `.github/workflows/ci.yml`

```yaml
name: CI
on:
  push:
    branches: ['main*', 'develop*']
  pull_request:
    branches: ['main*', 'develop*']

jobs:
  test-and-lint:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_ngm
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    env:
      NGM_DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_ngm
      # NES and Jawafdehi API URLs not set - integration tests will be skipped
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Install uv
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"
      
      - name: Set up Python
        run: uv python install 3.12
      
      - name: Install dependencies
        run: uv sync
      
      - name: Check formatting
        run: uv run ruff format --check .
      
      - name: Run linter
        run: uv run ruff check .
      
      - name: Run type checker
        run: uv run mypy src/
      
      - name: Run unit tests
        run: uv run pytest tests/unit/ -v --tb=short --cov=src/jawafdehi_mcp --cov-report=term-missing
      
      - name: Run integration tests (NGM only)
        run: uv run pytest tests/integration/test_ngm.py -v --tb=short
      
      # NES and Jawafdehi integration tests are skipped in CI
      # They require API credentials and should respect rate limits
```

### CI Pipeline Stages

1. **Setup**:
   - Checkout code
   - Install uv package manager
   - Set up Python 3.12
   - Install dependencies with `uv sync`
   - Start PostgreSQL service for NGM tests

2. **Code Quality**:
   - Check code formatting with `ruff format --check`
   - Run linter with `ruff check`
   - Run type checker with `mypy`

3. **Testing**:
   - Run all unit tests with coverage reporting
   - Run NGM integration tests (against PostgreSQL service)
   - Skip NES/Jawafdehi integration tests (require API access and rate limiting)

4. **Coverage Reporting**:
   - Generate coverage report
   - Fail if coverage drops below 80%

### Format Script

**File**: `scripts/format.sh`

```bash
#!/bin/bash
set -e

if [ "$1" = "--check" ]; then
    echo "Checking code formatting..."
    uv run ruff format --check .
    uv run ruff check .
else
    echo "Formatting code..."
    uv run ruff format .
    uv run ruff check --fix .
fi
```

### Local Development Commands

```bash
# Format code
./scripts/format.sh

# Check formatting (CI mode)
./scripts/format.sh --check

# Run all unit tests
uv run pytest tests/unit/

# Run all tests with coverage
uv run pytest --cov=src/jawafdehi_mcp --cov-report=html

# Run specific test file
uv run pytest tests/unit/test_validators.py -v

# Run integration tests (requires API access)
uv run pytest tests/integration/ -v
```

### CI Environment Variables

| Variable | CI Value | Purpose |
|----------|----------|---------|
| `NGM_DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/test_ngm` | PostgreSQL test database |
| `NES_API_URL` | Not set | NES integration tests skipped in CI |
| `JAWAFDEHI_API_URL` | Not set | Jawafdehi integration tests skipped in CI |

### Coverage Requirements

- Minimum 80% overall coverage
- 100% coverage for security-critical code (SQL validation)
- Coverage report generated on every CI run
- Pull requests must maintain or improve coverage

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Configuration Loading

*For any* set of environment variables provided at startup, the MCP server should successfully load them and enable tools that have their required configuration present.

**Validates: Requirements 1.1, 1.3, 1.4, 1.5, 1.6, 11.4**

### Property 2: Graceful Configuration Errors

*For any* tool invoked without its required environment variable, the tool should return an error response with success=false and an error message indicating which environment variable is missing.

**Validates: Requirements 1.7, 13.1**

### Property 3: SQL Query Validation

*For any* SQL query containing forbidden keywords (DROP, INSERT, UPDATE, DELETE, ALTER, CREATE, TRUNCATE) in any case combination, the DatabaseManager should reject the query with a validation error indicating the forbidden keyword.

**Validates: Requirements 2.3, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8, 9.9, 13.3, 15.7**

### Property 4: Multi-Statement Query Rejection

*For any* SQL query containing multiple statements (separated by semicolons), the DatabaseManager should reject the query.

**Validates: Requirements 9.10**

### Property 5: Query Execution and Response Format

*For any* valid SELECT query executed against the NGM database, the response should include columns (as list of strings), rows (as list of lists), and row_count (as integer).

**Validates: Requirements 2.2, 2.4**

### Property 6: HTTP Retry Logic

*For any* HTTP request that fails with a transient error, the HTTPClientManager should retry the request up to 3 times with exponential backoff before returning an error.

**Validates: Requirements 3.5, 4.7, 5.5, 6.5, 8.1, 8.2**

### Property 7: Response Structure Consistency

*For any* tool invocation (successful or failed), the response should contain exactly four fields: success (boolean), data (dict/list/null), error (string/null), and query_time_ms (integer).

**Validates: Requirements 3.7, 10.1, 10.2, 10.3, 10.4**

### Property 8: Entity Response Completeness

*For any* successful get_entity call, the response data should include id, type, names (as list), relationships, and metadata fields.

**Validates: Requirements 3.3**

### Property 9: Search Parameter Handling

*For any* search_entities call with an entity_type filter, the HTTP request should include the entity_type parameter in the query string.

**Validates: Requirements 4.3**

### Property 10: Search Limit Validation

*For any* search_entities or search_jawafdehi_cases call with a limit parameter, if the limit exceeds 100, the tool should cap the limit at 100.

**Validates: Requirements 4.4, 7.5**

### Property 11: Search Response Format

*For any* successful search_entities call, the response data should include results (as list), total (as integer), and query (as string).

**Validates: Requirements 4.6**

### Property 12: Case Search Filter Handling

*For any* search_jawafdehi_cases call with status or entity_id filters, the HTTP request should include those parameters in the query string.

**Validates: Requirements 7.3, 7.4**

### Property 13: Case Response Completeness

*For any* successful get_jawafdehi_case call, the response data should include id, title, status, entities, timeline, and documents fields.

**Validates: Requirements 6.3**

### Property 14: Jawafdehi Search Response Format

*For any* successful search_jawafdehi_cases call, the response data should include results (as list), total (as integer), and filters (as dict).

**Validates: Requirements 7.7**

### Property 15: Change Submission Response Format

*For any* successful submit_nes_change call, the response data should include queue_item_id (as integer), status (as string), and message (as string).

**Validates: Requirements 5.3**

### Property 16: JSON Parsing Error Handling

*For any* HTTP response with invalid JSON, the HTTPClientManager should handle the parsing error gracefully and return an error response.

**Validates: Requirements 8.6**

### Property 17: URL Validation

*For any* NES_API_URL or JAWAFDEHI_API_URL provided, if the URL does not start with "https://", the ConfigManager should reject it during validation.

**Validates: Requirements 15.1**

### Property 18: Credential Logging Prevention

*For any* log output generated by the MCP server, the output should not contain database connection strings, API keys, or password patterns.

**Validates: Requirements 13.6, 15.3**

## Implementation Phases

### Phase 1: Core Infrastructure (Priority 0)

- Set up project structure with uv
- Implement MCP server core
- Implement configuration manager
- Implement NGM query tool with SQL validation
- Write unit tests for SQL validator
- Create basic documentation

### Phase 2: Priority 1 Tools

- Implement `get_entity` (NES)
- Implement `get_jawafdehi_case` (Jawafdehi)
- Implement HTTP client manager with retry logic
- Write integration tests
- Update documentation

### Phase 3: Priority 2 Tools

- Implement `search_entities` (NES)
- Implement `search_jawafdehi_cases` (Jawafdehi)
- Add pagination support
- Write E2E tests
- Create user setup guide

### Phase 4: Priority 3 Tools

- Implement `submit_nes_change` (NES)
- Add authentication for write operations
- Write comprehensive tests
- Finalize documentation

### Phase 5: Polish and Release

- Performance optimization
- Error message improvements
- Comprehensive testing
- User acceptance testing
- Public release
