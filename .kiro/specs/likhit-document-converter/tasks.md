# Implementation Plan: Likhit Document Converter - Library/CLI MVP

## Overview

This implementation plan focuses on building the core Likhit library and CLI tool to get a single document type (CIAA Press Release) working end-to-end. The goal is to establish a working foundation with one complete path before expanding to additional document types or integration layers.

**MVP Scope**: CIAA Press Release PDF → Markdown/JSON output via CLI

**Out of Scope for MVP**: Frontend, API integration, additional document types (Kanun Patrika, Supreme Court Orders)

## Tasks

- [ ] 1. Set up Likhit Library project structure
  - [x] 1.1 Create new repository `github.com/NewNepal-org/likhit`
  - [ ] 1.2 Initialize Poetry project with Python 3.12+
  - [ ] 1.3 Set up directory structure: `likhit/`, `tests/`, `samples/`, `docs/`
  - [ ] 1.4 Configure pyproject.toml with core dependencies (pymupdf, pyyaml)
  - [ ] 1.5 Set up GitHub Actions for CI/CD
  - [ ] 1.6 Create basic README.md with installation instructions
  - _Requirements: 10.1, 10.2_

- [ ] 2. Implement core data models for CIAA Press Release
  - [ ] 2.1 Create DocumentType enum with CIAA_PRESS_RELEASE type
    - Define enum with string value "ciaa-press-release"
    - Implement validation for CLI/API usage
    - _Requirements: 1.1, 1.4_
  
  - [ ] 2.2 Create ExtractionResult dataclass
    - Define fields: title, doc_type, source_url, publication_date, likhit_version, sections, tables, metadata
    - Implement validation for required fields
    - _Requirements: 3.1, 3.2_
  
  - [ ] 2.3 Create Section dataclass
    - Define Section with heading, body, level, subsections
    - Support hierarchical structure
    - _Requirements: 2.6, 2.7, 2.8_
  
  - [ ] 2.4 Create Table dataclass
    - Define Table with headers, rows, caption, index
    - _Requirements: 2.9, 4.7, 4.8_

- [ ] 2.5 Write property test for data model validation
  - **Property 3: Extracted metadata includes required fields**
  - **Validates: Requirements 3.1, 3.2**

- [ ] 3. Implement PDF extraction for CIAA Press Release
  - [ ] 3.1 Create ExtractionStrategy abstract base class
    - Define extract_text() and extract_tables() abstract methods
    - _Requirements: 7.1, 7.2_
  
  - [ ] 3.2 Implement FontBasedStrategy for CIAA PDFs
    - Use pymupdf for text extraction
    - Handle page range filtering
    - Extract font information for structure detection
    - _Requirements: 2.1, 2.2, 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ] 3.3 Implement basic table extraction
    - Extract tables using pymupdf table detection
    - Parse table headers and rows
    - Extract table captions if present
    - _Requirements: 2.9, 4.6, 4.7, 4.8, 4.9_
  
  - [ ] 3.4 Write unit tests for extraction strategies
    - Test font-based extraction with sample CIAA PDF
    - Test page range filtering edge cases
    - Test table extraction with CIAA annual report tables
    - _Requirements: 2.1, 2.2, 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 4. Implement CIAA Press Release handler
  - [ ] 4.1 Create DocumentTypeHandler abstract base class
    - Define get_extraction_strategy(), detect_structure(), extract_metadata(), validate() methods
    - _Requirements: 7.1, 7.4_
  
  - [ ] 4.2 Implement CIAAPressReleaseHandler
    - Implement structure detection for CIAA press releases
    - Extract CIAA-specific metadata (title, date, case details)
    - Detect heading hierarchy based on font sizes
    - Validate extracted structure
    - _Requirements: 1.1, 2.6, 2.7, 2.10_
  
  - [ ] 4.3 Write unit tests for CIAA handler
    - Test structure detection with sample CIAA documents
    - Test metadata extraction accuracy
    - Test validation logic
    - _Requirements: 1.1, 2.6, 2.7, 2.10_

- [ ] 5. Implement output renderers
  - [ ] 5.1 Create OutputRenderer abstract base class
    - Define render() abstract method
    - _Requirements: 5.1, 5.6_
  
  - [ ] 5.2 Implement MarkdownRenderer
    - Generate YAML frontmatter with metadata
    - Render sections with appropriate heading levels
    - Render tables in Markdown table syntax
    - Escape special characters for security
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 10.8_
  
  - [ ] 5.3 Implement JSONRenderer
    - Generate valid JSON structure
    - Include metadata, sections, and tables
    - Represent hierarchical structure
    - Escape special characters for security
    - _Requirements: 5.6, 5.7, 5.8, 5.9, 5.10, 10.7_
  
  - [ ] 5.4 Write property tests for output renderers
    - **Property 6: Markdown output includes YAML frontmatter**
    - **Property 7: JSON output is valid and parseable**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.6, 5.7, 5.8**

- [ ] 6. Implement core extraction pipeline
  - [ ] 6.1 Create main extract() function
    - Validate input parameters (file_path, doc_type, metadata, pages, extract_table)
    - Select appropriate document type handler
    - Invoke extraction strategy
    - Process extracted content through document type handler
    - Render output in requested format
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ] 6.2 Implement input validation
    - Validate file extension (.pdf or .docx)
    - Validate file size (max 50MB)
    - Validate document type
    - Validate page range format
    - Validate metadata fields
    - _Requirements: 1.6, 1.7, 1.8, 1.9, 3.3, 4.3_
  
  - [ ] 6.3 Implement error handling
    - Handle PDF parsing failures
    - Handle text extraction failures
    - Handle table extraction failures
    - Handle empty documents
    - Handle extraction timeouts (60 seconds)
    - Provide descriptive error messages
    - _Requirements: 2.3, 2.4, 2.5, 4.8, 10.3_
  
  - [ ] 6.4 Write property tests for extraction pipeline
    - **Property 1: Valid document types are accepted**
    - **Property 2: Invalid document types are rejected**
    - **Property 4: Page range filtering works correctly**
    - **Property 5: Table extraction returns valid JSON**
    - **Property 11: Unsupported file types are rejected**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 1.8, 4.1, 4.2, 4.3, 4.6, 4.7, 4.8**

- [ ] 7. Implement CLI interface
  - [ ] 7.1 Create CLI entry point with argparse
    - Define `likhit extract` subcommand
    - Add required arguments: INPUT, --type, --out
    - Add optional arguments: --title, --date, --source-url, --pages, --extract-table
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [ ] 7.2 Implement CLI argument validation
    - Validate required arguments are provided
    - Display usage help when arguments are missing
    - _Requirements: 6.7_
  
  - [ ] 7.3 Implement CLI execution logic
    - Invoke extract() function with parsed arguments
    - Write output to specified file
    - Handle errors and display error messages
    - Exit with appropriate exit codes (0 for success, non-zero for failure)
    - _Requirements: 6.1, 6.8, 6.9_
  
  - [ ] 7.4 Write integration tests for CLI
    - Test complete CLI workflows with sample documents
    - Test all CLI flags and options
    - Test error scenarios (missing file, invalid type)
    - Verify output file creation and content
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_

- [ ] 8. Create CIAA sample documents and integration tests
  - [ ] 8.1 Add CIAA sample documents to samples/ directory
    - Add ciaa_press_release_sample.pdf with expected output
    - Add ciaa_annual_report_table_sample.pdf for table extraction testing
    - Document what each sample demonstrates
    - _Requirements: 9.2, 9.3, 10.2_
  
  - [ ] 8.2 Implement integration test framework
    - Create test runner that extracts all sample documents
    - Compare output against expected fixtures
    - Provide diff output for debugging
    - _Requirements: 9.2, 9.3, 9.4_
  
  - [ ] 8.3 Write property-based tests with hypothesis
    - Run at least 100 iterations per property
    - Test all applicable correctness properties for CIAA documents
    - _Requirements: 9.5_

- [ ] 9. Implement security and input sanitization
  - [ ] 9.1 Sanitize user-provided metadata
    - Escape special characters in metadata fields
    - Prevent XSS in output
    - _Requirements: 10.4_
  
  - [ ] 9.2 Validate page range input
    - Prevent injection attacks in page range parsing
    - _Requirements: 10.5_
  
  - [ ] 9.3 Validate output file paths
    - Prevent path traversal attacks
    - _Requirements: 10.6_
  
  - [ ] 9.4 Write security tests
    - Test XSS prevention in metadata
    - Test injection prevention in page ranges
    - Test path traversal prevention
    - _Requirements: 10.4, 10.5, 10.6_

- [ ] 10. Complete library documentation
  - [ ] 10.1 Write comprehensive README.md
    - Add installation instructions
    - Add CLI usage examples for CIAA documents
    - Add Python API examples
    - Document CIAA Press Release document type
    - _Requirements: 10.1_
  
  - [ ] 10.2 Document sample documents
    - Explain what each CIAA sample demonstrates
    - Provide expected output examples
    - _Requirements: 10.2_

## Notes

- Each task references specific requirements for traceability
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- **MVP Focus**: Get CIAA Press Release working completely before expanding to other document types
- **Future Expansion**: After MVP, add Kanun Patrika and Supreme Court Order handlers, then API and frontend integration
