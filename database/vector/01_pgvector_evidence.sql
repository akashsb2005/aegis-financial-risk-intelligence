-- AEGIS optional semantic-evidence retrieval extension
-- This migration is intentionally separate from the core PostgreSQL schema.
-- It requires pgvector to be installed on the PostgreSQL server.
-- Choose the vector dimension to match the embedding model actually deployed.
-- The 384-dimensional example below is suitable only for a model that emits 384 values.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS public.evidence_embeddings (
    evidence_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_uri TEXT NOT NULL,
    source_title TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(384) NOT NULL,
    published_at TIMESTAMPTZ,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_evidence_source UNIQUE (source_uri)
);

CREATE INDEX IF NOT EXISTS idx_evidence_embeddings_cosine
ON public.evidence_embeddings
USING hnsw (embedding vector_cosine_ops);

-- Insert only after generating a real 384-dimensional embedding:
-- INSERT INTO public.evidence_embeddings
--   (source_uri, source_title, content, embedding, published_at)
-- VALUES
--   ('https://example.org/report/1', 'Example risk filing',
--    'Example source text...', '[0.01, ...]'::vector, now());

-- Similarity retrieval; bind a real embedding from the same model:
-- SELECT evidence_id, source_uri, source_title,
--        1 - (embedding <=> '[0.01, ...]'::vector) AS cosine_similarity
-- FROM public.evidence_embeddings
-- ORDER BY embedding <=> '[0.01, ...]'::vector
-- LIMIT 5;

-- Inspect vector extension and index:
-- SELECT extname FROM pg_extension WHERE extname = 'vector';
-- SELECT indexname FROM pg_indexes
-- WHERE tablename = 'evidence_embeddings';
