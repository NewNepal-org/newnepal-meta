# Requirements Document: Likhit Document Converter

## Introduction

Likhit (लिखित, meaning "written" or "documented") is a document conversion system that transforms Nepali official documents—PDFs and DOCX files—into structured, machine-readable formats (Markdown and JSON). The system serves the NewNepal.org ecosystem by making content from CIAA press releases, Kanun Patrika issues, court rulings, and similar publications accessible for downstream platforms like Jawafdehi and NGM.

The system consists of three independent services: a standalone Python library with CLI (Likhit), a Django REST API integration (JawafdehiAPI), and a React/TypeScript web frontend (Likhit-frontend). This requirements document captures the functional and non-functional requirements for the CLI nd the core likhit library.

## Glossary

- **Likhit_Library**: Standalone Python library providing core document extraction functionality
- **Likhit_CLI**: Command-line interface built on top of Likhit_Library
- **JawafdehiAPI**: Django REST API service that integrates Likhit_Library
- **Likhit_Frontend**: React/TypeScript web application for document conversion
- **Document_Type**: Enumeration of supported document types (CIAA press release, Kanun Patrika, court order, etc.)
- **Extraction_Strategy**: Pluggable approach for extracting text from documents (font-based, OCR, etc.)
- **Output_Renderer**: Component that converts extracted data to specific output format (Markdown, JSON)
- **ExtractionResult**: Data structure containing extracted document content, metadata, and structure
- **YAML_Frontmatter**: Metadata block at the beginning of Markdown files, enclosed in "---" delimiters
- **DRF_Token**: Django REST Framework authentication token for API access
- **Page_Range**: String specification for filtering document pages (e.g., "1-3" or "5")

## Requirements

### Requirement 1: Document Processing and Format Support

**User Story:** As a data contributor, I want to convert Nepali official documents (PDF and DOCX) of different types, so that I can extract structured data from various government publications.

#### Acceptance Criteria

1. WHEN a user specifies doc_type as "ciaa-press-release", THE Likhit_Library SHALL process CIAA press release documents
2. WHEN a user specifies doc_type as "kanun-patrika", THE Likhit_Library SHALL process Kanun Patrika documents
3. WHEN a user specifies doc_type as "supreme-court-order", THE Likhit_Library SHALL process Supreme Court order documents
4. WHEN a user provides an invalid document type, THE Likhit_Library SHALL return a validation error listing supported types
5. WHERE new document types are added, THE Document_Type enumeration SHALL be extended without modifying existing extraction logic
6. WHEN a user provides a PDF file with .pdf extension, THE Likhit_Library SHALL accept and process the file
7. WHEN a user provides a DOCX file with .docx extension, THE Likhit_Library SHALL accept and process the file
8. WHEN a user provides a file with any other extension, THE Likhit_Library SHALL reject the file with error message "Unsupported file format. Please upload PDF or DOCX file"
9. WHEN a file exceeds 50MB, THE system SHALL reject the upload with HTTP 413 and error message "File size exceeds maximum limit of 50MB"

### Requirement 2: Text and Structure Extraction

**User Story:** As a user, I want to extract text and document structure (headings, paragraphs, lists, tables), so that the output preserves the original organization.

#### Acceptance Criteria

1. WHEN a PDF contains font-based text, THE Likhit_Library SHALL extract text using the font-based extraction strategy
2. WHEN text extraction completes, THE Likhit_Library SHALL return an ExtractionResult containing the extracted text
3. WHEN a PDF is corrupted or encrypted, THE Likhit_Library SHALL return error "Unable to parse PDF. File may be corrupted or encrypted"
4. WHEN a PDF contains no extractable text, THE Likhit_Library SHALL return error "No text content found in document"
5. WHEN extraction exceeds 60 seconds, THE system SHALL terminate the process and return a timeout error
6. WHEN a document contains headings, THE Likhit_Library SHALL identify heading levels (1-6) based on font size and formatting
7. WHEN a document contains paragraphs, THE Likhit_Library SHALL preserve paragraph boundaries in the output
8. WHEN a document contains lists, THE Likhit_Library SHALL identify and format list items appropriately
9. WHEN a document contains tables, THE Likhit_Library SHALL extract table structure with headers and rows
10. WHERE document type handlers are defined, THE system SHALL use type-specific structure detection rules

### Requirement 3: Metadata Management

**User Story:** As a data curator, I want to extract and specify document metadata (title, date, source URL), so that converted documents include proper attribution and context.

#### Acceptance Criteria

1. WHEN extraction completes successfully, THE ExtractionResult SHALL include title, doc_type, and likhit_version fields
2. WHEN a user provides metadata via CLI or API, THE Likhit_Library SHALL include the provided metadata in the output
3. WHEN a user provides publication_date, THE Likhit_Library SHALL validate the date format as YYYY-MM-DD
4. WHEN a user provides source_url, THE Likhit_Library SHALL include it in the output metadata
5. WHERE document type handlers implement metadata extraction, THE system SHALL extract type-specific metadata from document content

### Requirement 4: Page Range and Table Filtering

**User Story:** As a user, I want to extract specific pages or tables from a document, so that I can process only relevant sections of large documents.

#### Acceptance Criteria

1. WHEN a user specifies pages="1-3", THE Likhit_Library SHALL extract only pages 1, 2, and 3
2. WHEN a user specifies pages="5", THE Likhit_Library SHALL extract only page 5
3. WHEN a user provides an invalid page range format, THE Likhit_Library SHALL return error "Invalid page range format. Use format: '1-3' or '5'"
4. WHEN a user specifies a page range exceeding document length, THE Likhit_Library SHALL extract available pages without error
5. WHEN no page range is specified, THE Likhit_Library SHALL extract all pages
6. WHEN a user specifies extract_table=0, THE Likhit_Library SHALL extract the first table from the document
7. WHEN a table is extracted, THE output SHALL include headers array and rows array
8. WHEN a user requests a table index that doesn't exist, THE Likhit_Library SHALL return error "Table index {index} not found. Document contains {count} tables"
9. WHEN a table has a caption, THE extracted table SHALL include the caption field
10. WHEN extract_table is specified, THE output format SHALL be JSON

### Requirement 5: Output Formats

**User Story:** As a user, I want documents converted to Markdown or JSON format, so that I can use the structured data in different contexts.

#### Acceptance Criteria

1. WHEN output_format is "markdown", THE Output_Renderer SHALL generate Markdown-formatted text
2. WHEN rendering Markdown output, THE Output_Renderer SHALL include YAML frontmatter enclosed in "---" delimiters
3. WHEN rendering YAML frontmatter, THE Output_Renderer SHALL include title, doc_type, likhit_version, and publication_date fields
4. WHEN rendering document sections, THE Output_Renderer SHALL use appropriate Markdown heading syntax (# for level 1, ## for level 2, etc.)
5. WHEN rendering tables in Markdown, THE Output_Renderer SHALL use Markdown table syntax with proper alignment
6. WHEN output_format is "json", THE Output_Renderer SHALL generate valid JSON
7. WHEN rendering JSON output, THE Output_Renderer SHALL include metadata, sections, and tables as top-level fields
8. WHEN JSON output is generated, THE system SHALL validate that the output is parseable JSON
9. WHEN sections contain subsections, THE JSON SHALL represent the hierarchical structure
10. WHEN tables are present, THE JSON SHALL include tables array with headers and rows for each table

### Requirement 6: CLI Interface

**User Story:** As a developer, I want to use a command-line tool to convert documents, so that I can automate document processing in scripts and workflows.

#### Acceptance Criteria

1. WHEN a user runs "likhit extract INPUT --type TYPE --out OUTPUT", THE Likhit_CLI SHALL extract the document and write output to the specified file
2. WHEN a user provides --title flag, THE Likhit_CLI SHALL override the document title in the output
3. WHEN a user provides --date flag, THE Likhit_CLI SHALL include the specified publication date in the output
4. WHEN a user provides --source-url flag, THE Likhit_CLI SHALL include the URL in the output metadata
5. WHEN a user provides --pages flag, THE Likhit_CLI SHALL filter to the specified page range
6. WHEN a user provides --extract-table flag, THE Likhit_CLI SHALL extract only the specified table
7. WHEN required arguments are missing, THE Likhit_CLI SHALL display usage help and exit with error code
8. WHEN extraction succeeds, THE Likhit_CLI SHALL exit with code 0
9. WHEN extraction fails, THE Likhit_CLI SHALL display error message and exit with non-zero code

### Requirement 7: Extensibility and Architecture

**User Story:** As a developer, I want to add new extraction strategies for different document types, so that the system can handle diverse document formats without modifying core extraction logic.

#### Acceptance Criteria

1. WHERE a document type requires specific extraction approach, THE Document_Type handler SHALL specify the appropriate Extraction_Strategy
2. WHEN a new Extraction_Strategy is implemented, THE system SHALL use it without modifying existing strategies
3. WHEN an Extraction_Strategy fails, THE system SHALL return descriptive error indicating which strategy failed
4. WHERE multiple strategies are available, THE Document_Type handler SHALL select the most appropriate strategy based on document characteristics
5. WHEN extraction strategy is not specified for a document type, THE system SHALL use the default font-based strategy
6. WHERE the Likhit_Library is installed, THE system SHALL require only core dependencies (PDF library, python-docx, pyyaml)
7. WHERE advanced features are needed, THE system SHALL support optional dependencies as extras (e.g., tables extra for camelot-py)

### Requirement 8: Output Consistency and Determinism

**User Story:** As a developer, I want CLI and API to produce identical output for the same input, so that I can use either interface interchangeably.

#### Acceptance Criteria

1. WHEN a document is extracted via CLI and API with identical parameters, THE output content SHALL be identical
2. WHEN a document is extracted multiple times with identical parameters, THE output SHALL be identical (deterministic)
3. WHEN metadata is provided, THE output SHALL include the metadata consistently
4. WHEN page range is specified, THE filtered output SHALL be consistent across runs
5. WHEN table extraction is requested, THE table output SHALL be consistent across runs

### Requirement 9: Testing and Quality Assurance

**User Story:** As a developer, I want comprehensive test coverage with real document samples, so that I can confidently make changes without breaking existing functionality.

#### Acceptance Criteria

1. WHEN unit tests run, THE test suite SHALL achieve at least 80% code coverage for Likhit_Library
2. WHEN integration tests run, THE test suite SHALL extract sample documents and compare against expected outputs
3. WHEN sample documents are added to samples/ directory, THE integration tests SHALL automatically include them
4. WHEN extraction output differs from expected output, THE test suite SHALL provide diff output for debugging
5. WHERE property-based tests are implemented, THE test suite SHALL run at least 100 iterations per property

### Requirement 10: Documentation and Security

**User Story:** As a user, I want comprehensive documentation and secure input handling, so that I can use the system safely and effectively.

#### Acceptance Criteria

1. WHEN the Likhit_Library is published, THE repository SHALL include README with installation instructions and CLI examples
2. WHERE sample documents are provided, THE documentation SHALL explain what each sample demonstrates
3. WHEN errors occur, THE error messages SHALL include actionable guidance for resolution
4. WHEN user-provided metadata is included in output, THE system SHALL sanitize special characters to prevent XSS
5. WHEN page range is parsed, THE system SHALL validate the format to prevent injection attacks
6. WHEN output file paths are specified, THE system SHALL prevent path traversal attacks
7. WHEN JSON output is generated, THE system SHALL escape special characters appropriately
8. WHEN Markdown output is generated, THE system SHALL escape special characters to prevent injection
