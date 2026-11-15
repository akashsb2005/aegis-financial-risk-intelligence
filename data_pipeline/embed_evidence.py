"""Create local 384-dimensional evidence embeddings and store them in pgvector.

The default model is sentence-transformers/all-MiniLM-L6-v2. No API key is used.
Run database/vector/01_pgvector_evidence.sql first on a PostgreSQL server with pgvector.
"""
from __future__ import annotations

import argparse
import os

import psycopg
from pgvector.psycopg import register_vector
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DIMENSION = 384


def embed_pending(dsn: str, batch_size: int = 32) -> int:
    model = SentenceTransformer(MODEL_NAME)
    if model.get_sentence_embedding_dimension() != DIMENSION:
        raise ValueError(f"Expected {DIMENSION}-dimension embeddings from {MODEL_NAME}")
    with psycopg.connect(dsn) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                """SELECT source_uri, title, content, published_at
                   FROM public.news_articles n
                   WHERE NOT EXISTS (
                     SELECT 1 FROM public.evidence_embeddings e
                     WHERE e.source_uri = n.source_uri
                   )
                   ORDER BY n.published_at NULLS LAST, n.article_id
                   """
            )
            rows = cur.fetchall()
        inserted = 0
        with conn.cursor() as cur:
            for start in range(0, len(rows), batch_size):
                batch = rows[start:start + batch_size]
                texts = [f"{title}\n{content}" for _, title, content, _ in batch]
                vectors = model.encode(texts, normalize_embeddings=True)
                for (uri, title, content, published_at), vector in zip(batch, vectors):
                    cur.execute(
                        """INSERT INTO public.evidence_embeddings
                           (source_uri, source_title, content, embedding, published_at)
                           VALUES (%s,%s,%s,%s,%s)
                           ON CONFLICT (source_uri) DO NOTHING""",
                        (uri, title, content, vector, published_at),
                    )
                    inserted += cur.rowcount
        conn.commit()
    return inserted


def search_evidence(dsn: str, query: str, limit: int = 5) -> list[dict]:
    model = SentenceTransformer(MODEL_NAME)
    vector = model.encode(query, normalize_embeddings=True)
    with psycopg.connect(dsn) as conn:
        register_vector(conn)
        with conn.cursor() as cur:
            cur.execute(
                """SELECT source_uri, source_title, content,
                          1 - (embedding <=> %s) AS similarity
                   FROM public.evidence_embeddings
                   ORDER BY embedding <=> %s
                   LIMIT %s""",
                (vector, vector, limit),
            )
            return [
                {"source_uri": row[0], "title": row[1],
                 "content": row[2], "similarity": float(row[3])}
                for row in cur.fetchall()
            ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search", help="Search evidence instead of embedding pending articles")
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()
    if not 1 <= args.limit <= 20:
        raise SystemExit("--limit must be between 1 and 20")
    dsn = os.environ.get("AEGIS_PG_DSN")
    if not dsn:
        raise SystemExit("Set AEGIS_PG_DSN to a PostgreSQL connection string.")
    if args.search:
        for item in search_evidence(dsn, args.search, args.limit):
            print(f"{item['similarity']:.3f} | {item['title']} | {item['source_uri']}")
            print(item["content"][:500])
    else:
        print(f"Embedded {embed_pending(dsn)} new articles.")


if __name__ == "__main__":
    main()
