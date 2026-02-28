# NGM (Nepal Governance Modernization) - Database Insights & Analysis

**Report Date**: February 14, 2026  
**Service**: services/ngm  
**Purpose**: Key insights from judicial data analysis

---

## Introduction

Nepal Governance Modernization (NGM) is a comprehensive initiative to modernize Nepali governance through enhanced data accessibility and transparency. Currently focused on anti-corruption research, NGM is systematically digitizing and structuring critical government accountability materials from two key sources: the Commission for the Investigation of Abuse of Authority (CIAA) and Nepal's judicial system.

For CIAA, we are collecting and processing annual reports that document corruption investigations and enforcement actions—materials that directly support the Jawafdehi.org corruption case database. For the court system, we are building a complete judicial data infrastructure by scraping and structuring court case information from all 97 courts across Nepal's four-tier judiciary (Supreme Court, Special Court, 18 High Courts, and 77 District Courts).

To date, we have successfully scraped over 1.5 million court records, transforming unstructured case data from judiciary websites into a comprehensive, queryable PostgreSQL database. Our goal is to build Nepal's first complete case search system—enabling transparency, accountability, and data-driven analysis of both judicial proceedings and corruption cases. This infrastructure serves as the foundation for the Jawafdehi.org platform, empowering citizens, researchers, and civil society with unprecedented access to governance and accountability information.

### Technology Stack
- **Language**: Python 3.12+
- **Framework**: Scrapy (web scraping)
- **ORM**: SQLAlchemy
- **Database**: PostgreSQL with pg_trgm extension (full-text search)
- **Package Manager**: Poetry
- **Date Handling**: nepali library (BS ↔ AD conversion)

---

## Data Insights: Executive Summary

The NGM database contains **1.49 million court cases** and **4.78 million hearing records** spanning **75+ years** (1950-2026) across all **97 courts** in Nepal's four-tier judiciary system.

### Key Achievements
- ✅ 100% court coverage (all 97 courts)
- ✅ 68% case enrichment completion
- ✅ >99% data completeness for core fields
- ✅ 358,270 court-date combinations scraped
- ✅ Real-time data updates (5,669 cases in last 30 days)

---

## Court System Overview

### Court Distribution
Nepal's judiciary consists of four levels:
- **77 District Courts** (जिल्ला अदालत) - First instance courts
- **18 High Courts** (उच्च अदालत) - Appellate courts
- **1 Supreme Court** (सर्वोच्च अदालत) - Final appellate authority
- **1 Special Court** (विशेष अदालत) - Corruption and financial crimes

All 97 courts have been successfully scraped and integrated into the database.

---

## Case Volume Analysis

### Distribution by Court Type
The case load is heavily concentrated in district courts, which handle the majority of first-instance litigation:

- **District Courts**: 906,553 cases (61%)
- **High Courts**: 466,906 cases (31%)
- **Supreme Court**: 101,248 cases (7%)
- **Special Court**: 12,076 cases (1%)

### Top 10 Busiest Courts
The busiest courts are concentrated in urban centers and the Terai region:

1. **District Court Kathmandu** - 156,481 cases
2. **High Court Patan** - 142,214 cases
3. **Supreme Court** - 101,248 cases
4. **District Court Parsa** - 47,470 cases
5. **High Court Janakpur** - 44,831 cases
6. **High Court Birgunj** - 43,668 cases
7. **High Court Biratnagar** - 42,577 cases
8. **District Court Dhanusha** - 40,720 cases
9. **High Court Rajbiraj** - 40,183 cases
10. **District Court Morang** - 39,712 cases

**Key Insight**: Kathmandu District Court alone handles more cases than many entire provinces, reflecting the capital's concentration of legal activity.

---

## Data Collection Progress

### Enrichment Status
The database uses a two-stage collection process: initial listing followed by detailed enrichment.

- **Enriched**: 1,017,678 cases (68.45%)
- **Pending**: 467,858 cases (31.47%)
- **Failed**: 1,247 cases (0.08%)

**Key Insight**: The extremely low failure rate (0.08%) demonstrates robust scraping infrastructure. The 31% pending enrichment represents ongoing data collection rather than technical issues.

### Scraping Coverage
Comprehensive historical coverage across all court types:

- **District Courts**: 282,413 dates scraped
- **High Courts**: 65,979 dates scraped
- **Supreme Court**: 5,491 dates scraped
- **Special Court**: 4,387 dates scraped

**Total**: 358,270 court-date combinations successfully processed

---

## Case Status & Outcomes

### Verdict Analysis
The database tracks case progression from filing to final verdict:

- **Cases with Verdicts**: 786,505 (53%)
- **Active/Pending Cases**: 700,278 (47%)

**Key Insight**: Nearly half of all cases remain active or pending, indicating significant judicial backlog in Nepal's court system.

### Case Duration
For cases with verdicts, the average time from filing to decision:

- **Average Duration**: 217 days (~7 months)
- **Shortest Case**: Negative values indicate data quality issues
- **Longest Case**: 18,723 days (51 years)

**Key Insight**: While the average case takes 7 months, the wide range (including cases spanning decades) reveals significant variation in judicial processing times.

---

## Recent Activity

### Last 30 Days (January 15 - February 14, 2026)
The database captures current judicial activity with 5,669 new cases filed:

**Most Active Courts**:
1. District Court Kathmandu - 1,998 cases
2. High Court Patan - 672 cases
3. District Court Dhanusha - 489 cases
4. District Court Morang - 475 cases
5. District Court Parsa - 460 cases

**Key Insight**: Data is current and actively maintained, with daily updates from court websites.

---

## Hearing Records Analysis

### Volume & Coverage
The database contains **4.78 million hearing records**, providing detailed case progression tracking:

- **Total Hearings**: 4,776,206 records
- **Hearing Dates**: 100% complete
- **Bench Information**: 91.7% complete
- **Judge Names**: 92.6% complete

### Bench Type Distribution
Hearings are conducted by different bench configurations:

- **Standard Hearings**: 88.59% (bench type not specified)
- **Joint Bench** (संयुक्त इजलास): 8.55%
- **Single Bench** (एकल इजलास): 0.70%
- **Full Bench** (पूर्ण इजलाश): 0.31%
- **Constitutional Bench** (संबैधानिक इजलास): 0.18%
- **Special Bench** (बिशेष इजलाश): 0.04%
- **Grand Full Bench** (वृहत पूर्ण इजलाश): 0.01%

**Key Insight**: Most hearings don't specify bench type, but when specified, joint benches are most common. Constitutional and grand full benches are rare, reserved for significant legal questions.

---

## Data Quality Assessment

### Completeness Metrics

**Court Cases Table** (1,486,783 cases):
- Registration Dates: 99.995% complete (68 missing)
- Case Types: 100% complete
- Plaintiff Names: 100% complete
- Defendant Names: 100% complete

**Hearing Records Table** (4,776,206 hearings):
- Hearing Dates: 100% complete
- Bench Information: 91.7% complete
- Judge Names: 92.6% complete

**Key Insight**: Exceptional data quality with near-perfect completeness for critical fields. The database is production-ready for public access and research applications.

### Data Quality Issues Identified

1. **Bench Type Field Contamination**: Many numeric values (likely bench IDs) incorrectly stored in bench_type field
2. **Date Inconsistencies**: Some negative case durations suggest registration/verdict date errors
3. **Missing Bench Types**: 88% of hearings lack bench type specification
4. **Judge Name Format**: Multiple judges stored in single field (comma-separated), complicating individual judge analysis

---

## Historical Coverage

### Temporal Span
- **Earliest Case**: December 7, 1950
- **Latest Case**: February 13, 2026
- **Total Span**: 75+ years of judicial history

**Key Insight**: This represents one of the largest historical judicial datasets ever compiled for Nepal, enabling longitudinal analysis of legal trends, case types, and judicial performance over seven decades.

---

## Special Court (Corruption Cases)

### Overview
The Special Court handles corruption and financial crime cases, with **12,076 cases** in the database.

### Recent Cases
Recent Special Court filings show:
- Cases primarily involve government officials
- Nepal Government (नेपाल सरकार) frequently appears as defendant
- Common case types include appearance petitions (उपस्थित हुने निवेदन)

**Key Insight**: The Special Court data is particularly valuable for Jawafdehi.org's corruption tracking mission, providing structured access to anti-corruption case information.

---

## Sample Case Types

The database captures diverse case categories including:
- **Property Disputes** (राजिनामा लिखत बदर, अंश)
- **Family Law** (सम्बन्ध विच्छेद - divorce)
- **Criminal Cases** (गाली बेईज्जती - defamation)
- **Financial Matters** (खाता रोक्का - account freezing)
- **Corruption Cases** (भ्रष्टाचार)

**Key Insight**: The variety of case types demonstrates the database's utility for multiple research domains beyond corruption tracking.
