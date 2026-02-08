# Uranium: Simplified AI-Assisted Data Enrichment Workflow

## Overview

This document outlines a streamlined approach to AI-assisted data enrichment for Jawafdehi and NES. The workflow emphasizes human-in-the-loop review, iterative feedback, and clear separation of concerns.

## Component Diagram

```mermaid
graph TB
    subgraph "Document Source"
        subgraph "Government Sources"
            CIAA[CIAA]
            CIB[CIB]
        end
        Media[Media]
        External[External Sources]
    end
    
    subgraph "Input Processing"
        PDFProc[PDF Processing]
        MetaGen[Metadata Generation]
    end
    
    AI[AI]
    ChangeReq[Change Request]
    Human([Human Reviewer])
    Persistence[Persistence System]
    
    subgraph "External Systems"
        NES[(NES Database<br/>Entities)]
        JDS[(Jawafdehi Database<br/>Cases & Sources)]
    end
    
    CIAA --> PDFProc
    CIB --> PDFProc
    Media --> PDFProc
    External --> PDFProc
    
    PDFProc --> MetaGen
    MetaGen --> AI
    
    AI --> ChangeReq
    ChangeReq --> Human
    
    Human -->|Approve| Persistence
    Human -->|Reject + Feedback| AI
    
    Persistence --> NES
    Persistence --> JDS
    
    style External Systems fill:#f0f0f0
    style Input Processing fill:#e8f4ff
    style ChangeReq fill:#fff4e1
    style Persistence fill:#e1ffe1
```