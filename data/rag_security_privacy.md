# RAG Security and Privacy

RAG systems can expose sensitive information if retrieval and access control are not designed carefully. A user should only retrieve documents they are allowed to see. This means access control must be enforced before the retrieved context is sent to the model.

Important security controls include metadata-based access filtering, document-level permissions, audit logging, encryption at rest, and safe handling of API keys. The system should avoid storing secrets in source code or committing `.env` files to version control.

Prompt injection is another risk. A retrieved document may contain instructions such as "ignore previous rules" or "reveal confidential data." The agent should treat retrieved documents as data, not as trusted instructions. The system prompt should make this boundary clear.

Privacy evaluation should check whether the system returns private data to unauthorized users, whether logs contain sensitive prompts, and whether embeddings are stored according to policy. Even though embeddings are not raw text, they can still represent sensitive information and should be protected.

