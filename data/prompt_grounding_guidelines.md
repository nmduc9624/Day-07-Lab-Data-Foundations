# Prompt Grounding Guidelines

Prompt grounding means instructing the language model to answer using retrieved context rather than unsupported prior knowledge. A RAG prompt should clearly separate context, question, and answer instructions. It should also tell the model what to do when the answer is not present in the context.

A common prompt structure is:

1. System instruction: answer only from the provided context.
2. Retrieved context: numbered chunks with source labels.
3. User question.
4. Output instruction: concise answer with citations or source references.

Grounding quality improves when retrieved chunks are coherent and include source metadata. If the agent can point to `vector_store_notes.md` or `rag_system_design.md`, a human evaluator can verify whether the answer is supported.

Bad grounding often appears as hallucination, overgeneralization, or answers that ignore the retrieved evidence. To detect this, compare the final answer against the retrieved chunks. If the answer includes a claim that cannot be found in the context, the system should be marked as partially grounded or ungrounded.

