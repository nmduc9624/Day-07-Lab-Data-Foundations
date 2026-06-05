# RAG Evaluation Metrics

RAG evaluation should measure both retrieval quality and answer quality. A system can fail even when the application code runs without errors. The most common retrieval metrics are precision@k, recall@k, mean reciprocal rank, and hit rate. Precision@k asks how many of the top-k retrieved chunks are actually relevant. Recall@k asks whether the system found the necessary evidence somewhere in the top-k results.

Answer quality should be checked separately. A grounded answer should use the retrieved context and avoid unsupported claims. Useful answer-level checks include factual accuracy, citation traceability, completeness, and refusal behavior when the context is insufficient.

For classroom benchmarks, five well-designed questions are often enough to reveal major problems. A good benchmark set should include a direct factual question, a multi-step question, a metadata-dependent question, a question that requires multiple documents, and one expected failure case.

Evaluation notes:
- Top-1 relevance is useful for quick debugging.
- Top-3 relevance is better for RAG because the model may use several chunks.
- Score gaps matter: a strong top result should usually have a clear score separation from noisy results.
- Manual judgment is still important because embedding scores do not always match human relevance.

