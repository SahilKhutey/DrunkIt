# DrunkIt — Product Architecture & Technology Stack Specification v1.0

## Executive Summary

DrunkIt is engineered from the ground up as an **Alcohol Commerce & Intelligence Platform** connecting consumers, independent/craft and multinational alcohol brands, licensed retailers, distributors, and state regulatory systems.

**Architectural Philosophy:**
> **Discovery First, Availability Second, Regulation as a Core Primitive, Commerce Where Permitted, Intelligence Continuously.**  
> Built as a **Modular Monolith $\longrightarrow$ Event-Driven Platform $\longrightarrow$ Distributed Domain Services**.

---

## 1. High-Level North Star Architecture

```text
                                 DRUNKIT PLATFORM
                                        │
                 ┌──────────────────────┼──────────────────────┐
                 ▼                      ▼                      ▼
        CONSUMER EXPERIENCE       B2B ECOSYSTEM        PLATFORM SERVICES
                 │                      │                      │
          ┌──────┼──────┐        ┌──────┼──────┐        ┌──────┼──────┐
          │      │      │        │      │      │        │      │      │
        Search Discover Buy    Brands Retailers Dist. Compliance Intelligence
          │      │      │        │      │      │        │      │      │
          └──────┼──────┘        └──────┼──────┘        └──────┼──────┘
                 │                      │                      │
                 └──────────────────────┼──────────────────────┘
                                        ▼
                              DRUNKIT CORE PLATFORM
                                        │
               ┌────────────────────────┼────────────────────────┐
               ▼                        ▼                        ▼
         PRODUCT GRAPH            COMMERCE ENGINE          DATA PLATFORM
               │                        │                        │
               ▼                        ▼                        ▼
          Availability             Orders/Payments          Analytics
          Inventory                Fulfilment               ML/AI
          Retailer Graph           Settlement               Intelligence
          Brand Graph              Refunds                  Recommendations
               │                        │                        │
               └────────────────────────┼────────────────────────┘
                                        ▼
                                REGULATORY ENGINE
                                        │
                             State/Country Rule Sets
                                        │
                                        ▼
                               COMPLIANCE DECISION
```

---

## 2. Five Dedicated Product Surfaces

The platform unifies 5 role-specific surface applications:

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│ 1. DRUNKIT CONSUMER (Next.js Web + Expo React Native Mobile)                    │
│    • Home, Search, Discover, Mood/Occasion Collections, Taste Profile           │
│    • Brand Storytelling, Master Distiller Notes, ABV/Cask Attributes            │
│    • Real-Time Nearby Store Availability, MRP Lock, Verified Reviews            │
│    • Cart, Age Verification, Checkout, Real-Time Delivery Tracking (where legal)│
├─────────────────────────────────────────────────────────────────────────────────┤
│ 2. DRUNKIT RETAIL (Licensed Merchant Console)                                   │
│    • Merchant Dashboard, POS Integration / CSV / Real-Time Inventory Sync        │
│    • Pricing Management, Storefront Operating Hours, Daily Dry Day Lockouts     │
│    • Order Acceptance, Click-and-Collect Staging, Excise Reconciliation         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 3. DRUNKIT BRANDS (Producer & Importer Portal)                                  │
│    • Brand & Distillery Profiles, Product Catalogue Management, SKUs & Labels   │
│    • Geo-Availability Heatmaps, New SKU Launch Campaigns, Merchandising Studio  │
│    • Consumer Engagement Analytics, Market Whitespace Detection                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 4. DRUNKIT INTELLIGENCE (B2B Market & Demand Platform)                          │
│    • Real-Time SKU Velocity, Flavor Affinity Shifts, Price Elasticity Curves    │
│    • Regional Inventory Stockout Alerts, Brand Benchmarking, B2B Subscriptions  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 5. DRUNKIT ADMIN & COMPLIANCE CONSOLE (Platform Authority)                      │
│    • User, Brand, Retailer KYC & License Verification                           │
│    • State Jurisdiction Rule Builder & Policy Versioning (e.g. WB-2026-08)      │
│    • Immutable Audit Trails, Dispute Management, Risk & Dry Day Calendar Engine │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack Reference Matrix

| Layer | Primary Technology | Secondary / Scaling Evolution | Strategic Rationale |
| :--- | :--- | :--- | :--- |
| **Consumer Web** | **Next.js 14+ (App Router)** | Edge CDN (Cloudflare / Vercel) | Server-side rendering (SSR) for SEO, rich metadata for brand & product pages. |
| **Web Styling & UI** | **Tailwind CSS + shadcn/ui** | Radix UI primitives | Fast iteration, high-density professional theme tokens, WCAG 2.2 AA accessibility. |
| **Web State Management**| **Zustand + TanStack Query** | Persist middleware | Clean separation of client UI state (Zustand) from asynchronous server cache (React Query). |
| **Mobile Application** | **React Native + Expo** | EAS Build Pipelines | Single shared TypeScript codebase for Consumer & Merchant mobile apps. |
| **Backend API** | **Python 3.12 + FastAPI** | Pydantic v2 + AsyncIO | Native integration with ML/AI pipelines, high-throughput async endpoints, auto OpenAPI generation. |
| **Authoritative DB** | **PostgreSQL 16+** | Read Replicas + Citus | ACID compliance for highly relational catalog $\to$ inventory $\to$ compliance $\to$ order graphs. |
| **In-Memory Cache** | **Redis 7.2+** | Redis Sentinel / Cluster | Session management, OTP state, rate limiting, availability cache, job coordination. |
| **Text & Attribute Search**| **PostgreSQL FTS** | **OpenSearch / Elasticsearch** | Full-text product, brand, and region search transitioning to distributed search clusters at scale. |
| **Vector & Taste AI** | **pgvector (PostgreSQL ext)** | Qdrant / Pinecone (Future) | Semantic natural-language discovery (*"Smooth single malt under ₹4,000 without heavy smoke"*). |
| **AI / ML Frameworks** | **PyTorch, Hugging Face, Sentence Transformers, scikit-learn** | MLflow | Product taste embeddings, collaborative filtering, demand forecasting, anomaly detection. |
| **Job Queue & Workers** | **FastAPI Background / Dramatiq / Celery** | **Kafka / Redpanda** | Asynchronous notifications, catalog indexing, image processing, audit hash-chaining. |
| **Object Storage** | **S3-Compatible (MinIO / AWS S3)** | CloudFront CDN | Product imagery, brand hero assets, verified license document storage with encryption. |
| **Observability** | **OpenTelemetry, Prometheus, Grafana, Loki** | Distributed Tracing | Real-time APM, rule evaluation latency, audit verification metrics. |

---

## 4. Product Graph & Semantic Discovery Engine

### 4.1 Knowledge Graph Hierarchy
```text
                     CANONICAL PRODUCER
                            │
                            ▼
                      CANONICAL BRAND
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          REGION          TASTE        DISTILLERY
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                    CANONICAL PRODUCT
                            │
             ┌──────────────┴──────────────┐
             ▼                             ▼
       PRODUCT VARIANT                    SKU
      (750ml / Cask / ABV)           (EAN-13 / GTIN)
             │                             │
             ▼                             ▼
      LICENSED RETAILER              STATE MARKET
             │                             │
             ▼                             ▼
      INVENTORY LEDGER               STATUTORY MRP
```

### 4.2 Semantic Vector Search with pgvector
```python
# Semantic Taste Query Flow:
# 1. User Prompt: "Peated, fruity finish, aged over 12 years under ₹5000"
# 2. Embedding Model: all-MiniLM-L6-v2 produces a 384-dimensional vector.
# 3. Hybrid SQL Query: Combine Cosine Similarity with Relational Availability & Compliance filters.

SELECT 
    p.id, 
    p.name, 
    b.name AS brand_name, 
    inv.price_mrp, 
    inv.stock_quantity,
    1 - (p.taste_embedding <=> :query_embedding) AS similarity_score
FROM products p
JOIN brands b ON p.brand_id = b.id
JOIN inventory inv ON inv.product_id = p.id
JOIN retailers r ON inv.retailer_id = r.id
WHERE inv.stock_quantity > 0
  AND r.state_code = :user_state_code
  AND inv.price_mrp <= :max_budget
ORDER BY similarity_score DESC
LIMIT 20;
```

---

## 5. Retailer Integration & Inventory Normalization Pipeline

Different retailers utilize divergent POS systems, naming conventions, and inventory descriptions:

```text
  RETAILER POS / CSV / MANUAL FEED
  • "JW Black 750ml"
  • "Johnnie Walker BLK 75cl"
  • "JOHNNIE WALKER BLACK LABEL 750"
                  │
                  ▼
      INVENTORY NORMALIZER ENGINE
  • Levenshtein & Fuzzy Name Matching
  • Volume & ABV Disambiguation
  • State Excise Brand Code Mapping
                  │
                  ▼
         CANONICAL DRUNKIT SKU
  • Brand: Johnnie Walker
  • Line: Black Label 12 Year Old
  • Volume: 750 ml | ABV: 40.0%
  • Unified DrunkIt SKU ID: `SKU_JWB_750`
```

---

## 6. Regulatory Engine-as-Code Architecture

```text
                  ORDER / CHECKOUT REQUEST
                             │
                             ▼
                 REGULATORY POLICY ENGINE
                             │
       ┌─────────────────────┼─────────────────────┐
       ▼                     ▼                     ▼
CONSUMER ELIGIBILITY    PRODUCT ELIGIBILITY   RETAILER PERMIT
• Verified Age ≥ Min   • Permitted ABV       • Valid Excise License
• Daily Quota Limit    • Active State Brand  • Operating Retail Hours
• Dry Day Calendar     • Size Permitted      • Geo Delivery Boundary
       └─────────────────────┼─────────────────────┘
                             ▼
                COMPLIANCE DECISION GATE
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
            ALLOW                          DENY
     (Proceed to Escrow)            (Halt with Reason Code)
```

**Key Principle**: The Compliance Gate evaluates **before** payment tokenization and order creation. In jurisdictions without digital delivery authorization, the engine seamlessly locks the checkout button and pivots to **Assisted Commerce (In-Store Availability & Store Locator)**.

---

## 7. Infrastructure Evolution Path

```text
STAGE 1: MVP PLATFORM
Next.js (Web) + FastAPI + PostgreSQL (FTS + pgvector) + Redis + S3 + Docker Compose

STAGE 2: PRODUCT-MARKET FIT
+ OpenSearch Cluster + Dedicated Background Workers + Analytics Data Warehouse

STAGE 3: NATIONAL SCALE
+ Kafka / Redpanda Event Bus + ClickHouse Analytics + Kubernetes (EKS/GKE) + Multi-Region Routing

STAGE 4: GLOBAL INFRASTRUCTURE
+ Global Market Graph + Dynamic Regulatory Adapter APIs + Cross-Border Brand Syndication
```
