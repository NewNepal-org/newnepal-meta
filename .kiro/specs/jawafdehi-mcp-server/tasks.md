# Implementation Plan: Jawafdehi MCP Server

## Overview

This implementation plan creates a Python-based MCP (Model Context Protocol) server that provides AI assistants with tools to query NewNepal.org data sources. The server exposes six tools across three data sources: NGM judicial database, NES entity database, and Jawafdehi corruption case API. Implementation follows a phased approach prioritizing core infrastructure and high-priority tools first.

## Tasks

- [ ] 1. Phase 1: Core Infrastructure and Priority 0 Tools
  - [ ] 1.1 Set up project structure with uv package manager
    - Create `services/jawafdehi-mcp/` directory structure
    - Initialize `pyproject.toml` with uv configuration
    - Set up `src/jawafdehi_mcp/` package structure
    - Create `tests/` directory with unit, integration, and e2e subdirectories
    - Add `.gitignore` for Python projects
    - _Requirements: 11.5_

  - [ ] 1.2 Implement configuration manager
    - Create `src/jawafdehi_mcp/config.py` with `ConfigManager` class
    - Implement `from_env()` class method to load environment variables with defaults
    - Set JAWAFDEHI_API_URL default to `https://portal.jawafdehi.org`
    - Set NES_API_URL default to `https://nes.newnepal.org`
    - NGM_DATABASE_URL has no default (optional)
    - Implement `get_tool_config()` method to return tool-specific configuration
    - Implement `is_tool_enabled()` method to check if tool has required config
    - Add validation for PostgreSQL connection strings (NGM_DATABASE_URL)
    - Add validation for HTTPS URLs (NES_API_URL, JAWAFDEHI_API_URL)
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 1.6, 1.7, 11.6, 11.7, 15.1_

  - [ ]* 1.3 Write unit tests for configuration manager
    - **Property 1: Configuration Loading**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 11.4, 11.6, 11.7**
    - Test loading all environment variables
    - Test loading partial environment variables (NGM_DATABASE_URL missing)
    - Test loading no environment variables (all defaults applied)
    - Test JAWAFDEHI_API_URL defaults to `https://portal.jawafdehi.org`
    - Test NES_API_URL defaults to `https://nes.newnepal.org`
    - Test NGM_DATABASE_URL has no default
    - Test URL validation (HTTPS requirement)
    - Test PostgreSQL connection string validation
    - Test `is_tool_enabled()` for each tool
    - Test `get_tool_config()` returns correct config or None
    - _Requirements: 14.1, 14.2, 14.3_

  - [ ] 1.4 Implement SQL query validator
    - Create `src/jawafdehi_mcp/utils/validators.py`
    - Implement `validate_sql_query()` function
    - Check for forbidden keywords (DROP, INSERT, UPDATE, DELETE, ALTER, CREATE, TRUNCATE)
    - Implement case-insensitive keyword detection
    - Detect and reject multi-statement queries (semicolon-separated)
    - _Requirements: 2.3, 9.1-9.10, 15.7_

  - [ ]* 1.5 Write unit tests for SQL validator
    - **Property 3: SQL Query Validation**
    - **Property 4: Multi-Statement Query Rejection**
    - **Validates: Requirements 2.3, 9.1-9.10, 13.3, 15.7**
    - Test SELECT queries are allowed
    - Test each forbidden keyword is rejected (DROP, INSERT, UPDATE, DELETE, ALTER, CREATE, TRUNCATE)
    - Test case-insensitive keyword detection
    - Test multi-statement query rejection
    - Test queries with comments
    - Test SQL injection patterns
    - Test edge cases (empty query, whitespace only)
    - _Requirements: 14.1, 14.2, 14.3_

  - [ ] 1.6 Implement database connection manager
    - Create `src/jawafdehi_mcp/clients/database.py` with `DatabaseManager` class
    - Implement connection pooling with asyncpg (max 5 connections)
    - Implement `execute_query()` method with timeout (30 seconds)
    - Implement row limit enforcement (1000 rows)
    - Integrate SQL query validation before execution
    - Add connection error handling with sanitized error messages
    - _Requirements: 2.2, 2.5, 2.6, 2.7, 2.8, 12.3, 12.4_

  - [ ]* 1.7 Write unit tests for database manager
    - **Property 5: Query Execution and Response Format**
    - **Validates: Requirements 2.2, 2.4**
    - Mock asyncpg connections
    - Test query execution with valid SELECT
    - Test query validation before execution
    - Test connection pool management
    - Test timeout handling
    - Test row limit enforcement
    - Test result formatting (columns as list of strings, rows as list of lists, row_count as integer)
    - Test connection error handling
    - _Requirements: 14.1, 14.4_

  - [ ] 1.8 Implement MCP server core
    - Create `src/jawafdehi_mcp/server.py` with `JawafMCPServer` class
    - Initialize MCP server using `mcp` library
    - Load configuration from `ConfigManager` with defaults
    - Register ALL tools with `@self.mcp.tool()` decorator pattern regardless of configuration
    - Tools check for required configuration at invocation time
    - Implement error handling and logging
    - Add main entry point for server startup
    - _Requirements: 1.1, 1.2_

  - [ ] 1.9 Implement NGM query tool
    - Create `src/jawafdehi_mcp/tools/ngm.py`
    - Implement `ngm_query_judicial()` function with `@mcp_tool` decorator
    - Check if NGM_DATABASE_URL is configured, return error if not
    - Use `DatabaseManager` to execute queries
    - Format response with success, data, error, and query_time_ms fields
    - Add query timing tracking
    - Return rows as list of lists (not list of dicts) with separate columns field for efficiency
    - _Requirements: 2.1, 2.2, 2.4, 10.1-10.6_

  - [ ]* 1.10 Write unit tests for NGM query tool
    - **Property 2: Graceful Configuration Errors**
    - **Property 7: Response Structure Consistency**
    - **Validates: Requirements 1.8, 3.7, 10.1-10.4, 13.1**
    - Mock DatabaseManager
    - Test tool with missing NGM_DATABASE_URL configuration (returns error at runtime)
    - Test tool with valid query
    - Test response format (success, data, error, query_time_ms)
    - Test query_time_ms is populated correctly
    - Test rows are returned as list of lists (not list of dicts)
    - Test error response format
    - _Requirements: 14.1, 14.4_

  - [ ] 1.11 Create basic documentation
    - Create `services/jawafdehi-mcp/README.md`
    - Document installation with uvx
    - Document MCP configuration for Kiro, VS Code, Cursor
    - Document environment variables
    - Document NGM query tool usage
    - Add examples for common queries
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [ ] 1.12 Set up CI/CD pipeline
    - Create `.github/workflows/ci.yml`
    - Configure PostgreSQL service for NGM tests
    - Add steps for uv installation and dependency sync
    - Add code formatting check (ruff format --check)
    - Add linting (ruff check)
    - Add type checking (mypy)
    - Add unit test execution with coverage reporting
    - Add NGM integration tests
    - Fail if coverage drops below 80%
    - _Requirements: 14.6, 14.7_

  - [ ] 1.13 Create format script
    - Create `scripts/format.sh`
    - Add formatting with ruff format
    - Add linting with ruff check --fix
    - Add --check mode for CI
    - Make script executable
    - _Requirements: 14.6_

- [ ] 2. Checkpoint - Core infrastructure complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 3. Phase 2: Priority 1 Tools (NES and Jawafdehi Read Operations)
  - [ ] 3.1 Implement HTTP client manager
    - Create `src/jawafdehi_mcp/clients/http.py` with `HTTPClientManager` class
    - Implement connection pooling with httpx
    - Implement `get()` method with retry logic (3 attempts, exponential backoff)
    - Implement `post()` method with retry logic
    - Add timeout handling (30 seconds)
    - Add JSON parsing with error handling
    - Add request/response logging
    - _Requirements: 8.1-8.6_

  - [ ]* 3.2 Write unit tests for HTTP client manager
    - **Property 6: HTTP Retry Logic**
    - **Property 16: JSON Parsing Error Handling**
    - **Validates: Requirements 3.5, 4.7, 5.5, 6.5, 8.1-8.6**
    - Mock httpx responses
    - Test successful GET/POST requests
    - Test retry logic with exponential backoff (3 attempts)
    - Test timeout handling
    - Test connection error handling
    - Test JSON parsing errors
    - Test connection reuse
    - _Requirements: 14.1, 14.4_

  - [ ] 3.3 Implement get_entity tool (NES)
    - Create `src/jawafdehi_mcp/tools/nes.py`
    - Implement `get_entity()` function with `@mcp_tool` decorator
    - Use NES_API_URL from config (defaults to `https://nes.newnepal.org`)
    - Use `HTTPClientManager` to make GET request to NES API
    - Parse entity response (id, type, names, relationships, metadata)
    - Format response with consistent structure
    - Handle entity not found errors
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6, 10.1-10.5_

  - [ ]* 3.4 Write unit tests for get_entity tool
    - **Property 7: Response Structure Consistency**
    - **Property 8: Entity Response Completeness**
    - **Validates: Requirements 3.1-3.7, 10.1-10.4**
    - Mock HTTPClientManager
    - Test tool with default NES_API_URL
    - Test tool with custom NES_API_URL
    - Test tool with valid entity_id
    - Test response format and completeness (id, type, names, relationships, metadata)
    - Test entity not found error handling
    - Test API failure error handling
    - _Requirements: 14.1, 14.4_

  - [ ] 3.5 Implement get_jawafdehi_case tool
    - Add `get_jawafdehi_case()` function to `src/jawafdehi_mcp/tools/jawafdehi.py`
    - Use JAWAFDEHI_API_URL from config (defaults to `https://portal.jawafdehi.org`)
    - Use `HTTPClientManager` to make GET request to Jawafdehi API
    - Parse case response (id, title, status, entities, timeline, documents)
    - Format response with consistent structure
    - Handle case not found errors
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.6, 10.1-10.5_

  - [ ]* 3.6 Write unit tests for get_jawafdehi_case tool
    - **Property 7: Response Structure Consistency**
    - **Property 13: Case Response Completeness**
    - **Validates: Requirements 6.1-6.6, 10.1-10.4**
    - Mock HTTPClientManager
    - Test tool with default JAWAFDEHI_API_URL
    - Test tool with custom JAWAFDEHI_API_URL
    - Test tool with valid case_id
    - Test response format and completeness (id, title, status, entities, timeline, documents)
    - Test case not found error handling
    - Test API failure error handling
    - _Requirements: 14.1, 14.4_

  - [ ]* 3.7 Write integration tests for NES tools
    - Create `tests/integration/test_nes.py`
    - Test `get_entity` against real NES API with known entity IDs
    - Test error handling for non-existent entities
    - Test response parsing and formatting
    - Implement rate limiting (max 5 requests per minute)
    - Use pytest markers for integration tests
    - _Requirements: 14.5_

  - [ ]* 3.8 Write integration tests for Jawafdehi tools
    - Create `tests/integration/test_jawafdehi.py`
    - Test `get_jawafdehi_case` against real Jawafdehi API with known case IDs
    - Test error handling for non-existent cases
    - Test response parsing and formatting
    - Implement rate limiting (max 5 requests per minute)
    - Use pytest markers for integration tests
    - _Requirements: 14.5_

  - [ ] 3.9 Update documentation for Priority 1 tools
    - Document `get_entity` tool usage and examples
    - Document `get_jawafdehi_case` tool usage and examples
    - Add NES_API_URL and JAWAFDEHI_API_URL to environment variable documentation
    - Add troubleshooting section for API errors
    - _Requirements: 11.4_

- [ ] 4. Checkpoint - Priority 1 tools complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Phase 3: Priority 2 Tools (Search Operations)
  - [ ] 5.1 Implement search_entities tool (NES)
    - Add `search_entities()` function to `src/jawafdehi_mcp/tools/nes.py`
    - Use NES_API_URL from config (defaults to `https://nes.newnepal.org`)
    - Accept query, entity_type, and limit parameters
    - Default limit to 20, cap at 100
    - Build query parameters including entity_type filter if provided
    - Use `HTTPClientManager` to make GET request to NES API
    - Parse search response (results, total, query)
    - Format response with consistent structure
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 10.1-10.5_

  - [ ]* 5.2 Write unit tests for search_entities tool
    - **Property 7: Response Structure Consistency**
    - **Property 9: Search Parameter Handling**
    - **Property 10: Search Limit Validation**
    - **Property 11: Search Response Format**
    - **Validates: Requirements 4.1-4.7, 10.1-10.4**
    - Mock HTTPClientManager
    - Test tool with default NES_API_URL
    - Test tool with query parameter
    - Test entity_type filter is included in request
    - Test limit parameter (default 20, max 100)
    - Test response format (results, total, query)
    - Test API failure error handling
    - _Requirements: 14.1, 14.4_

  - [ ] 5.3 Implement search_jawafdehi_cases tool
    - Add `search_jawafdehi_cases()` function to `src/jawafdehi_mcp/tools/jawafdehi.py`
    - Use JAWAFDEHI_API_URL from config (defaults to `https://portal.jawafdehi.org`)
    - Accept query, status, entity_id, and limit parameters
    - Default limit to 20, cap at 100
    - Build query parameters including status and entity_id filters if provided
    - Use `HTTPClientManager` to make GET request to Jawafdehi API
    - Handle pagination for large result sets
    - Parse search response (results, total, filters)
    - Format response with consistent structure
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 10.1-10.5_

  - [ ]* 5.4 Write unit tests for search_jawafdehi_cases tool
    - **Property 7: Response Structure Consistency**
    - **Property 10: Search Limit Validation**
    - **Property 12: Case Search Filter Handling**
    - **Property 14: Jawafdehi Search Response Format**
    - **Validates: Requirements 7.1-7.8, 10.1-10.4**
    - Mock HTTPClientManager
    - Test tool with default JAWAFDEHI_API_URL
    - Test tool with query parameter
    - Test status and entity_id filters are included in request
    - Test limit parameter (default 20, max 100)
    - Test response format (results, total, filters)
    - Test pagination handling
    - Test API failure error handling
    - _Requirements: 14.1, 14.4_

  - [ ]* 5.5 Update integration tests for search operations
    - Add `test_search_entities_real_api()` to `tests/integration/test_nes.py`
    - Test search with various queries and entity_type filters
    - Add `test_search_jawafdehi_cases_real_api()` to `tests/integration/test_jawafdehi.py`
    - Test search with various queries, status, and entity_id filters
    - Maintain rate limiting (max 5 requests per minute)
    - _Requirements: 14.5_

  - [ ] 5.6 Update documentation for Priority 2 tools
    - Document `search_entities` tool usage and examples
    - Document `search_jawafdehi_cases` tool usage and examples
    - Add search query examples and best practices
    - Add pagination guidance
    - _Requirements: 11.4_

- [ ] 6. Checkpoint - Priority 2 tools complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Phase 4: Priority 3 Tools (Write Operations)
  - [ ] 7.1 Implement submit_nes_change tool
    - Add `submit_nes_change()` function to `src/jawafdehi_mcp/tools/nes.py`
    - Use NES_API_URL from config (defaults to `https://nes.newnepal.org`)
    - Accept action, payload, and change_description parameters
    - Use `HTTPClientManager` to make POST request to NES API
    - Parse submission response (queue_item_id, status, message)
    - Format response with consistent structure
    - Handle validation errors from API
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 10.1-10.5_

  - [ ]* 7.2 Write unit tests for submit_nes_change tool
    - **Property 7: Response Structure Consistency**
    - **Property 15: Change Submission Response Format**
    - **Validates: Requirements 5.1-5.5, 10.1-10.4**
    - Mock HTTPClientManager
    - Test tool with default NES_API_URL
    - Test tool with valid action, payload, and description
    - Test response format (queue_item_id, status, message)
    - Test validation error handling
    - Test API failure error handling
    - _Requirements: 14.1, 14.4_

  - [ ]* 7.3 Update integration tests for write operations
    - Add `test_submit_nes_change_real_api()` to `tests/integration/test_nes.py`
    - Test submission with various action types
    - Test validation error handling
    - Maintain rate limiting (max 5 requests per minute)
    - _Requirements: 14.5_

  - [ ] 7.4 Update documentation for Priority 3 tools
    - Document `submit_nes_change` tool usage and examples
    - Document supported action types (ADD_NAME, CREATE_ENTITY, UPDATE_ENTITY)
    - Add payload format examples for each action type
    - Add guidance on change descriptions
    - _Requirements: 11.4_

- [ ] 8. Checkpoint - Priority 3 tools complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Phase 5: Polish and Release
  - [ ] 9.1 Implement response formatter utility
    - Create `src/jawafdehi_mcp/utils/formatters.py`
    - Implement `format_success_response()` function
    - Implement `format_error_response()` function
    - Ensure consistent query_time_ms tracking across all tools
    - Ensure NGM tool returns rows as list of lists (not list of dicts) for efficiency
    - Refactor all tools to use formatter utilities
    - _Requirements: 10.1-10.6_

  - [ ]* 9.2 Write unit tests for response formatter
    - **Property 7: Response Structure Consistency**
    - **Validates: Requirements 10.1-10.5**
    - Test success response format
    - Test error response format
    - Test metadata generation
    - Test timestamp format (ISO 8601)
    - _Requirements: 14.1_

  - [ ] 9.3 Implement credential logging prevention
    - Add logging configuration to `src/jawafdehi_mcp/server.py`
    - Implement log sanitization for database URLs
    - Implement log sanitization for API keys
    - Implement log sanitization for password patterns
    - Add tests to verify no credentials in logs
    - _Requirements: 13.6, 15.3, 15.4_

  - [ ]* 9.4 Write unit tests for logging security
    - **Property 18: Credential Logging Prevention**
    - **Validates: Requirements 13.6, 15.3**
    - Test database URLs are sanitized in logs
    - Test API keys are sanitized in logs
    - Test password patterns are sanitized in logs
    - Test PII is not logged in query results
    - _Requirements: 14.1_

  - [ ] 9.5 Performance optimization
    - Review and optimize database connection pooling
    - Review and optimize HTTP connection reuse
    - Add optional entity caching (TTL: 1 hour, max 100 MB)
    - Add optional case caching (TTL: 30 minutes)
    - Verify memory usage stays under 100 MB
    - _Requirements: 12.1, 12.2, 12.5_

  - [ ] 9.6 Improve error messages
    - Review all error messages for clarity and actionability
    - Add specific guidance for missing configuration errors
    - Add specific guidance for database connection errors
    - Add specific guidance for API errors
    - Add specific guidance for timeout errors
    - _Requirements: 13.1-13.5_

  - [ ]* 9.7 Comprehensive testing review
    - Verify overall code coverage is at least 80%
    - Verify SQL validation has 100% coverage
    - Verify configuration validation has 100% coverage
    - Run all unit tests and verify they pass
    - Run all integration tests and verify they pass
    - _Requirements: 14.1, 14.2, 14.3, 14.6, 14.7_

  - [ ] 9.8 Create comprehensive user documentation
    - Create installation guide for non-technical users
    - Document prerequisites (Git, uv) for each platform (Windows, macOS, Linux)
    - Create MCP configuration examples for Kiro, VS Code, Cursor
    - Document all six tools with usage examples
    - Create troubleshooting guide
    - Add FAQ section
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [ ] 9.9 Create developer documentation
    - Document project structure
    - Document development setup with uv
    - Document testing strategy (unit, integration, E2E)
    - Document CI/CD pipeline
    - Document contribution guidelines
    - Add architecture diagrams
    - _Requirements: 11.5_

  - [ ] 9.10 Security audit
    - Review SQL injection prevention measures
    - Review HTTPS enforcement for API URLs
    - Review credential storage and handling
    - Review logging for sensitive data
    - Review dependency security with pip-audit
    - Document security considerations
    - _Requirements: 15.1-15.7_

  - [ ] 9.11 Create LICENSE and repository metadata
    - Add open source license (MIT or Apache 2.0)
    - Create CONTRIBUTING.md
    - Create CODE_OF_CONDUCT.md
    - Add repository description and topics to GitHub
    - _Requirements: Open source principles_

- [ ] 10. Final checkpoint - Release preparation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at phase boundaries
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- Integration tests validate real API interactions with rate limiting
- The implementation uses Python with async/await patterns throughout
- All tools follow consistent response format for AI assistant consumption
- Server supports graceful degradation when data sources are unavailable
