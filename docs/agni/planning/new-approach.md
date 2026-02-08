# Uranium: Simplified AI-Assisted Data Enrichment Workflow

## Overview

This document outlines a streamlined approach to AI-assisted data enrichment for Jawafdehi and NES. The workflow emphasizes human-in-the-loop review, iterative feedback, and clear separation of concerns.

## Component Diagram

```mermaid
graph TB
    subgraph "Uranium System"
        UI[Web Interface]
        Parser[Document Parser]
        Extractor[AI Extractor]
        Matcher[Entity Matcher]
        Queue[Approval Queue<br/>Hash Map]
        Processor[Batch Processor<br/>Cron Job]
        Validator[Data Validator]
    end
    
    subgraph "External Systems"
        NES[(NES Database<br/>Entities)]
        JDS[(Jawafdehi Database<br/>Cases & Sources)]
    end
    
    Human([Human Reviewer])
    Doc[Source Documents]
    
    Doc --> UI
    Human <--> UI
    
    UI --> Parser
    Parser --> Extractor
    Extractor --> Matcher
    Matcher <--> NES
    Matcher --> UI
    
    UI --> Queue
    Queue --> Processor
    Processor --> Validator
    Validator <--> NES
    Validator <--> JDS
    
    style Uranium System fill:#e1e8ff
    style External Systems fill:#f0f0f0
    style Queue fill:#fff4e1
    style Processor fill:#fff4e1
```

## Workflow Diagram

```mermaid
sequenceDiagram
    actor Human
    participant Uranium
    participant NES as NES Database
    participant JDS as Jawafdehi Database

    Note over Human: Prepare source document<br/>(PDF, government report, etc.)
    
    Human->>Uranium: Upload document + metadata + context
    activate Uranium
    
    Uranium->>Uranium: Parse document
    Uranium->>Uranium: Extract entities, case details
    
    Uranium->>NES: Query existing entities
    NES-->>Uranium: Return matching entities
    Uranium->>Uranium: Match entities & generate proposal
    
    Uranium->>Human: Present proposal for review
    deactivate Uranium
    
    alt Human provides feedback
        Human->>Uranium: Submit feedback/corrections
        activate Uranium
        Uranium->>Uranium: Refine proposal based on feedback
        Uranium->>Human: Present updated proposal
        deactivate Uranium
        Note over Human,Uranium: Feedback loop continues until approved/rejected
    end
    
    alt Human approves
        Human->>Uranium: Approve changes
        activate Uranium
        Uranium->>Uranium: Add to approved queue (hash map)
        Uranium->>Human: ✅ Queued for processing
        deactivate Uranium
        
        Note over Uranium: Cron job runs periodically
        
        activate Uranium
        Uranium->>Uranium: Read approved queue in bulk
        Uranium->>Uranium: Check for entity collisions
        
        alt No collisions detected
            Uranium->>Uranium: Begin transaction
            
            Uranium->>NES: Create/update entities
            activate NES
            NES-->>Uranium: Confirm entity changes
            deactivate NES
            
            Uranium->>JDS: Create JawafEntity records
            activate JDS
            JDS-->>Uranium: Confirm JawafEntity creation
            
            Uranium->>JDS: Create DocumentSource
            JDS-->>Uranium: Confirm DocumentSource creation
            
            Uranium->>JDS: Create/update Case
            JDS-->>Uranium: Confirm Case changes
            deactivate JDS
            
            Uranium->>Uranium: Verify data integrity
            
            alt Verification successful
                Uranium->>Uranium: Commit transaction
                Uranium->>Uranium: Remove from queue
                Note over Uranium: ✅ Changes applied successfully
            else Verification failed
                Uranium->>Uranium: Rollback transaction
                Uranium->>Uranium: Mark for review
                Note over Uranium: ❌ Verification failed, flagged for review
            end
            
        else Collisions detected
            Uranium->>Uranium: Flag conflicting items
            Note over Uranium: ⚠️ Collisions detected, requires manual resolution
        end
        
        deactivate Uranium
        
    else Human rejects
        Human->>Uranium: Reject proposal
        Uranium->>Human: ❌ Proposal discarded
    end
```
