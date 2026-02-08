# AgniAI Human/AI Interaction Example

This document demonstrates a complete workflow of the AgniAI POC system processing a real CIAA (Commission for the Investigation of Abuse of Authority) press release about corruption charges filed against school officials.

## Source Document

**File:** `example.doc` (CIAA Press Release)  
**Date:** 2082.08.29 (Nepali calendar)  
**Subject:** Charges filed against school officials for misappropriation of ICT lab funds

## Workflow Walkthrough

### Stage 1: Document Submission

**Human Action:**
```
> agni process example.doc
```

**System Response:**
```
✓ Document loaded: example.doc (2,847 characters)
✓ Document ID: doc_20241216_143022_a7f3
⏳ Processing through pipeline...
```

---

### Stage 2: AI Extraction

**AI Processing:**

The system sends the document to Gemini 2.5 Flash with structured extraction instructions.

**Extracted Result:**

```json
{
  "metadata": {
    "author": {
      "value": "गणेश बहादुर अधिकारी",
      "confidence": 0.95
    },
    "publication_date": {
      "value": "2082-08-29",
      "confidence": 0.98
    },
    "document_type": {
      "value": "press_release",
      "confidence": 0.99
    },
    "source": {
      "value": "अख्तियार दुरुपयोग अनुसन्धान आयोग",
      "confidence": 0.99
    }
  },
  "entities": [
    {
      "type": "person",
      "name_en": "Dhaniklal Thakur",
      "name_ne": "धनिकलाल ठाकुर",
      "attributes": {
        "role": "प्रधानाध्यापक",
        "role_en": "Principal",
        "organization": "श्री शंकर जनता माध्यमिक विद्यालय",
        "organization_en": "Shree Shankar Janata Secondary School",
        "location": "विदेह नगरपालिका-2, धनुषा"
      },
      "confidence_scores": {
        "name_en": 0.92,
        "name_ne": 0.98,
        "role": 0.95,
        "organization": 0.97
      }
    },
    {
      "type": "person",
      "name_en": "Arun Kumar Kushiyait",
      "name_ne": "अरुण कुमार कुशियैत",
      "attributes": {
        "role": "तत्कालीन लेखापाल",
        "role_en": "Former Accountant",
        "organization": "श्री शंकर जनता माध्यमिक विद्यालय",
        "status": "deceased"
      },
      "confidence_scores": {
        "name_en": 0.88,
        "name_ne": 0.96,
        "role": 0.94,
        "status": 0.99
      }
    },
    {
      "type": "person",
      "name_en": "Kumari Sarita Devi Kushiyait",
      "name_ne": "कुमारी सरिता देवी कुशियैत",
      "attributes": {
        "role": "श्रीमती",
        "role_en": "Wife",
        "relationship": "Wife of Arun Kumar Kushiyait"
      },
      "confidence_scores": {
        "name_en": 0.85,
        "name_ne": 0.97,
        "relationship": 0.96
      }
    },
    {
      "type": "person",
      "name_en": "Ganesh Bahadur Adhikari",
      "name_ne": "गणेश बहादुर अधिकारी",
      "attributes": {
        "role": "सहायक प्रवक्ता",
        "role_en": "Assistant Spokesperson",
        "organization": "अख्तियार दुरुपयोग अनुसन्धान आयोग"
      },
      "confidence_scores": {
        "name_en": 0.94,
        "name_ne": 0.99,
        "role": 0.97
      }
    },
    {
      "type": "organization",
      "name_en": "Commission for the Investigation of Abuse of Authority",
      "name_ne": "अख्तियार दुरुपयोग अनुसन्धान आयोग",
      "attributes": {
        "acronym": "CIAA",
        "location": "टङ्गाल, काठमाडौं",
        "type": "government_body"
      },
      "confidence_scores": {
        "name_en": 0.99,
        "name_ne": 0.99,
        "location": 0.98
      }
    },
    {
      "type": "organization",
      "name_en": "Shree Shankar Janata Secondary School",
      "name_ne": "श्री शंकर जनता माध्यमिक विद्यालय",
      "attributes": {
        "location": "विदेह नगरपालिका-2, दुहवी, गोवराही, धनुषा",
        "type": "educational_institution"
      },
      "confidence_scores": {
        "name_en": 0.91,
        "name_ne": 0.98,
        "location": 0.95
      }
    },
    {
      "type": "organization",
      "name_en": "Videha Municipality",
      "name_ne": "विदेह नगरपालिका",
      "attributes": {
        "district": "धनुषा",
        "type": "local_government"
      },
      "confidence_scores": {
        "name_en": 0.89,
        "name_ne": 0.98,
        "district": 0.96
      }
    },
    {
      "type": "organization",
      "name_en": "Special Court, Kathmandu",
      "name_ne": "विशेष अदालत, काठमाडौं",
      "attributes": {
        "type": "judicial_body",
        "location": "काठमाडौं"
      },
      "confidence_scores": {
        "name_en": 0.93,
        "name_ne": 0.99,
        "type": 0.95
      }
    }
  ]
}
```

---

### Stage 3: Entity Matching

**System Processing:**

The system queries the NES database for each extracted entity to find potential matches.

**Matching Results:**

```
Entity 1: Dhaniklal Thakur (धनिकलाल ठाकुर)
  ❌ No matches found in NES database
  → Recommendation: CREATE NEW ENTITY

Entity 2: Arun Kumar Kushiyait (अरुण कुमार कुशियैत)
  ❌ No matches found in NES database
  → Recommendation: CREATE NEW ENTITY

Entity 3: Kumari Sarita Devi Kushiyait (कुमारी सरिता देवी कुशियैत)
  ❌ No matches found in NES database
  → Recommendation: CREATE NEW ENTITY

Entity 4: Ganesh Bahadur Adhikari (गणेश बहादुर अधिकारी)
  🔍 Found 2 potential matches:
    [1] entity:person/ganesh-adhikari-001 (Similarity: 0.72)
        Name: Ganesh Adhikari / गणेश अधिकारी
        Role: Government Official
    [2] entity:person/ganesh-bahadur-adhikari-ciaa (Similarity: 0.95)
        Name: Ganesh Bahadur Adhikari / गणेश बहादुर अधिकारी
        Role: Assistant Spokesperson, CIAA
  → Recommendation: MATCH TO entity:person/ganesh-bahadur-adhikari-ciaa

Entity 5: CIAA (अख्तियार दुरुपयोग अनुसन्धान आयोग)
  ✓ Found 1 strong match:
    [1] entity:organization/government_body/ciaa (Similarity: 0.99)
        Name: Commission for the Investigation of Abuse of Authority
        Name (NE): अख्तियार दुरुपयोग अनुसन्धान आयोग
  → Recommendation: MATCH TO entity:organization/government_body/ciaa

Entity 6: Shree Shankar Janata Secondary School
  ❌ No matches found in NES database
  → Recommendation: CREATE NEW ENTITY

Entity 7: Videha Municipality (विदेह नगरपालिका)
  ✓ Found 1 strong match:
    [1] entity:organization/local_government/videha-municipality (Similarity: 0.98)
        Name: Videha Municipality / विदेह नगरपालिका
        District: Dhanusha
  → Recommendation: MATCH TO entity:organization/local_government/videha-municipality

Entity 8: Special Court, Kathmandu (विशेष अदालत, काठमाडौं)
  ✓ Found 1 strong match:
    [1] entity:organization/judicial_body/special-court-ktm (Similarity: 0.97)
        Name: Special Court, Kathmandu / विशेष अदालत, काठमाडौं
  → Recommendation: MATCH TO entity:organization/judicial_body/special-court-ktm
```

---

### Stage 4: Change Request Generation & Human Review

**System Display:**

```
═══════════════════════════════════════════════════════════════
                    CHANGE REQUEST REVIEW
═══════════════════════════════════════════════════════════════

Request ID: cr_20241216_143025_b8d9
Document ID: doc_20241216_143022_a7f3

───────────────────────────────────────────────────────────────
DOCUMENT METADATA
───────────────────────────────────────────────────────────────

Author:           गणेश बहादुर अधिकारी [95%]
Publication Date: 2082-08-29 [98%]
Document Type:    press_release [99%]
Source:           अख्तियार दुरुपयोग अनुसन्धान आयोग [99%]

───────────────────────────────────────────────────────────────
ENTITIES TO CREATE (4 new entities)
───────────────────────────────────────────────────────────────

[1] PERSON: Dhaniklal Thakur
    Name (EN):     Dhaniklal Thakur [92%]
    Name (NE):     धनिकलाल ठाकुर [98%]
    Role:          प्रधानाध्यापक (Principal) [95%]
    Organization:  श्री शंकर जनता माध्यमिक विद्यालय [97%]
    Location:      विदेह नगरपालिका-2, धनुषा
    
    ⚠️  LOW CONFIDENCE: name_en (92%)
    
    Explanation: Principal accused of misappropriating ICT lab funds
                 totaling Rs. 8,62,152.65

[2] PERSON: Arun Kumar Kushiyait
    Name (EN):     Arun Kumar Kushiyait [88%] ⚠️
    Name (NE):     अरुण कुमार कुशियैत [96%]
    Role:          तत्कालीन लेखापाल (Former Accountant) [94%]
    Organization:  श्री शंकर जनता माध्यमिक विद्यालय
    Status:        deceased [99%]
    
    ⚠️  LOW CONFIDENCE: name_en (88%)
    
    Explanation: Former accountant accused of colluding in fund
                 misappropriation; deceased

[3] PERSON: Kumari Sarita Devi Kushiyait
    Name (EN):     Kumari Sarita Devi Kushiyait [85%] ⚠️
    Name (NE):     कुमारी सरिता देवी कुशियैत [97%]
    Role:          श्रीमती (Wife)
    Relationship:  Wife of Arun Kumar Kushiyait [96%]
    
    ⚠️  LOW CONFIDENCE: name_en (85%)
    
    Explanation: Wife of deceased accountant; charges filed against
                 her for recovery of misappropriated funds

[4] ORGANIZATION: Shree Shankar Janata Secondary School
    Name (EN):     Shree Shankar Janata Secondary School [91%]
    Name (NE):     श्री शंकर जनता माध्यमिक विद्यालय [98%]
    Location:      विदेह नगरपालिका-2, दुहवी, गोवराही, धनुषा [95%]
    Type:          educational_institution
    
    ⚠️  LOW CONFIDENCE: name_en (91%)
    
    Explanation: School where the alleged corruption occurred

───────────────────────────────────────────────────────────────
ENTITIES TO UPDATE (4 existing entities)
───────────────────────────────────────────────────────────────

[5] MATCH: entity:person/ganesh-bahadur-adhikari-ciaa
    
    Current Data:
      Name (EN): Ganesh Bahadur Adhikari
      Name (NE): गणेश बहादुर अधिकारी
      Role:      Assistant Spokesperson, CIAA
    
    Proposed Updates:
      + Add document reference: CIAA Press Release 2082-08-29
      + Confirm role: सहायक प्रवक्ता
    
    Explanation: Document author; existing entity confirmed

[6] MATCH: entity:organization/government_body/ciaa
    
    Current Data:
      Name (EN): Commission for the Investigation of Abuse of Authority
      Name (NE): अख्तियार दुरुपयोग अनुसन्धान आयोग
      Location:  Tangal, Kathmandu
    
    Proposed Updates:
      + Add document reference: Press Release 2082-08-29
      + Confirm location: टङ्गाल, काठमाडौं
    
    Explanation: Issuing organization; existing entity confirmed

[7] MATCH: entity:organization/local_government/videha-municipality
    
    Current Data:
      Name (EN): Videha Municipality
      Name (NE): विदेह नगरपालिका
      District:  Dhanusha
    
    Proposed Updates:
      + Add case reference: ICT Lab fund misappropriation case
    
    Explanation: Municipality involved in fund allocation

[8] MATCH: entity:organization/judicial_body/special-court-ktm
    
    Current Data:
      Name (EN): Special Court, Kathmandu
      Name (NE): विशेष अदालत, काठमाडौं
    
    Proposed Updates:
      + Add case reference: Charges filed 2082-08-29
    
    Explanation: Court where charges were filed

═══════════════════════════════════════════════════════════════

Actions:
  [a] Approve all changes
  [r] Reject with feedback
  [q] Quit without saving

Your choice:
```

---

### Human Review - First Iteration (Rejection with Feedback)

**Human Action:**
```
> r

Enter feedback (one item per line, use prefixes: processor:, extraction:, matching:):

extraction: Name "Arun Kumar Kushiyait" should be "Arun Kumar Kushiyait" (no change needed but verify spelling)
extraction: Name "Kumari Sarita Devi Kushiyait" - remove "Kumari" prefix, should be "Sarita Devi Kushiyait"
matching: Ganesh Bahadur Adhikari match looks correct but verify he is still Assistant Spokesperson
extraction: School name in English should be "Shree Shankar Janata Secondary School, Duhabi"
```

**System Response:**
```
✓ Feedback recorded
⏳ Reprocessing with feedback...
```

---

### Reprocessing with Feedback

**System Processing:**

The pipeline reruns with feedback routed to appropriate stages:

- **Stage 1 (Processor)**: No processor feedback, re-reads original document
- **Stage 2 (Extraction)**: Receives 3 extraction feedback items as context
- **Stage 3 (Matching)**: Receives 1 matching feedback item for verification
- **Stage 4 (Review)**: Generates updated change request

**Updated Change Request:**

```
═══════════════════════════════════════════════════════════════
                UPDATED CHANGE REQUEST REVIEW
═══════════════════════════════════════════════════════════════

Request ID: cr_20241216_143127_c9e2
Document ID: doc_20241216_143022_a7f3
Previous Request: cr_20241216_143025_b8d9

───────────────────────────────────────────────────────────────
CHANGES FROM PREVIOUS REVIEW
───────────────────────────────────────────────────────────────

✓ Entity [2]: Name verified as "Arun Kumar Kushiyait"
✓ Entity [3]: Name corrected to "Sarita Devi Kushiyait"
✓ Entity [4]: School name updated to include location "Duhabi"
✓ Entity [5]: Ganesh Bahadur Adhikari role verified

───────────────────────────────────────────────────────────────
ENTITIES TO CREATE (4 new entities)
───────────────────────────────────────────────────────────────

[1] PERSON: Dhaniklal Thakur
    [No changes from previous review]

[2] PERSON: Arun Kumar Kushiyait
    Name (EN):     Arun Kumar Kushiyait [95%] ✓
    Name (NE):     अरुण कुमार कुशियैत [96%]
    [Spelling verified per feedback]

[3] PERSON: Sarita Devi Kushiyait
    Name (EN):     Sarita Devi Kushiyait [92%] ✓
    Name (NE):     सरिता देवी कुशियैत [97%]
    Role:          श्रीमती (Wife)
    
    ✓ CORRECTED: Removed "Kumari" prefix per feedback

[4] ORGANIZATION: Shree Shankar Janata Secondary School, Duhabi
    Name (EN):     Shree Shankar Janata Secondary School, Duhabi [94%] ✓
    Name (NE):     श्री शंकर जनता माध्यमिक विद्यालय, दुहवी [98%]
    
    ✓ CORRECTED: Added location "Duhabi" per feedback

───────────────────────────────────────────────────────────────
ENTITIES TO UPDATE (4 existing entities)
───────────────────────────────────────────────────────────────

[5-8] [No changes from previous review]

═══════════════════════════════════════════════════════════════

Actions:
  [a] Approve all changes
  [r] Reject with feedback
  [q] Quit without saving

Your choice:
```

---

### Human Review - Second Iteration (Approval)

**Human Action:**
```
> a
```

**System Response:**
```
✓ Change request approved
⏳ Persisting changes...

═══════════════════════════════════════════════════════════════
                    PERSISTENCE SUMMARY
═══════════════════════════════════════════════════════════════

Request ID: cr_20241216_143127_c9e2
Status: APPROVED
Timestamp: 2024-12-16 14:31:45

Changes to be persisted:
  • 4 new entities to create
  • 4 existing entities to update
  • 1 document processed
  • Total confidence score: 94.2%

[POC MODE] Changes logged but not persisted to database.

Log file: /var/log/agni/persistence_20241216_143145.json

✓ Processing complete!

═══════════════════════════════════════════════════════════════
```

---

## Key Observations

### Strengths Demonstrated

1. **Bilingual Extraction**: Successfully extracted both Nepali and English names
2. **Complex Relationships**: Identified the relationship between deceased accountant and his wife
3. **Entity Matching**: Correctly matched 4 existing entities in NES database
4. **Confidence Scoring**: Flagged low-confidence extractions for human review
5. **Feedback Integration**: Successfully incorporated human corrections in second iteration

### Areas Requiring Human Oversight

1. **Name Romanization**: English transliterations of Nepali names need verification (e.g., "Kushiyait" vs other possible spellings)
2. **Title Prefixes**: AI included "Kumari" as part of the name when it's an honorific
3. **Location Details**: Initial extraction missed specific location "Duhabi"
4. **Role Verification**: Current roles need verification against latest information

### Workflow Efficiency

- **Initial extraction**: ~15 seconds (AI processing)
- **Entity matching**: ~3 seconds (database queries)
- **Human review (first)**: ~2 minutes (reading + feedback)
- **Reprocessing**: ~12 seconds (AI + matching)
- **Human review (second)**: ~30 seconds (verification + approval)
- **Total time**: ~3 minutes

**Comparison to manual entry**: Estimated 20-30 minutes for manual data entry of 8 entities with bilingual names and relationships.

**Time saved**: ~85-90%

---

## Lessons for Implementation

1. **Feedback prefixes work well**: Clear routing of corrections to appropriate stages
2. **Confidence thresholds are useful**: 0.7 threshold effectively flags items needing review
3. **Iterative refinement is fast**: Second iteration took only 12 seconds
4. **Bilingual support is critical**: Nepali names have higher confidence than romanized versions
5. **Entity relationships matter**: System correctly identified family relationships and organizational affiliations

---

## Next Steps for Production

1. **Add batch processing**: Process multiple documents in one session
2. **Improve romanization**: Use standardized transliteration rules for Nepali names
3. **Add entity disambiguation**: When multiple matches exist, provide more context for selection
4. **Implement actual persistence**: Connect to NES database for real data updates
5. **Add audit trail**: Track all changes with timestamps and reviewer information
