# Phase 1

## Merchant Ingestion

Green River is a generic product extraction, embedding, and storage system for merchant/product webpages.

The Phase 1 pipeline takes a merchant product URL, extracts webpage content using Scrapling, converts the content into a moderately structured representation, uses LangGraph + Groq to produce a validated `StructuredProduct`, generates embeddings through Jina, and stores the structured product JSON together with its vector in PostgreSQL/Supabase.

The system is intentionally website-agnostic. There are no retailer-specific parsers such as `amazon.py` or `uniqlo.py`. The same central pipeline is used across merchant webpages.

---

## High-Level Pipeline

```text
                            MERCHANT URL
                                 │
                                 ▼
                         ┌─────────────┐
                         │  Scrapling  │
                         └──────┬──────┘
                                │
                                ▼
                       Raw webpage text
                                │
                  ┌─────────────┴─────────────┐
                  │                           │
                  ▼                           ▼
              raw.txt                   Generic Parser
                                              │
                                              ▼
                                      Pydantic WebPage
                                              │
                                              ▼
                                      structured.txt
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
                         ┌────────────────────┴────────────────────┐
                         │                                         │
                         ▼                                         ▼
                 Product JSON                               Embedding text
                         │                                         │
                         │                                         ▼
                         │                                  Jina Embeddings
                         │                                         │
                         │                                         ▼
                         │                                  1024-d vector
                         │                                         │
                         └──────────────────┬──────────────────────┘
                                            ▼
                                   PostgreSQL / Supabase
                                            │
                                            ▼
                                    merchant_products
```

---

# API

FastAPI is the application entry point.

### Current Routes

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Service health check |
| `POST` | `/extract` | URL → raw + moderately structured webpage text |
| `POST` | `/extract-product` | URL → Groq `StructuredProduct` |
| `POST` | `/embed-product` | URL → product extraction + Jina embedding + Supabase storage |
| `POST` | `/merchant/ingest` | Main merchant ingestion endpoint: URL → structured product + embedding + Supabase |

### Merchant Ingestion Endpoint

```text
POST /merchant/ingest
```

Input is a webpage URL. The endpoint does not accept manually entered raw merchant text.

```json
{
  "url": "https://merchant.example/product/..."
}
```

The endpoint runs the complete ingestion workflow:

```text
URL
 ↓
Scrapling
 ↓
Generic preprocessing
 ↓
LangGraph + Groq
 ↓
StructuredProduct
 ↓
Jina embedding
 ↓
Supabase
```

The response includes the Supabase database `id`, the structured product, and embedding metadata.

Example response shape:

```json
{
  "id": 2,
  "url": "https://merchant.example/product/...",
  "product": {
    "source_site": "Example Merchant",
    "product_name": "Example Product",
    "brand": "Example Brand",
    "category": "Shirts",
    "product_id": null,
    "price": "₹269.00",
    "currency": "₹",
    "color": "Blue",
    "sizes": ["M"],
    "availability": "In stock",
    "description": "...",
    "features": [],
    "material": "Cotton",
    "care_instructions": null,
    "rating": null,
    "review_count": null,
    "shipping": null,
    "returns": null,
    "country_of_origin": null,
    "manufacturer": null,
    "url": "https://merchant.example/product/..."
  },
  "model": "jina-embeddings-v5-text-small",
  "dimensions": 1024
}
```

The `id` is the stored row identifier in `merchant_products`.

---

# Project Structure

```text
green-river/
│
├── data/
│   ├── raw/
│   ├── structured/
│   └── embeddings/
│
├── src/
│   └── green_river/
│       │
│       ├── app/
│       │   ├── __init__.py
│       │   └── api.py
│       │
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── extractor.py
│       │   ├── graph.py
│       │   └── prompts.py
│       │
│       ├── embeddings/
│       │   ├── __init__.py
│       │   ├── jina.py
│       │   ├── graph.py
│       │   ├── service.py
│       │   └── storage.py
│       │
│       ├── __init__.py
│       ├── cli.py
│       ├── db.py
│       ├── models.py
│       ├── parser.py
│       ├── scraper.py
│       ├── service.py
│       └── utils.py
│
├── tests/
│   ├── test1.py
│   └── test2.py
│
├── .env
├── .gitignore
├── pyproject.toml
└── uv.lock
```

---

# Ingestion Architecture

## Webpage Extraction

The deterministic webpage layer is responsible for fetching and preparing content before the LLM sees it.

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
 Pydantic WebPage
       │
       ├──────────────► structured.txt
       │
       ▼
Structured webpage text
```

This layer establishes:

**URL → scrape → parse → validate → structured output**

---

# Groq-Based Product Extraction

The LLM layer transforms moderately structured webpage content into a normalized `StructuredProduct`.

```text
Merchant URL
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
```

The Groq extraction is schema-constrained rather than freeform. The current implementation uses structured output with strict validation.

Important extraction rules include:

- Missing scalar values are returned as `null`.
- Missing list values are returned as `[]`.
- The model must not guess missing values.
- Product lines, collections, technologies, manufacturers, retailers, or page/site names are not automatically treated as the product brand.
- Navigation, footer, cookie, login, and other UI noise should not be treated as product data.

The extraction tests cover missing values and incorrect brand inference.

---

# Embedding Pipeline

The extracted product is converted into a compact semantic embedding string and sent to Jina.

```text
URL
 │
 ▼
Scrapling
 │
 ▼
Pydantic WebPage
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
      PostgreSQL / Supabase
```

Current embedding model:

```text
jina-embeddings-v5-text-small
```

Current stored vector size:

```text
1024 dimensions
```

---

# Complete Merchant Ingestion Architecture

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
                     POST /merchant/ingest
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
          │      API       │       │     jsonb      │
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
                    │ merchant_products│
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

# Database

Product records are stored in the Supabase PostgreSQL `merchant_products` table.

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

| Column | Purpose |
| --- | --- |
| `id` | Database record identifier returned by ingestion |
| `product_id` | Product identifier when one is available |
| `source_url` | Original merchant/product URL |
| `product_json` | Full `StructuredProduct` JSON stored as `jsonb` |
| `embedding` | Jina-generated 1024-dimensional vector |
| `created_at` | Record creation timestamp |

---

# Database Operations

The database layer is implemented in `db.py`.

### `insert_product()`

Stores one product's structured JSON and embedding and returns the Supabase row `id`.

### `get_product()`

Retrieves one stored product by database row ID.

### `similarity_search()`

Performs vector similarity search against the stored `embedding` column and returns the nearest products, with a default limit of 8.

The database-side similarity search is already implemented. The next application-level step is to expose query-time search through the API.

---

# End-to-End Data Flow

```text
Merchant URL
    ↓
Scrapling
    ↓
Raw webpage text
    ↓
Pydantic WebPage
    ↓
Moderately structured text
    ↓
LangGraph + Groq
    ↓
StructuredProduct
    ↓
Product JSON
    ↓
Embedding text
    ↓
Jina Embedding API
    ↓
1024-dimensional Vector
    ↓
PostgreSQL / Supabase
    ↓
merchant_products
```

---

## Responsibilities

| Component | Responsibility |
| --- | --- |
| **FastAPI** | Exposes the HTTP API, including merchant ingestion |
| **Service** | Orchestrates scraping, extraction, embedding, and persistence |
| **Scrapling** | Fetches and cleans merchant webpages |
| **Parser** | Converts raw webpage content into an intermediate structure |
| **Pydantic** | Validates application and product structures |
| **LangGraph** | Orchestrates the LLM extraction workflow |
| **Groq** | Extracts normalized product information |
| **StructuredProduct** | Represents the normalized product |
| **Jina** | Generates semantic embeddings |
| **PostgreSQL / Supabase** | Persists structured product JSON and vectors |
| **db.py** | Provides insert, retrieval, and similarity-search database operations |

---

# Verification Status

The current ingestion path has been verified through FastAPI using a real merchant webpage URL.

Verified components:

```text
FastAPI                     ✅
Scrapling                   ✅
Generic preprocessing      ✅
Pydantic WebPage           ✅
LangGraph + Groq           ✅
StructuredProduct          ✅
Jina embeddings            ✅
PostgreSQL connection      ✅
Supabase merchant_products ✅
insert_product()           ✅
get_product()              ✅
similarity_search()         ✅
POST /merchant/ingest      ✅
```

A successful `/merchant/ingest` request stores the structured Groq output and the Jina embedding in the same `merchant_products` row and returns the stored database ID to the API client.

---

# Phase 1 Goal

The objective of Phase 1 is to establish a reliable end-to-end merchant webpage ingestion pipeline:

```text
Webpage URL
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

Phase 1 now provides the foundation for later phases involving query-time vector retrieval, semantic search, ranking, recommendations, and RAG.


vision imaging embeddings added 

final architecture till phase 1

```text

                    /merchant/ingest
                           │
                    URL + uploaded image
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
         Scrapling                  Image bytes
             │                           │
             ▼                           ▼
      webpage content              Jina Omni
             │                     image embedding
             ▼                           │
           Groq                          │
             │                           │
             ▼                           │
     StructuredProduct                   │
             │                           │
             ▼                           │
          Jina Omni                      │
       text embedding                    │
             │                           │
             └─────────────┬─────────────┘
                           ▼
                       Supabase
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        product_json   text vector   image vector

```
