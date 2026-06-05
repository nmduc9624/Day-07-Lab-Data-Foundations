# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Minh Đức  
**Nhóm:** 2 đứa trái ngoài cùng  
**Ngày:** 05/06/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**  
High cosine similarity nghĩa là hai vector embedding có hướng gần nhau, tức là hai đoạn văn bản có nội dung, chủ đề hoặc ý nghĩa gần nhau trong không gian embedding. Điểm càng gần 1 thì hai đoạn văn bản càng được xem là tương đồng.

**Ví dụ HIGH similarity:**
- Sentence A: Python is a programming language used for automation and data analysis.
- Sentence B: Python can be used to write scripts and analyze data.
- Tại sao tương đồng: Cả hai câu đều nói về Python và các ứng dụng trong lập trình, tự động hóa và phân tích dữ liệu.

**Ví dụ LOW similarity:**
- Sentence A: Vector databases store embeddings for similarity search.
- Sentence B: A recipe needs flour, eggs, and sugar.
- Tại sao khác: Hai câu thuộc hai domain khác nhau; một câu nói về vector database, câu còn lại nói về nấu ăn.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**  
Cosine similarity tập trung vào hướng của vector, phù hợp với việc đo độ gần nghĩa giữa các embedding. Euclidean distance dễ bị ảnh hưởng bởi độ lớn vector, trong khi với text embedding, hướng vector thường quan trọng hơn độ dài.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**  
Công thức:

```text
num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
step = 500 - 50 = 450
num_chunks = ceil((10000 - 50) / 450)
num_chunks = ceil(9950 / 450) = 23
```

**Đáp án:** 23 chunks.

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**  
Khi overlap = 100:

```text
step = 500 - 100 = 400
num_chunks = ceil((10000 - 100) / 400)
num_chunks = ceil(9900 / 400) = 25
```

Số chunk tăng từ 23 lên 25. Overlap lớn hơn giúp giữ thêm ngữ cảnh giữa các chunk liền kề, giảm rủi ro mất thông tin quan trọng nằm ở ranh giới chunk.

---

## 2. Document Selection - Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** AI knowledge assistant / RAG, vector store, chunking, Python và customer support knowledge base.

**Tại sao nhóm chọn domain này?**  
Domain này phù hợp trực tiếp với mục tiêu lab: xây dựng retrieval pipeline dựa trên embedding và vector store. Bộ tài liệu có cả nội dung kỹ thuật, thiết kế hệ thống, ghi chú tiếng Việt và tài liệu customer support, giúp kiểm tra chunking, metadata filter và grounding trong nhiều kiểu câu hỏi.

Nhóm sử dụng bộ tài liệu mẫu có sẵn trong thư mục `data/` của lab vì các tài liệu này đã đúng định dạng `.txt/.md`, có cùng domain với mục tiêu bài học là RAG, embedding, vector store và retrieval strategy.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | python_intro.txt | data/python_intro.txt | 1944 | source, category=programming, lang=en |
| 2 | vector_store_notes.md | data/vector_store_notes.md | 2123 | source, category=retrieval, lang=en |
| 3 | rag_system_design.md | data/rag_system_design.md | 2391 | source, category=retrieval, lang=en |
| 4 | customer_support_playbook.txt | data/customer_support_playbook.txt | 1692 | source, category=support, lang=en |
| 5 | chunking_experiment_report.md | data/chunking_experiment_report.md | 1987 | source, category=retrieval, lang=en |
| 6 | vi_retrieval_notes.md | data/vi_retrieval_notes.md | 1667 | source, category=retrieval, lang=vi |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| source | string | data/rag_system_design.md | Truy vết chunk về tài liệu gốc khi giải thích câu trả lời. |
| category | string | retrieval, programming, support | Lọc tài liệu theo domain trước khi search để giảm nhiễu. |
| lang | string | en, vi | Hỗ trợ lọc theo ngôn ngữ khi query/tài liệu có cả tiếng Anh và tiếng Việt. |
| doc_id | string | rag_system_design | Dùng để xóa toàn bộ chunk của một tài liệu trong `delete_document`. |

---

## 3. Chunking Strategy - Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` với `chunk_size=300` trên 3 tài liệu mẫu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| python_intro.txt | FixedSizeChunker (`fixed_size`) | 8 | 269.2 | Trung bình, có overlap nhưng có thể cắt ngang câu. |
| python_intro.txt | SentenceChunker (`by_sentences`) | 5 | 386.2 | Tốt, giữ nguyên ranh giới câu. |
| python_intro.txt | RecursiveChunker (`recursive`) | 11 | 174.8 | Tốt, ưu tiên paragraph/newline/câu/từ. |
| vector_store_notes.md | FixedSizeChunker (`fixed_size`) | 8 | 291.6 | Trung bình, chunk đều nhưng ít hiểu cấu trúc Markdown. |
| vector_store_notes.md | SentenceChunker (`by_sentences`) | 8 | 262.5 | Khá tốt với các đoạn giải thích bằng câu. |
| vector_store_notes.md | RecursiveChunker (`recursive`) | 12 | 175.0 | Tốt hơn với Markdown vì ưu tiên tách theo paragraph và newline. |
| rag_system_design.md | FixedSizeChunker (`fixed_size`) | 9 | 292.3 | Trung bình, có thể cắt ngang section. |
| rag_system_design.md | SentenceChunker (`by_sentences`) | 5 | 474.8 | Giữ câu tốt nhưng chunk hơi dài. |
| rag_system_design.md | RecursiveChunker (`recursive`) | 15 | 157.5 | Phù hợp nhất cho tài liệu có section/heading. |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**  
Strategy này thử tách text theo danh sách separator ưu tiên: paragraph (`\n\n`), newline (`\n`), ranh giới câu (`. `), space, và cuối cùng là cắt theo ký tự nếu không còn cách nào khác. Nếu một phần sau khi tách vẫn dài hơn `chunk_size`, hàm tiếp tục đệ quy với separator tiếp theo. Cách này giữ được cấu trúc tự nhiên của tài liệu Markdown/txt tốt hơn so với cắt cứng theo số ký tự.

**Tại sao tôi chọn strategy này cho domain nhóm?**  
Bộ tài liệu có nhiều Markdown heading, paragraph và các đoạn giải thích ngắn. RecursiveChunker tận dụng được cấu trúc này, tạo chunk ngắn hơn, dễ đọc hơn và ít cắt ngang ý hơn FixedSizeChunker. Với RAG, chunk có ý nghĩa trọn vẹn giúp agent dễ grounding hơn khi inject context vào prompt.

**Code snippet (nếu custom):**

```python
# Không dùng custom chunker trong lần nộp này.
# Strategy cá nhân: RecursiveChunker(chunk_size=300)
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| rag_system_design.md | best baseline: SentenceChunker | 5 | 474.8 | Chunk dài, giữ câu tốt nhưng có thể gom nhiều ý vào một chunk. |
| rag_system_design.md | **của tôi: RecursiveChunker** | 15 | 157.5 | Chunk ngắn, bám section tốt hơn, dễ hiển thị top-k context hơn. |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi | RecursiveChunker | 8/10 | Giữ cấu trúc paragraph/section, chunk dễ đọc, phù hợp tài liệu Markdown. | Nếu chunk quá ngắn có thể thiếu ngữ cảnh ở một số câu hỏi tổng hợp. |
| Thành viên còn lại | SentenceChunker | 7/10 | Giữ câu đầy đủ, ít cắt ngang ý, dễ đọc khi tài liệu có câu rõ ràng. | Chunk có thể quá dài khi câu/paragraph dài, đôi khi gom nhiều ý vào cùng một chunk. |

Baseline dùng SentenceChunker với `max_sentences_per_chunk=3`. Thành viên còn lại cũng dùng SentenceChunker nhưng tinh chỉnh `max_sentences_per_chunk=2`, nên số lượng chunk, độ dài trung bình và kết quả retrieval có thể khác baseline.

**Strategy nào tốt nhất cho domain này? Tại sao?**  
RecursiveChunker phù hợp hơn một chút với bộ tài liệu này vì phần lớn tài liệu có cấu trúc Markdown/paragraph rõ ràng. So với SentenceChunker, RecursiveChunker tạo chunk ngắn hơn và bám section tốt hơn, nên dễ đưa vào top-k context cho RAG. SentenceChunker vẫn tốt khi tài liệu có câu rõ ràng, nhưng đôi khi chunk dài và gom nhiều ý hơn.

---

## 4. My Approach - Cá nhân (10 điểm)

Giải thích cách tiếp cận khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk` - approach:**  
Hàm xử lý text rỗng trước, sau đó dùng regex `(?<=[.!?])\s+|\.\n+` để tách câu dựa trên dấu kết thúc câu và khoảng trắng/newline. Các câu được `strip()` để bỏ khoảng trắng thừa, rồi gom thành từng nhóm tối đa `max_sentences_per_chunk` câu.

**`RecursiveChunker.chunk` / `_split` - approach:**  
`chunk()` là wrapper xử lý text rỗng và gọi `_split`. `_split` có base case là text ngắn hơn `chunk_size` thì trả về ngay; nếu text quá dài thì thử separator hiện tại, gom các piece sao cho không vượt `chunk_size`, và đệ quy với separator tiếp theo cho piece vẫn quá dài. Nếu hết separator thì fallback cắt fixed-size theo ký tự.

### EmbeddingStore

**`add_documents` + `search` - approach:**  
Mỗi `Document` được chuyển thành record gồm `id`, `content`, `metadata`, và `embedding`. Metadata được copy từ document và bổ sung `doc_id`. `search()` embed query bằng embedding function, tính dot product với từng record, sort theo score giảm dần và trả về top-k.

**`search_with_filter` + `delete_document` - approach:**  
`search_with_filter()` lọc metadata trước, sau đó mới tính similarity trên tập record đã lọc, đúng với yêu cầu lab. `delete_document()` xóa tất cả record có `metadata["doc_id"] == doc_id` và trả về `True` nếu kích thước store giảm.

### KnowledgeBaseAgent

**`answer` - approach:**  
Agent gọi `store.search(question, top_k)` để lấy các chunk liên quan, sau đó ghép các chunk vào prompt có section `Context`, `Question`, `Answer`. Cuối cùng agent gọi `llm_fn(prompt)` để sinh câu trả lời. Cách này thể hiện pattern RAG: retrieve -> inject context -> generate.

### Test Results

```text
python -m unittest tests.test_solution -v
Ran 42 tests in 0.018s
OK
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions - Cá nhân (5 điểm)

Ghi chú: Kết quả actual được tính bằng mock embedder của lab, nên điểm không phản ánh semantic similarity thật sự như embedding model thật. Điều này cũng là một điểm cần phân tích khi đánh giá retrieval quality.

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Python is a programming language. | Python is used to write software and scripts. | high | -0.016 | Không |
| 2 | Vector stores retrieve similar embeddings. | A database can search documents by vector similarity. | high | 0.153 | Một phần |
| 3 | Customer support handles billing issues. | Password reset steps help users regain account access. | medium | -0.084 | Không |
| 4 | Chunk overlap preserves context between text windows. | Bananas and apples are common fruits. | low | 0.099 | Một phần |
| 5 | RAG injects retrieved context into the model prompt. | Retrieval augmented generation answers questions using external knowledge. | high | -0.074 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**  
Bất ngờ nhất là pair 1 và pair 5 có nghĩa rất gần nhau nhưng điểm mock embedding lại âm. Nguyên nhân là `_mock_embed` tạo vector deterministic từ hash của text, không phải model semantic thật. Điều này cho thấy khi đánh giá RAG cần phân biệt giữa pipeline code đúng và embedding backend có chất lượng semantic thật hay không.

---

## 6. Results - Cá nhân (10 điểm)

Chạy 5 benchmark queries trên implementation cá nhân, dùng mock embedding mặc định của lab.

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | What is Python used for? | Python is used for programming, scripting, automation, data analysis and building applications. |
| 2 | What does a vector store do? | A vector store keeps embeddings and retrieves similar documents/chunks by vector similarity. |
| 3 | What are the main steps in a RAG pipeline? | Load documents, chunk them, embed chunks, store vectors, retrieve relevant chunks, inject context into prompt, then generate answer. |
| 4 | Why does chunk overlap help retrieval? | Overlap preserves context across neighboring chunks and reduces information loss at chunk boundaries. |
| 5 | What should customer support documents include for useful retrieval? | Support docs should include clear issue descriptions, step-by-step resolutions, escalation rules, and useful metadata. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What is Python used for? | `chunking_experiment_report.md`: nói về chunking experiment | 0.117 | No | Agent đưa context từ chunking report, không phù hợp với Python. |
| 2 | What does a vector store do? | `customer_support_playbook.txt`: nói về support assistant | 0.170 | No | Agent đưa context customer support, thiếu định nghĩa vector store. |
| 3 | What are the main steps in a RAG pipeline? | `rag_system_design.md`: nói về thiết kế RAG assistant | 0.341 | Yes | Agent có context đúng về RAG system design. |
| 4 | Why does chunk overlap help retrieval? | `vi_retrieval_notes.md`: ghi chú retrieval tiếng Việt | 0.090 | Partial | Context liên quan retrieval nhưng không phải tài liệu chunk overlap chính. |
| 5 | What should customer support documents include for useful retrieval? | `rag_system_design.md`: nói về thiết kế RAG | 0.219 | Partial | Context gần domain RAG nhưng top-1 không phải support playbook. |

### Top-3 Retrieved Chunks

| # | Query | Rank | Retrieved Chunk | Score | Relevant? |
|---|-------|------|-----------------|-------|-----------|
| 1 | What is Python used for? | 1 | `chunking_experiment_report.md` | 0.117 | No |
| 1 | What is Python used for? | 2 | `rag_system_design.md` | 0.055 | No |
| 1 | What is Python used for? | 3 | `vector_store_notes.md` | -0.030 | No |
| 2 | What does a vector store do? | 1 | `customer_support_playbook.txt` | 0.170 | No |
| 2 | What does a vector store do? | 2 | `vi_retrieval_notes.md` | 0.126 | Partial |
| 2 | What does a vector store do? | 3 | `rag_system_design.md` | 0.072 | Partial |
| 3 | What are the main steps in a RAG pipeline? | 1 | `rag_system_design.md` | 0.341 | Yes |
| 3 | What are the main steps in a RAG pipeline? | 2 | `vector_store_notes.md` | 0.304 | Partial |
| 3 | What are the main steps in a RAG pipeline? | 3 | `customer_support_playbook.txt` | 0.097 | No |
| 4 | Why does chunk overlap help retrieval? | 1 | `vi_retrieval_notes.md` | 0.090 | Partial |
| 4 | Why does chunk overlap help retrieval? | 2 | `customer_support_playbook.txt` | 0.062 | No |
| 4 | Why does chunk overlap help retrieval? | 3 | `vector_store_notes.md` | -0.044 | Partial |
| 5 | What should customer support documents include for useful retrieval? | 1 | `rag_system_design.md` | 0.219 | Partial |
| 5 | What should customer support documents include for useful retrieval? | 2 | `python_intro.txt` | 0.075 | No |
| 5 | What should customer support documents include for useful retrieval? | 3 | `vi_retrieval_notes.md` | 0.068 | Partial |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 1 / 5 chính xác trực tiếp, 2 / 5 partial.

### Metadata Utility: Filtered vs Unfiltered Search

| Query | No Filter Top-1 | Filter Used | Filtered Top-1 | Better? |
|---|---|---|---|---|
| What does a vector store do? | `customer_support_playbook.txt` | `category=retrieval` | `vi_retrieval_notes.md` | Partial |
| What is Python used for? | `chunking_experiment_report.md` | `category=programming` | `python_intro.txt` | Yes |
| What should customer support documents include for useful retrieval? | `rag_system_design.md` | `category=support` | `customer_support_playbook.txt` | Yes |
| Cho biết retrieval trong trợ lý tri thức nội bộ là gì? | `rag_system_design.md` | `lang=vi` | `vi_retrieval_notes.md` | Yes |

Với query "What does a vector store do?", filter `category=retrieval` giúp loại bỏ `customer_support_playbook.txt`, nhưng top-1 sau filter vẫn là `vi_retrieval_notes.md` thay vì `vector_store_notes.md`. Điều này cho thấy metadata filter có thể giảm nhiễu theo domain, nhưng với mock embedding thì score vẫn chưa phản ánh semantic similarity thật sự. Nếu cần ép đúng tài liệu vector store để kiểm thử riêng, có thể dùng filter chặt hơn như `source=data/vector_store_notes.md`, nhưng trong benchmark tổng quát filter quá chặt có thể làm mất recall.

### Grounding Quality

**Query:** What are the main steps in a RAG pipeline?  
**Supporting chunk:** `rag_system_design.md`  
**Agent answer có dựa trên chunk này không?** Yes

Câu trả lời của agent được tạo từ retrieved context có chứa `rag_system_design.md`, đây là tài liệu mô tả trực tiếp thiết kế RAG pipeline. Vì retrieved chunk đúng domain và nằm top-1 với score 0.341, câu trả lời có grounding tốt hơn các query mà top-1 bị lệch sang tài liệu khác.

**Nhận xét:**  
Kết quả retrieval với mock embedding không ổn định về mặt semantic. Pipeline code hoạt động đúng, nhưng vì embedding backend không hiểu nghĩa nên query có thể retrieve tài liệu không đúng chủ đề. Nếu dùng `sentence-transformers` hoặc OpenAI embeddings, dự kiến precision sẽ tốt hơn rõ rệt.

---

## 7. What I Learned (5 điểm - Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**  
Khác strategy chunking có thể làm kết quả retrieval thay đổi rất nhiều ngay cả khi dùng cùng bộ tài liệu. Fixed-size chunking dễ cài đặt nhưng không phải lúc nào cũng tốt; strategy dựa trên cấu trúc tài liệu thường cho chunk dễ đọc và dễ grounding hơn.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**  
Metadata filtering rất hữu ích khi bộ tài liệu có nhiều domain hoặc nhiều ngôn ngữ. Tuy nhiên filter quá chặt có thể làm mất kết quả tốt, nên cần thiết kế metadata vừa đủ và test với benchmark queries thực tế.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**  
Tôi sẽ chia tài liệu thành các chunk nhỏ hơn trước khi add vào `EmbeddingStore`, thay vì store cả document dài như một record. Tôi cũng sẽ dùng embedding model semantic thật (`all-MiniLM-L6-v2` hoặc OpenAI embeddings) để benchmark retrieval chất lượng hơn, và thêm metadata `section`/`topic` để filter chính xác hơn.

### Failure Analysis

Failure case rõ nhất là query "What is Python used for?" nhưng top-1 lại là `chunking_experiment_report.md`. Nguyên nhân chính là mock embedding không học ý nghĩa text mà tạo vector từ hash, nên similarity score không phản ánh semantic similarity. Cách cải thiện là dùng embedding backend thật, chunk tài liệu trước khi store, và thêm metadata filter `category=programming` cho query liên quan Python.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 10 / 10 |
| Chunking strategy | Nhóm | 14 / 15 |
| My approach | Cá nhân | 10 / 10 |
| Similarity predictions | Cá nhân | 5 / 5 |
| Results | Cá nhân | 8 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 5 / 5 |
| **Tổng** | | **92 / 100** |
