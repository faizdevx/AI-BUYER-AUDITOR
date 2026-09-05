# Phase 1

## Merchant Ingestion

Green River is a generic product extraction, embedding, and storage system for merchant/product webpages.

The Phase 1 pipeline takes a merchant URL, extracts webpage content using Scrapling, converts the content into a structured representation, uses LangGraph + Groq for product extraction, generates embeddings through Jina, and stores the resulting product data and vectors in PostgreSQL/Supabase.

### High-Level Pipeline

```text
                         WEBSITE
                            │
                            ▼
                    ┌─────────────┐
                    │  Scrapling  │
                    └──────┬──────┘
                           │
                           ▼
                  Cleaned webpage text
                           │
                  ┌────────┴────────┐
                  ▼                 ▼
               _raw.txt        Generic Parser
                                    │
                                    ▼
                              Pydantic Model
                                    │
                                    ▼
                           _structured.txt
                                    │
                                    ▼
                                  Groq
                                    │
                                    ▼
                           StructuredProduct
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                  Jina Embeddings        Product JSON
                         │                     │
                         ▼                     │
                     Vector                   │
                         │                     │
                         └──────────┬──────────┘
                                    ▼
                              PostgreSQL
                               / Supabase
```

---

## Project Structure

```text
app/
├── api.py
│   └── FastAPI endpoints only
│
├── cli.py
│   └── Terminal interface
│
├── scraper.py
│   └── URL → Scrapling → raw webpage text
│
├── parser.py
│   └── Raw webpage text → structured representation
│
├── models.py
│   └── Pydantic models
│
├── service.py
│   └── Application/service orchestration
│
└── utils.py
    └── Generic helper functions
```

---

# Ingestion Architecture

## Initial FastAPI Architecture

Before introducing Groq, the ingestion flow was intentionally simple:

```text
Browser / Client
       │
       ▼
POST /extract
       │
       ▼
   Scrapling
       │
       ▼
  Raw webpage text
       │
       ├──────────────► raw.txt
       │
       ▼
 Generic Parser
       │
       ▼
   Pydantic
       │
       ├──────────────► structured.txt
       │
       ▼
Structured content
```

The initial architecture established the basic ingestion pipeline:

**URL → scrape → parse → validate → structured output**

---

# Groq-Based Product Extraction

The next iteration introduced LangGraph and Groq to transform moderately structured webpage content into a normalized product representation.

```text
Amazon / Merchant URL
          │
          ▼
      Scrapling
          │
          ▼
  Raw webpage text
          │
          ▼
Intermediate structuring
          │
          ▼
      LangGraph
          │
          ▼
        Groq
          │
          ▼
 StructuredProduct
     (Pydantic)
          │
          ▼
    JSON response
```

This separated deterministic webpage extraction from LLM-based product interpretation.

---

# Embedding Pipeline

The current Phase 1 pipeline extends product extraction with semantic embeddings and persistent storage.

```text
URL
 │
 ▼
Scrapling
 │
 ▼
Raw webpage text
 │
 ▼
Pydantic WebPage structure
 │
 ▼
LangGraph
 │
 ▼
Groq
 │
 ▼
StructuredProduct
 │
 ├──────────────────────┐
 │                      │
 ▼                      ▼
Product JSON       Embedding text
 │                      │
 │                      ▼
 │                 Jina API
 │                      │
 │                      ▼
 │                  1024-d vector
 │                      │
 └──────────┬───────────┘
            ▼
      PostgreSQL
       / Supabase
```

---

# Complete Phase 1 Architecture

```text
                         GREEN RIVER
                Generic Product Extraction
                 + Embedding + Storage System


                         ┌──────────────┐
                         │   FastAPI    │
                         │   REST API   │
                         └──────┬───────┘
                                │
                                ▼
                    POST /embed-product
                                │
                                ▼
                         ┌──────────────┐
                         │   Service    │
                         │  service.py  │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   Scraper    │
                         │  Scrapling   │
                         └──────┬───────┘
                                │
                                ▼
                       Raw webpage text
                                │
                                ▼
                         ┌──────────────┐
                         │    Parser    │
                         │  parser.py   │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   Pydantic   │
                         │   WebPage    │
                         └──────┬───────┘
                                │
                                ▼
                    Moderately structured text
                                │
                                ▼
                         ┌──────────────┐
                         │  LangGraph   │
                         │              │
                         │     Groq     │
                         └──────┬───────┘
                                │
                                ▼
                      StructuredProduct
                                │
                                ▼
                    product.model_dump()
                                │
                   ┌────────────┴────────────┐
                   │                         │
                   ▼                         ▼
          ┌────────────────┐       ┌────────────────┐
          │ Jina Embedding │       │  Product JSON  │
          │      API       │       │                │
          └───────┬────────┘       └───────┬────────┘
                  │                        │
                  ▼                        │
             1024-d vector                │
                  │                        │
                  └───────────┬────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   PostgreSQL     │
                    │    Supabase      │
                    │                  │
                    │ merchant_products │
                    ├──────────────────┤
                    │ id               │
                    │ product_id       │
                    │ source_url       │
                    │ product_json     │
                    │ embedding        │
                    │ created_at       │
                    └────────┬─────────┘
                             │
                             ▼
                          Stored
```

---

## Data Flow

The complete Phase 1 data flow can be summarized as:

```text
Merchant URL
    ↓
Scrapling
    ↓
Cleaned Webpage Text
    ↓
Pydantic WebPage
    ↓
LangGraph + Groq
    ↓
StructuredProduct
    ↓
Product JSON
    ↓
Embedding Text
    ↓
Jina Embedding API
    ↓
1024-dimensional Vector
    ↓
PostgreSQL / Supabase
```

### Responsibilities

| Component                 | Responsibility                                              |
| ------------------------- | ----------------------------------------------------------- |
| **FastAPI**               | Exposes ingestion and embedding endpoints                   |
| **Service**               | Orchestrates the complete ingestion workflow                |
| **Scrapling**             | Fetches and cleans merchant webpages                        |
| **Parser**                | Converts raw webpage content into an intermediate structure |
| **Pydantic**              | Validates application data structures                       |
| **LangGraph**             | Orchestrates the LLM extraction workflow                    |
| **Groq**                  | Extracts normalized product information                     |
| **StructuredProduct**     | Represents the final normalized product                     |
| **Jina**                  | Generates semantic embeddings                               |
| **PostgreSQL / Supabase** | Persists product metadata, JSON, and embeddings             |

---

## Database Schema

The resulting product records are stored in the `merchant_products` table.

```text
merchant_products
├── id
├── product_id
├── source_url
├── product_json
├── embedding
└── created_at
```

### Stored Data

* **`id`** — Database record identifier
* **`product_id`** — Product identifier
* **`source_url`** — Original merchant/product URL
* **`product_json`** — Structured product representation
* **`embedding`** — Jina-generated 1024-dimensional vector
* **`created_at`** — Record creation timestamp

---

# Phase 1 Goal

The objective of Phase 1 is to establish a reliable end-to-end merchant ingestion pipeline:

```text
Webpage
   ↓
Extraction
   ↓
Normalization
   ↓
LLM-based Product Structuring
   ↓
Embedding
   ↓
Persistent Storage
```

This provides the foundation for later phases involving product retrieval, semantic search, ranking, recommendations, and other downstream systems.
