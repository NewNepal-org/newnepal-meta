# Requirements Document: Jawafdehi MCP Server

## Introduction

The Jawafdehi MCP Server is a Python-based Model Context Protocol (MCP) server that provides AI assistants with tools to query NewNepal.org data sources. The server enables AI assistants in IDEs (VS Code, Kiro, Cursor) to access three critical data sources: NGM (Nepal Governance Modernization) judicial database, NES (Nepal Entity Service) entity database, and Jawafdehi corruption case API. The system is designed for frictionless installation by non-technical users using the `uv` package manager and supports graceful degradation when data sources are unavailable.

## Glossary

- **MCP_Server**: The Python process implementing the Model Context Protocol that exposes tools to AI assistants
- **Tool**: A callable function exposed by the MCP server that AI assistants can invoke
- **NGM**: Nepal Governance Modernization judicial database containing court case data
- **NES**: Nepal Entity Service database containing information about persons, organizations, and government bodies
- **Jawafdehi**: Corruption and accountability case database and API
- **IDE**: Integrated Development Environment (VS Code, Kiro, Cursor)
- **ConfigManager**: Component responsible for loading and validating environment variables
- **HTTPClientManager**: Component managing HTTP requests to external APIs with retry logic
- **DatabaseManager**: Component managing PostgreSQL connections for NGM queries
- **Query_Timeout**: Maximum time allowed for a query to execute (30 seconds)
- **Row_Limit**: Maximum number of rows returned by a query (1000 rows)

## Requirements

### Requirement 1: Server Initialization and Configuration

**User Story:** As a user, I want the MCP server to start successfully regardless of which data sources I have configured, so that I can use available tools without being blocked by missing credentials.

#### Acceptance Criteria

1. WHEN the MCP_Server starts, THE MCP_Server SHALL load environment variables from the runtime environment
2. WHEN the MCP_Server starts, THE MCP_Server SHALL register all six tools regardless of configuration
3. THE ConfigManager SHALL set JAWAFDEHI_API_URL to `https://portal.jawafdehi.org` if not provided
4. THE ConfigManager SHALL set NES_API_URL to `https://nes.newnepal.org` if not provided
5. THE ConfigManager SHALL validate NGM_DATABASE_URL as a valid PostgreSQL connection string when provided
6. THE ConfigManager SHALL validate NES_API_URL as a valid HTTPS URL
7. THE ConfigManager SHALL validate JAWAFDEHI_API_URL as a valid HTTPS URL
8. WHEN ngm_query_judicial is invoked without NGM_DATABASE_URL configured, THE tool SHALL return an error message indicating the missing environment variable

### Requirement 2: NGM Judicial Query Tool

**User Story:** As an AI assistant, I want to execute SQL queries against the NGM judicial database, so that I can retrieve court case information for users.

#### Acceptance Criteria

1. WHEN NGM_DATABASE_URL is not configured, THE ngm_query_judicial tool SHALL return an error message indicating missing configuration
2. WHEN a SELECT query is provided, THE ngm_query_judicial tool SHALL execute the query against the NGM database
3. WHEN a query contains forbidden keywords (DROP, INSERT, UPDATE, DELETE, ALTER, CREATE, TRUNCATE), THE ngm_query_judicial tool SHALL reject the query with a validation error
4. WHEN a query executes successfully, THE ngm_query_judicial tool SHALL return results with columns (list of column names), rows (list of lists containing values), row_count (integer), and query_time_ms (integer)
5. WHEN a query exceeds Query_Timeout, THE ngm_query_judicial tool SHALL cancel the query and return a timeout error
6. WHEN a query returns more than Row_Limit rows, THE ngm_query_judicial tool SHALL limit results to Row_Limit rows
7. THE DatabaseManager SHALL use connection pooling with a maximum of 5 concurrent connections
8. WHEN a database connection fails, THE ngm_query_judicial tool SHALL return an error message with sanitized connection details

### Requirement 3: NES Entity Retrieval

**User Story:** As an AI assistant, I want to retrieve detailed profiles of specific entities from NES, so that I can provide users with information about persons, organizations, and government bodies.

#### Acceptance Criteria

1. WHEN NES_API_URL is not configured, THE get_entity tool SHALL return an error message indicating missing configuration
2. WHEN a valid entity_id is provided, THE get_entity tool SHALL make an HTTP GET request to the NES API
3. WHEN an entity is found, THE get_entity tool SHALL return the complete entity profile including names, relationships, and metadata
4. WHEN an entity is not found, THE get_entity tool SHALL return an error indicating the entity does not exist
5. WHEN an API request fails, THE HTTPClientManager SHALL retry the request up to 3 times with exponential backoff
6. WHEN an API request exceeds Query_Timeout, THE get_entity tool SHALL cancel the request and return a timeout error
7. THE get_entity tool SHALL format entity data in a consistent response structure with success, data, error, and metadata fields

### Requirement 4: NES Entity Search

**User Story:** As an AI assistant, I want to search for entities in NES by query text and type, so that I can help users find relevant persons, organizations, or government bodies.

#### Acceptance Criteria

1. WHEN NES_API_URL is not configured, THE search_entities tool SHALL return an error message indicating missing configuration
2. WHEN a search query is provided, THE search_entities tool SHALL make an HTTP GET request to the NES API with the query parameter
3. WHERE an entity_type filter is provided, THE search_entities tool SHALL include the entity_type in the API request
4. WHEN a limit parameter is provided, THE search_entities tool SHALL limit results to the specified number (maximum 100)
5. WHEN no limit is provided, THE search_entities tool SHALL default to 20 results
6. WHEN search results are returned, THE search_entities tool SHALL include results, total count, and query in the response
7. WHEN an API request fails, THE HTTPClientManager SHALL retry the request up to 3 times with exponential backoff

### Requirement 5: NES Change Submission

**User Story:** As an AI assistant, I want to submit changes to the NES queue, so that I can help users add names, create entities, or update entity information.

#### Acceptance Criteria

1. WHEN NES_API_URL is not configured, THE submit_nes_change tool SHALL return an error message indicating missing configuration
2. WHEN a change submission is provided with action, payload, and description, THE submit_nes_change tool SHALL make an HTTP POST request to the NES API
3. WHEN a change is successfully queued, THE submit_nes_change tool SHALL return the queue_item_id, status, and message
4. WHEN a change submission fails validation, THE submit_nes_change tool SHALL return an error with validation details
5. WHEN an API request fails, THE HTTPClientManager SHALL retry the request up to 3 times with exponential backoff

### Requirement 6: Jawafdehi Case Retrieval

**User Story:** As an AI assistant, I want to retrieve detailed information about specific corruption cases, so that I can provide users with comprehensive case details including entities, timeline, and documents.

#### Acceptance Criteria

1. WHEN JAWAFDEHI_API_URL is not configured, THE get_jawafdehi_case tool SHALL return an error message indicating missing configuration
2. WHEN a valid case_id is provided, THE get_jawafdehi_case tool SHALL make an HTTP GET request to the Jawafdehi API
3. WHEN a case is found, THE get_jawafdehi_case tool SHALL return complete case details including entities, timeline, and documents
4. WHEN a case is not found, THE get_jawafdehi_case tool SHALL return an error indicating the case does not exist
5. WHEN an API request fails, THE HTTPClientManager SHALL retry the request up to 3 times with exponential backoff
6. WHEN an API request exceeds Query_Timeout, THE get_jawafdehi_case tool SHALL cancel the request and return a timeout error

### Requirement 7: Jawafdehi Case Search

**User Story:** As an AI assistant, I want to search for corruption cases by query text, status, or related entity, so that I can help users find relevant accountability cases.

#### Acceptance Criteria

1. WHEN JAWAFDEHI_API_URL is not configured, THE search_jawafdehi_cases tool SHALL return an error message indicating missing configuration
2. WHEN a search query is provided, THE search_jawafdehi_cases tool SHALL make an HTTP GET request to the Jawafdehi API with the query parameter
3. WHERE a status filter is provided, THE search_jawafdehi_cases tool SHALL include the status in the API request
4. WHERE an entity_id filter is provided, THE search_jawafdehi_cases tool SHALL include the entity_id in the API request
5. WHEN a limit parameter is provided, THE search_jawafdehi_cases tool SHALL limit results to the specified number (maximum 100)
6. WHEN no limit is provided, THE search_jawafdehi_cases tool SHALL default to 20 results
7. WHEN search results are returned, THE search_jawafdehi_cases tool SHALL include results, total count, and applied filters in the response
8. THE search_jawafdehi_cases tool SHALL handle pagination for large result sets

### Requirement 8: HTTP Client Reliability

**User Story:** As a system component, I want HTTP requests to external APIs to be reliable and resilient, so that transient network failures do not cause permanent errors.

#### Acceptance Criteria

1. WHEN an HTTP request fails with a transient error, THE HTTPClientManager SHALL retry the request with exponential backoff
2. THE HTTPClientManager SHALL attempt a maximum of 3 retries per request
3. WHEN all retry attempts fail, THE HTTPClientManager SHALL return an error indicating the API is unavailable
4. THE HTTPClientManager SHALL reuse HTTP connections for multiple requests to the same API
5. WHEN an HTTP request exceeds Query_Timeout, THE HTTPClientManager SHALL cancel the request and return a timeout error
6. THE HTTPClientManager SHALL parse JSON responses and handle parsing errors gracefully

### Requirement 9: SQL Query Security

**User Story:** As a system administrator, I want SQL queries to be validated for safety, so that users cannot execute destructive operations or SQL injection attacks against the NGM database.

#### Acceptance Criteria

1. THE DatabaseManager SHALL validate all SQL queries before execution
2. WHEN a query contains DROP keyword, THE DatabaseManager SHALL reject the query
3. WHEN a query contains INSERT keyword, THE DatabaseManager SHALL reject the query
4. WHEN a query contains UPDATE keyword, THE DatabaseManager SHALL reject the query
5. WHEN a query contains DELETE keyword, THE DatabaseManager SHALL reject the query
6. WHEN a query contains ALTER keyword, THE DatabaseManager SHALL reject the query
7. WHEN a query contains CREATE keyword, THE DatabaseManager SHALL reject the query
8. WHEN a query contains TRUNCATE keyword, THE DatabaseManager SHALL reject the query
9. THE DatabaseManager SHALL detect forbidden keywords case-insensitively
10. WHEN a query contains multiple statements, THE DatabaseManager SHALL reject the query
11. THE DatabaseManager SHALL use parameterized queries where possible to prevent SQL injection

### Requirement 10: Response Format Consistency

**User Story:** As an AI assistant, I want all tool responses to follow a consistent format, so that I can reliably parse and present results to users.

#### Acceptance Criteria

1. THE MCP_Server SHALL format all tool responses with success, data, error, and query_time_ms fields
2. WHEN a tool executes successfully, THE response SHALL have success=true and data containing results
3. WHEN a tool encounters an error, THE response SHALL have success=false and error containing an error message
4. THE query_time_ms field SHALL contain the execution time in milliseconds as an integer
5. WHEN a tool returns an error, THE error message SHALL be clear and actionable for users
6. THE ngm_query_judicial tool SHALL return rows as a list of lists (not list of dicts) with a separate columns field to minimize payload size

### Requirement 11: Installation and Setup

**User Story:** As a non-technical user, I want to install the MCP server with minimal steps, so that I can start using NewNepal.org data sources in my IDE without complex configuration.

#### Acceptance Criteria

1. WHEN a user adds the MCP server to their IDE configuration with uvx command, THE IDE SHALL automatically download and install the server
2. WHEN a user restarts their IDE, THE IDE SHALL check for server updates and download the latest version if available
3. THE MCP_Server SHALL start successfully and register all tools even when only NGM_DATABASE_URL is missing
4. WHEN a user provides environment variables in the MCP configuration, THE MCP_Server SHALL load them at startup
5. THE installation process SHALL not require manual dependency management or Python environment setup
6. WHEN a user does not provide JAWAFDEHI_API_URL, THE server SHALL use `https://portal.jawafdehi.org` as default
7. WHEN a user does not provide NES_API_URL, THE server SHALL use `https://nes.newnepal.org` as default

### Requirement 12: Performance and Resource Management

**User Story:** As a system administrator, I want the MCP server to use resources efficiently, so that it does not impact IDE performance or overwhelm data sources.

#### Acceptance Criteria

1. THE MCP_Server process SHALL use less than 100 MB of memory during normal operation
2. WHEN the MCP_Server is idle, THE MCP_Server SHALL use minimal CPU resources
3. THE DatabaseManager SHALL limit concurrent database connections to 5
4. WHEN a query exceeds Query_Timeout (30 seconds), THE system SHALL cancel the operation
5. WHEN a query returns more than Row_Limit (1000 rows), THE system SHALL limit the results
6. THE HTTPClientManager SHALL respect API rate limits to avoid overwhelming external services

### Requirement 13: Error Handling and User Feedback

**User Story:** As a user, I want clear error messages when something goes wrong, so that I can understand the problem and take corrective action.

#### Acceptance Criteria

1. WHEN a tool is called without required configuration, THE error message SHALL indicate which environment variable is missing
2. WHEN a database connection fails, THE error message SHALL indicate the connection failed and suggest verifying the database URL
3. WHEN a SQL query is invalid, THE error message SHALL indicate which forbidden keyword was detected
4. WHEN an API request fails after retries, THE error message SHALL indicate the API may be temporarily unavailable
5. WHEN a query times out, THE error message SHALL suggest simplifying the query or adding more specific filters
6. THE MCP_Server SHALL never log sensitive credentials or personally identifiable information

### Requirement 14: Testing and Quality Assurance

**User Story:** As a developer, I want comprehensive automated tests, so that I can confidently make changes without breaking existing functionality.

#### Acceptance Criteria

1. THE project SHALL maintain at least 80% overall code coverage
2. THE SQL validation code SHALL have 100% code coverage
3. THE configuration validation code SHALL have 100% code coverage
4. WHEN unit tests run, THE tests SHALL use mocked dependencies and not require external services
5. WHEN integration tests run against external APIs, THE tests SHALL respect rate limits (maximum 5 requests per minute)
6. THE CI pipeline SHALL run unit tests, integration tests (NGM only), linting, formatting checks, and type checking on every commit
7. WHEN code coverage drops below 80%, THE CI pipeline SHALL fail

### Requirement 15: Security and Data Privacy

**User Story:** As a user, I want my data and credentials to be handled securely, so that sensitive information is not exposed or logged.

#### Acceptance Criteria

1. THE MCP_Server SHALL only accept HTTPS URLs for API endpoints
2. THE MCP_Server SHALL store database credentials only in environment variables
3. THE MCP_Server SHALL never log database credentials or API keys
4. THE MCP_Server SHALL never log query results containing personally identifiable information
5. THE MCP_Server SHALL process all data locally without sending telemetry to external services
6. THE MCP_Server SHALL allow users to control which data sources to enable via configuration
7. THE DatabaseManager SHALL only allow SELECT queries to prevent data modification
