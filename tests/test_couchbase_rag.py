"""Tests for the SeinfeldRAGTool vector-store seam.

These run without Couchbase or Capella AI: a fake vector store is injected
through the tool's ``vector_store`` constructor argument.
"""

from langchain_core.documents import Document

from seinfeld_script_generator.tools.couchbase_rag import SeinfeldRAGTool


class FakeVectorStore:
    def __init__(self, docs=None, error=None):
        self.docs = docs or []
        self.error = error
        self.calls = []

    def similarity_search(self, query, k=4, **kwargs):
        self.calls.append((query, k, kwargs))
        if self.error:
            raise self.error
        return self.docs[:k]


def test_run_searches_injected_vector_store_and_formats_documents():
    store = FakeVectorStore(
        docs=[
            Document(
                page_content="What's the deal with airline peanuts?",
                metadata={"Character": "JERRY", "Season": 1, "EpisodeNo": 15},
            )
        ]
    )
    tool = SeinfeldRAGTool(vector_store=store)

    output = tool._run("airline food", num_results=3)

    assert store.calls == [
        ("airline food", 3, {"fields": ["Character", "EpisodeNo", "Season"]})
    ]
    assert "Demo Mode" not in output
    assert "**Found 1 relevant examples:**" in output
    assert "**Character:** JERRY" in output
    assert "**Episode:** Season 1, Episode 15" in output
    assert "What's the deal with airline peanuts?" in output


def test_run_falls_back_to_demo_when_search_returns_nothing():
    tool = SeinfeldRAGTool(vector_store=FakeVectorStore(docs=[]))

    assert "Demo Mode" in tool._run("parking")


def test_run_falls_back_to_demo_when_search_errors():
    tool = SeinfeldRAGTool(vector_store=FakeVectorStore(error=RuntimeError("boom")))

    assert "Demo Mode" in tool._run("parking")


def test_run_uses_demo_mode_when_vector_store_unavailable(monkeypatch):
    monkeypatch.setattr(SeinfeldRAGTool, "_initialize_connections", lambda self: None)
    tool = SeinfeldRAGTool()

    assert "Demo Mode" in tool._run("parking")
