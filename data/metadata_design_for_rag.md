# Metadata Design for RAG

Metadata helps a retrieval system narrow the search space before computing semantic similarity. Good metadata makes retrieval more precise, especially when the knowledge base contains multiple domains, languages, departments, document types, or time periods.

Useful metadata fields include `source`, `doc_id`, `category`, `lang`, `owner`, `department`, `created_at`, `updated_at`, `section`, and `access_level`. The best fields depend on the domain. For example, a support knowledge base often benefits from `product`, `issue_type`, `severity`, and `region`. A technical documentation system may need `service`, `version`, `environment`, and `runbook_type`.

Metadata filtering should usually happen before vector search. Filtering after search can hide relevant results because the top-k list may already be filled with documents from the wrong category. However, filters can also be too strict. If a query uses `category=retrieval` and `lang=en`, the system may miss a useful Vietnamese document or a related RAG design note.

Good metadata design balances precision and recall. The goal is not to filter as much as possible, but to remove obvious noise while keeping enough candidates for semantic search.

