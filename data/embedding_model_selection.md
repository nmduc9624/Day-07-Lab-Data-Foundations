# Embedding Model Selection

Embedding model quality has a direct impact on retrieval quality. A mock embedder is useful for tests because it is deterministic and does not require network access, but it does not understand meaning. A real embedding model maps semantically similar texts to nearby vectors, so it can retrieve relevant documents even when the query and document use different words.

When selecting an embedding model, teams should consider semantic quality, latency, cost, language support, vector dimension, and operational requirements. A local model such as `all-MiniLM-L6-v2` is convenient for offline experiments and avoids API cost. A hosted embedding model such as `text-embedding-3-small` can provide stronger semantic retrieval and simpler deployment when API access is available.

Model choice should be evaluated with benchmark queries instead of assumptions. A good comparison uses the same documents, same chunking strategy, and same top-k setting. The only changed variable should be the embedding backend. This makes it easier to see whether retrieval improvements come from the model rather than from changes in data preparation.

If retrieval scores improve but answers still fail, the issue may be prompt construction, missing documents, poor chunking, or weak grounding rather than embedding model quality.

