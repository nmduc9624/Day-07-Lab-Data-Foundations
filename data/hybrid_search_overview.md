# Hybrid Search Overview

Hybrid search combines dense vector retrieval with sparse keyword retrieval. Dense retrieval is good at semantic matching, while sparse retrieval is good at exact terms, product names, error codes, function names, and rare identifiers. Combining both methods often improves robustness.

A pure vector search may miss a document when the query contains an exact identifier such as `ERR_BILLING_042`, `KubernetesCrashLoopBackOff`, or a product SKU. A keyword search can catch these exact matches. On the other hand, keyword search may fail when the user asks a semantic question using different wording from the document. Dense embeddings help in that case.

Hybrid search usually works by retrieving candidates from both systems, normalizing scores, merging candidates, and optionally reranking the final set. Metadata filters can be applied before or after candidate generation depending on the architecture.

For RAG applications, hybrid search is especially helpful in enterprise knowledge bases where users ask about both concepts and exact operational details. It reduces the risk that the system only works for natural language questions but fails on codes, names, and commands.

