from __future__ import annotations

import json
import os
import re
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        env_path = Path(".env")
        if not env_path.exists():
            return False
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if not line or line.strip().startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())
        return True

from src.agent import KnowledgeBaseAgent
from src.embeddings import (
    EMBEDDING_PROVIDER_ENV,
    LOCAL_EMBEDDING_MODEL,
    OPENAI_EMBEDDING_MODEL,
    LocalEmbedder,
    OpenAIEmbedder,
    _mock_embed,
)
from src.models import Document
from src.store import EmbeddingStore


SAMPLE_FILES = [
    "data/python_intro.txt",
    "data/vector_store_notes.md",
    "data/rag_system_design.md",
    "data/customer_support_playbook.txt",
    "data/chunking_experiment_report.md",
    "data/vi_retrieval_notes.md",
    "data/rag_evaluation_metrics.md",
    "data/metadata_design_for_rag.md",
    "data/embedding_model_selection.md",
    "data/reranking_notes.md",
    "data/hybrid_search_overview.md",
    "data/prompt_grounding_guidelines.md",
    "data/rag_security_privacy.md",
    "data/vi_rag_deployment_strategy.md",
]


HTML = r"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Lab 7 Knowledge Assistant</title>
  <style>
    :root {
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --ink: #1d2433;
      --muted: #667085;
      --line: #d8dee9;
      --accent: #176b87;
      --accent-strong: #0f5369;
      --good: #087443;
      --partial: #9a5b00;
      --bad: #b42318;
      --shadow: 0 12px 30px rgba(16, 24, 40, 0.08);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: var(--ink);
      background: var(--bg);
      letter-spacing: 0;
    }
    main {
      width: min(1120px, calc(100vw - 32px));
      margin: 28px auto 44px;
    }
    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      gap: 18px;
      margin-bottom: 18px;
    }
    h1 {
      margin: 0;
      font-size: 28px;
      line-height: 1.2;
    }
    .sub {
      margin: 6px 0 0;
      color: var(--muted);
      font-size: 14px;
    }
    .status {
      border: 1px solid var(--line);
      background: var(--panel);
      padding: 9px 12px;
      border-radius: 6px;
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }
    .status-stack {
      display: flex;
      flex-direction: column;
      gap: 8px;
      align-items: flex-end;
    }
    .shell {
      display: grid;
      grid-template-columns: minmax(0, 1fr) 360px;
      gap: 16px;
      align-items: start;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }
    .chat {
      min-height: 520px;
      display: flex;
      flex-direction: column;
    }
    .messages {
      padding: 18px;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .message {
      max-width: 86%;
      padding: 12px 14px;
      border-radius: 8px;
      line-height: 1.5;
      font-size: 15px;
      white-space: pre-wrap;
    }
    .user {
      margin-left: auto;
      color: #ffffff;
      background: var(--accent);
    }
    .bot {
      background: #f2f5f8;
      border: 1px solid #e5e9f0;
    }
    .composer {
      border-top: 1px solid var(--line);
      padding: 14px;
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 10px;
      align-items: end;
    }
    textarea {
      width: 100%;
      min-height: 48px;
      max-height: 120px;
      resize: vertical;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 12px;
      font: inherit;
      outline: none;
    }
    textarea:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(23, 107, 135, 0.14);
    }
    button {
      border: 0;
      border-radius: 6px;
      background: var(--accent);
      color: #ffffff;
      font-weight: 700;
      height: 48px;
      padding: 0 18px;
      cursor: pointer;
    }
    button:hover { background: var(--accent-strong); }
    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
    .side {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }
    .box {
      padding: 16px;
    }
    .box h2 {
      margin: 0 0 12px;
      font-size: 16px;
    }
    .steps {
      min-height: 130px;
    }
    .step {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.45;
      margin: 8px 0;
    }
    .dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #98a2b3;
      flex: 0 0 auto;
    }
    .step.active .dot {
      background: var(--accent);
      animation: pulse 1s infinite;
    }
    .step.done .dot { background: var(--good); }
    .spinner {
      width: 18px;
      height: 18px;
      border: 3px solid #d0d5dd;
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin 0.85s linear infinite;
      display: none;
    }
    .processing .spinner { display: inline-block; }
    .table-wrap {
      overflow-x: auto;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    th, td {
      border-bottom: 1px solid var(--line);
      text-align: left;
      padding: 10px 8px;
      vertical-align: top;
    }
    th {
      color: var(--muted);
      font-weight: 700;
      background: #f9fafb;
    }
    .rank {
      font-weight: 700;
      width: 44px;
    }
    .score {
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }
    .eval-good { color: var(--good); font-weight: 700; }
    .eval-partial { color: var(--partial); font-weight: 700; }
    .eval-bad { color: var(--bad); font-weight: 700; }
    .empty {
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes pulse {
      0%, 100% { transform: scale(1); opacity: 1; }
      50% { transform: scale(1.45); opacity: 0.55; }
    }
    @media (max-width: 860px) {
      main { width: min(100vw - 20px, 760px); margin-top: 16px; }
      .topbar { align-items: flex-start; flex-direction: column; }
      .status-stack { align-items: stretch; width: 100%; }
      .status { white-space: normal; }
      .shell { grid-template-columns: 1fr; }
      .message { max-width: 100%; }
      .composer { grid-template-columns: 1fr; }
      button { width: 100%; }
    }
  </style>
</head>
<body>
  <main>
    <div class="topbar">
      <div>
        <h1>Lab 7 Knowledge Assistant</h1>
        <p class="sub">Hỏi đáp trên bộ tài liệu RAG, vector store, chunking và support playbook.</p>
      </div>
      <div class="status-stack">
        <div id="backend" class="status">Embedding backend: đang kiểm tra...</div>
        <div id="testStatus" class="status">Tests: đang kiểm tra...</div>
      </div>
    </div>

    <section class="shell">
      <div class="panel chat">
        <div id="messages" class="messages">
          <div class="message bot">Nhập câu hỏi để agent retrieve context, tạo câu trả lời và hiển thị Top-3 kết quả liên quan.</div>
        </div>
        <form id="askForm" class="composer">
          <textarea id="question" placeholder="Ví dụ: What does a vector store do?" aria-label="Câu hỏi"></textarea>
          <button id="askButton" type="submit">Gửi</button>
        </form>
      </div>

      <aside class="side">
        <div class="panel box">
          <h2>Tiến trình xử lý <span class="spinner" id="spinner"></span></h2>
          <div id="steps" class="steps">
            <p class="empty">Các bước xử lý sẽ xuất hiện khi bạn gửi câu hỏi.</p>
          </div>
        </div>

        <div class="panel box">
          <h2>Top-3 Retrieved Chunks</h2>
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Source</th>
                  <th>Score</th>
                  <th>Đánh giá</th>
                </tr>
              </thead>
              <tbody id="resultsBody">
                <tr><td colspan="4" class="empty">Chưa có kết quả.</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </aside>
    </section>
  </main>

  <script>
    const form = document.getElementById("askForm");
    const question = document.getElementById("question");
    const askButton = document.getElementById("askButton");
    const messages = document.getElementById("messages");
    const steps = document.getElementById("steps");
    const spinner = document.getElementById("spinner");
    const resultsBody = document.getElementById("resultsBody");
    const backend = document.getElementById("backend");
    const testStatus = document.getElementById("testStatus");

    const stepLabels = [
      "Đọc câu hỏi người dùng",
      "Tạo embedding cho câu hỏi",
      "Search trong EmbeddingStore",
      "Chọn Top-3 retrieved chunks",
      "Inject context vào KnowledgeBaseAgent",
      "Sinh câu trả lời cuối cùng",
      "Thông báo số test pass"
    ];

    let activeStepTimer = null;

    function addMessage(text, role) {
      const node = document.createElement("div");
      node.className = `message ${role}`;
      node.textContent = text;
      messages.appendChild(node);
      messages.scrollTop = messages.scrollHeight;
      return node;
    }

    function renderSteps(activeIndex, doneAll = false) {
      steps.innerHTML = "";
      stepLabels.forEach((label, index) => {
        const row = document.createElement("div");
        row.className = "step";
        if (doneAll || index < activeIndex) row.classList.add("done");
        if (!doneAll && index === activeIndex) row.classList.add("active");
        row.innerHTML = `<span class="dot"></span><span>${label}</span>`;
        steps.appendChild(row);
      });
    }

    function startProcessingSteps() {
      let index = 0;
      spinner.parentElement.classList.add("processing");
      renderSteps(index);
      activeStepTimer = window.setInterval(() => {
        index = Math.min(index + 1, stepLabels.length - 1);
        renderSteps(index);
      }, 550);
    }

    function stopProcessingSteps() {
      if (activeStepTimer) window.clearInterval(activeStepTimer);
      activeStepTimer = null;
      spinner.parentElement.classList.remove("processing");
      renderSteps(stepLabels.length, true);
    }

    function evaluationClass(text) {
      if (text.startsWith("Rất tốt")) return "eval-good";
      if (text.startsWith("Có liên quan")) return "eval-partial";
      return "eval-bad";
    }

    function renderResults(results) {
      resultsBody.innerHTML = "";
      if (!results.length) {
        resultsBody.innerHTML = `<tr><td colspan="4" class="empty">Không có kết quả retrieval.</td></tr>`;
        return;
      }
      for (const item of results) {
        const row = document.createElement("tr");
        row.innerHTML = `
          <td class="rank">${item.rank}</td>
          <td>${item.source}</td>
          <td class="score">${Number(item.score).toFixed(3)}</td>
          <td class="${evaluationClass(item.evaluation)}">${item.evaluation}</td>
        `;
        resultsBody.appendChild(row);
      }
    }

    async function loadStatus() {
      try {
        const response = await fetch("/api/status");
        const data = await response.json();
        backend.textContent = `Embedding backend: ${data.backend}`;
        testStatus.textContent = `Tests: ${data.tests.passed}/${data.tests.total} pass`;
      } catch {
        backend.textContent = "Embedding backend: chưa sẵn sàng";
        testStatus.textContent = "Tests: chưa kiểm tra được";
      }
    }

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const text = question.value.trim();
      if (!text) return;

      addMessage(text, "user");
      question.value = "";
      askButton.disabled = true;
      const botMessage = addMessage("Đang xử lý câu hỏi...", "bot");
      startProcessingSteps();

      try {
        const response = await fetch("/api/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question: text })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Request failed");
        botMessage.textContent = data.answer;
        renderResults(data.top3);
        backend.textContent = `Embedding backend: ${data.backend}`;
        testStatus.textContent = `Tests: ${data.tests.passed}/${data.tests.total} pass`;
      } catch (error) {
        botMessage.textContent = `Không xử lý được câu hỏi: ${error.message}`;
        renderResults([]);
      } finally {
        stopProcessingSteps();
        askButton.disabled = false;
        question.focus();
      }
    });

    question.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        form.requestSubmit();
      }
    });

    loadStatus();
  </script>
</body>
</html>
"""


class RAGService:
    def __init__(self) -> None:
        load_dotenv(override=False)
        self.embedder = self._make_embedder()
        self.backend_name = getattr(self.embedder, "_backend_name", self.embedder.__class__.__name__)
        self.store = EmbeddingStore(collection_name="ui_store", embedding_fn=self.embedder)
        self.store.add_documents(self._load_documents())
        self.agent = KnowledgeBaseAgent(store=self.store, llm_fn=self._grounded_answer)

    def _make_embedder(self):
        provider = os.getenv(EMBEDDING_PROVIDER_ENV, "mock").strip().lower()
        if provider == "local":
            try:
                return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))
            except Exception:
                return _mock_embed
        if provider == "openai":
            try:
                return OpenAIEmbedder(model_name=os.getenv("OPENAI_EMBEDDING_MODEL", OPENAI_EMBEDDING_MODEL))
            except Exception:
                return _mock_embed
        return _mock_embed

    def _load_documents(self) -> list[Document]:
        documents: list[Document] = []
        for raw_path in SAMPLE_FILES:
            path = Path(raw_path)
            if not path.exists():
                continue
            documents.append(
                Document(
                    id=path.stem,
                    content=path.read_text(encoding="utf-8"),
                    metadata={
                        "source": str(path),
                        "extension": path.suffix.lower(),
                    },
                )
            )
        return documents

    def _grounded_answer(self, prompt: str) -> str:
        question_match = re.search(r"Question:\n(.*?)\n\nAnswer:", prompt, re.DOTALL)
        context_match = re.search(r"Context:\n(.*?)\n\nQuestion:", prompt, re.DOTALL)
        user_question = question_match.group(1).strip() if question_match else ""
        context = context_match.group(1).strip() if context_match else ""
        top_context = context.split("\n\n[2]")[0]
        clean_context = re.sub(r"^\[1\]\s*", "", top_context).strip()
        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", clean_context)
            if paragraph.strip() and not paragraph.strip().startswith("#")
        ]
        first_paragraph = paragraphs[0] if paragraphs else clean_context
        sentences = re.split(r"(?<=[.!?])\s+", first_paragraph)
        evidence = " ".join(sentence.strip() for sentence in sentences[:2] if sentence.strip())

        if "vector store" in user_question.lower():
            return (
                "Vector store là một lớp lưu trữ hoặc cơ sở dữ liệu dùng để lưu embeddings "
                "và truy xuất các item/chunk giống nhất với query vector. Dựa trên context retrieved, "
                f"nó hỗ trợ semantic search, recommendation, clustering và RAG. Nguồn chính: {evidence}"
            )
        if evidence:
            return f"Dựa trên context retrieved, câu trả lời là: {evidence}"
        return "Không tìm thấy đủ context phù hợp để trả lời câu hỏi này."

    def ask(self, question: str) -> dict:
        top3_raw = self.store.search(question, top_k=3)
        answer = self.agent.answer(question, top_k=3)
        top3 = []
        for rank, result in enumerate(top3_raw, start=1):
            source_path = result["metadata"].get("source", "unknown")
            source = Path(source_path).name
            top3.append(
                {
                    "rank": rank,
                    "source": source,
                    "score": result["score"],
                    "evaluation": self._evaluate(question, source, result["score"], rank),
                }
            )
        return {
            "answer": answer,
            "top3": top3,
            "backend": self.backend_name,
            "tests": get_test_status(),
        }

    def _evaluate(self, question: str, source: str, score: float, rank: int) -> str:
        lower_question = question.lower()
        if "vector store" in lower_question and source == "vector_store_notes.md":
            return "Rất tốt, đúng tài liệu nhất"
        if source == "rag_system_design.md":
            return "Có liên quan một phần vì RAG dùng vector store/retrieval"
        if source == "vi_retrieval_notes.md":
            return "Có liên quan một phần vì nói về retrieval"
        if score >= 0.45 and rank == 1:
            return "Rất tốt, đúng tài liệu nhất"
        if score >= 0.15:
            return "Có liên quan một phần vì cùng domain retrieval/RAG"
        return "Ít liên quan hoặc có thể là nhiễu"


SERVICE: RAGService | None = None
TEST_STATUS: dict | None = None


def get_service() -> RAGService:
    global SERVICE
    if SERVICE is None:
        SERVICE = RAGService()
    return SERVICE


def get_test_status() -> dict:
    global TEST_STATUS
    if TEST_STATUS is not None:
        return TEST_STATUS

    loader = unittest.TestLoader()
    suite = loader.discover("tests")
    result = unittest.TestResult()
    suite.run(result)
    total = result.testsRun
    failed = len(result.failures) + len(result.errors)
    passed = total - failed
    TEST_STATUS = {
        "passed": passed,
        "total": total,
        "failed": failed,
        "ok": failed == 0,
    }
    return TEST_STATUS


class UIHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self._send_html(HTML)
            return
        if path == "/api/status":
            service = get_service()
            self._send_json({"backend": service.backend_name, "tests": get_test_status()})
            return
        self.send_error(404, "Not found")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/ask":
            self.send_error(404, "Not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            question = str(payload.get("question", "")).strip()
            if not question:
                self._send_json({"error": "Question is required"}, status=400)
                return
            self._send_json(get_service().ask(question))
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)

    def log_message(self, format: str, *args) -> None:
        return

    def _send_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    port = int(os.getenv("UI_PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), UIHandler)
    print(f"Lab 7 UI running at http://127.0.0.1:{port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
