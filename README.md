# Dodge-ai-task
## Introduction
This project involves building a graph-based data modeling and query system on top of a fragmented enterprise dataset representing the Order-to-Cash (O2C) process. The goal is to unify disconnected data across multiple business entities and enable intuitive exploration through a visual graph interface.
In addition, the system incorporates a conversational interface powered by a Large Language Model (LLM), allowing users to query the data using natural language. These queries are dynamically translated into structured operations, ensuring that all responses are accurate and grounded in the dataset.
## PHASE 0: Initial Dataset Overview
The dataset simulates an enterprise Order-to-Cash (O2C) process in which business transactions are fragmented across multiple functional systems, including sales, logistics, billing, and finance. Each stage produces independent documents that are only implicitly connected through reference fields rather than explicit relationships. As a result, reconstructing the lifecycle of a transaction requires identifying and linking these documents across tables. I approach this problem by modeling the data as a graph, where entities such as orders, deliveries, invoices, and payments are represented as nodes, and their relationships as edges. This enables intuitive traversal of business flows, supports natural language querying, and provides a unified view of otherwise fragmented enterprise data.
## PHASE 1: Data Preparation
The dataset was successfully ingested, cleaned, and standardized to ensure consistency across all transactional entities. Key relationships between sales orders, deliveries, billing documents, journal entries, and payments were identified and validated using reference fields, confirming the reconstruction of the Order-to-Cash flow. The analysis also revealed that the data does not follow a strict one-to-one progression, with variations in record counts indicating partial deliveries, multiple billing items per transaction, and incomplete payments. This highlights the inherently fragmented and non-linear nature of enterprise data, reinforcing the need for a graph-based model to effectively represent and traverse these relationships.


<img width="479" height="390" alt="Screenshot 2026-03-24 at 11 44 06 AM" src="https://github.com/user-attachments/assets/b767781a-f72b-449a-a95f-8a5d16fbc4de" />

## PHASE 2: Graph Construction
The graph successfully models the end-to-end Order-to-Cash flow by connecting transactional entities across multiple stages. The constructed graph captures real-world complexities such as one-to-many relationships, where a single delivery can result in multiple billing documents and corresponding financial entries. This demonstrates the effectiveness of graph-based modeling in representing non-linear business processes and enabling traceability across fragmented enterprise data.


<img width="569" height="252" alt="Screenshot 2026-03-24 at 11 56 24 AM" src="https://github.com/user-attachments/assets/7084cabb-437d-4615-bec4-096e5e72659f" />

## PHASE 3: Query Layer
The query layer enables structured exploration of the graph through traversal and aggregation functions. By leveraging the relationships encoded in the graph, the system can reconstruct complete transaction flows, compute business metrics such as top billed products, and identify anomalies such as incomplete order lifecycles. This demonstrates the effectiveness of graph-based querying in handling non-linear, multi-stage enterprise data while supporting both analytical and diagnostic use cases.


<img width="1052" height="721" alt="Screenshot 2026-03-24 at 12 07 08 PM" src="https://github.com/user-attachments/assets/321a7f92-386e-424d-9f6a-b19bc22daa26" />


