# Reranking Notes

Reranking is a second-stage retrieval technique. The vector store first retrieves a broad set of candidates, such as top-20 chunks. A reranker then reorders those candidates using a more expensive but more precise scoring method. This can improve final top-k quality without making the initial vector search too slow.

Reranking is useful when embedding similarity returns many partially related chunks. For example, a query about "vector store workflow" may retrieve documents about RAG, chunking, support assistants, and embeddings. A reranker can compare the query against each candidate more carefully and move the most directly relevant chunk to rank 1.

Common reranking approaches include cross-encoder models, LLM-based relevance scoring, keyword overlap boosts, freshness boosts, and metadata-aware ranking. In production systems, reranking often combines semantic relevance with business rules such as document freshness, access permissions, and source reliability.

Reranking should be evaluated with the same benchmark queries used for the base retriever. The goal is not only to improve average score, but to move the best supporting evidence into the context window used by the generator.

