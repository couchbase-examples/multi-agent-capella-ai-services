"""Couchbase RAG Tool for retrieving Seinfeld script examples using vector search."""

import os
from datetime import timedelta
from typing import Any, Optional, Type

from crewai.tools import BaseTool
from langchain_couchbase.vectorstores import DistanceStrategy
from pydantic import BaseModel, Field
from langchain_openai import OpenAIEmbeddings
from langchain_couchbase import CouchbaseQueryVectorStore


class SeinfeldSearchInput(BaseModel):
    """Input schema for the Seinfeld RAG search tool."""

    query: str = Field(
        description="The search query to find relevant Seinfeld dialogue or scenes. "
        "Be specific about what you're looking for, e.g., 'George complaining about his job' "
        "or 'Jerry making observational jokes about dating'."
    )
    num_results: int = Field(
        default=5,
        description="Number of results to return (1-10). More results give more context "
        "but may include less relevant examples.",
        ge=1,
        le=10,
    )


class SeinfeldRAGTool(BaseTool):
    """
    A tool for searching Seinfeld scripts stored in Couchbase using vector similarity search.

    This tool connects to a Couchbase cluster containing Seinfeld episode dialogues with pre-computed embeddings. It performs semantic search to find dialogues
    that are similar to the query, enabling RAG (Retrieval Augmented Generation) for
    authentic Seinfeld script generation.
    """

    name: str = "seinfeld_script_search"
    description: str = (
        "Search the Seinfeld script database to find similar dialogue, scenes, or character "
        "interactions. Use this tool to retrieve authentic examples from the show that can "
        "inform your writing. You can search for specific character dialogues, themes, "
        "situations, or comedic patterns. Returns actual dialogue from Seinfeld episodes "
        "that match your query semantically."
    )
    args_schema: Type[BaseModel] = SeinfeldSearchInput

    # Couchbase connection settings
    _cluster: Any = None
    _bucket: Any = None
    _scope: Any = None
    _collection: Any = None
    _openai_client: Any = None
    _embeddings: Any = None
    _vector_store: Any = None

    def __init__(self, **kwargs):
        """Initialize the Seinfeld RAG Tool."""
        super().__init__(**kwargs)
        self._initialize_connections()

    def _initialize_connections(self):
        """Initialize Couchbase and OpenAI connections."""
        try:
            from couchbase.auth import PasswordAuthenticator
            from couchbase.cluster import Cluster
            from couchbase.options import ClusterOptions
            from openai import OpenAI

            # Get connection settings from environment
            connection_string = os.getenv("CB_CONNECTION_STRING")
            username = os.getenv("CB_USERNAME")
            password = os.getenv("CB_PASSWORD")
            bucket_name = os.getenv("CB_BUCKET")
            scope_name = os.getenv("CB_SCOPE")
            collection_name = os.getenv("CB_COLLECTION")

            # Connect to Couchbase
            auth = PasswordAuthenticator(username, password)
            options = ClusterOptions(auth)
            self._cluster = Cluster(connection_string, options)
            self._cluster.wait_until_ready(timedelta(seconds=10))

            self._bucket = self._cluster.bucket(bucket_name)
            self._scope = self._bucket.scope(scope_name)
            self._collection = self._scope.collection(collection_name)

            self._embeddings = OpenAIEmbeddings(
                    openai_api_key=os.getenv("EMBEDDING_API_KEY"),
                    openai_api_base=os.getenv("CAPELLA_AI_ENDPOINT"),
                    check_embedding_ctx_length=False,
                    tiktoken_enabled=False,
                    model=os.getenv("EMBEDDING_MODEL_NAME"),
                )

            self._vector_store = CouchbaseQueryVectorStore(
                cluster=self._cluster,
                embedding=self._embeddings,
                bucket_name=bucket_name,
                scope_name=scope_name,
                collection_name=collection_name,
                distance_metric=DistanceStrategy.DOT,
                text_key="Dialogue",
                embedding_key="dialogue_embedding",
            )
        except Exception as e:
            print(f"Warning: Could not initialize Couchbase connection: {e}")
            print("The tool will operate in demo mode with sample responses.")

    def _vector_search(self, query: str, num_results: int, character: Optional[str] = None) -> list[dict]:
        """Perform vector search in Couchbase."""
        try:
            results = self._vector_store.similarity_search(query, k=num_results, fields=["Character", "EpisodeNo", "Season"])
            return results

        except Exception as e:
            print(f"Vector search error: {e}")
            return []

    def _run(self, query: str, num_results: int = 5) -> str:
        """
        Execute the Seinfeld script search.

        Args:
            query: The search query to find relevant Seinfeld content
            num_results: Number of results to return

        Returns:
            Formatted string containing relevant Seinfeld dialogue examples
        """
        # Check if connections are initialized
        if self._cluster is None or self._openai_client is None:
            return self._get_demo_response(query)

        # Perform vector search
        results = self._vector_search(query, num_results)

        if not results:
            return self._get_demo_response(query)

        # Format results
        formatted_results = self._format_results(results, query)
        return formatted_results

    def _format_results(self, results: list[dict], query: str) -> str:
        """Format search results into a readable string."""
        output = f"## Seinfeld Script Search Results\n"
        output += f"**Query:** {query}\n"
        output += f"**Found {len(results)} relevant examples:**\n\n"

        for i, result in enumerate(results, 1):
            output += f"### Example {i}\n"

            # Add metadata if available
            metadata = result.get("metadata", {})
            if metadata:
                if "title" in metadata:
                    output += f"**Episode:** {metadata['title']}\n"
                if "description" in metadata:
                    output += f"**Context:** {metadata['description']}\n"

            # Add the actual dialogue/text
            text = result.get("text", "")
            if text:
                output += f"**Dialogue:**\n```\n{text[:1000]}{'...' if len(text) > 1000 else ''}\n```\n"

            output += f"**Relevance Score:** {result.get('score', 'N/A')}\n\n"
            output += "---\n\n"

        return output

    def _get_demo_response(self, query: str) -> str:
        """Return demo response when Couchbase is not available."""
        demo_dialogues = {
            "default": """
## Seinfeld Script Search Results (Demo Mode)
**Note:** Running in demo mode - Couchbase connection not available.

### Example 1 - Jerry's Apartment
**Context:** Classic observational comedy setup

```
JERRY: See, that's the thing about [topic]. Everyone acts like it's normal, 
but have you ever really thought about it? I mean, really thought about it?

GEORGE: What's there to think about? It's [topic]!

JERRY: Exactly! That's my point. We just accept it.

GEORGE: (getting agitated) Well what am I supposed to do, Jerry? Question 
everything? I've got enough problems!
```

### Example 2 - Monk's Coffee Shop
**Context:** George's paranoid interpretation

```
GEORGE: You know what I think? I think this whole [topic] thing is a conspiracy.

ELAINE: George, not everything is a conspiracy.

GEORGE: That's exactly what they want you to think!

KRAMER: (sliding into booth) I'm telling you, I've been saying this for years. 
[Topic]! It's all connected!

JERRY: Here we go.
```

### Example 3 - Jerry's Apartment
**Context:** Kramer's enthusiastic scheme

```
KRAMER: Jerry! Jerry! You're not gonna believe this!

JERRY: What now?

KRAMER: I've figured out the whole [topic] situation. It's genius!

JERRY: Kramer, the last time you had a genius idea, you ended up in the 
Hudson River.

KRAMER: That was different. That was a miscalculation. This? This is foolproof!

JERRY: (to camera) Nothing's foolproof when it comes to Kramer.
```

---
Use these examples as templates for the style, rhythm, and character voices.
""",
        }

        return demo_dialogues["default"].replace("[topic]", query.split()[0] if query else "this")

