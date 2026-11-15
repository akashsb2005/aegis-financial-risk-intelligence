# Financial news, event and semantic-evidence pipeline

## RSS ingestion

The RSS/Atom adapter stores source-linked articles for a ticker already registered in `public.securities`. It preserves publisher/feed name, canonical source URL and publication time. A small transparent keyword classifier creates **event candidates** for earnings, M&A, dividends, regulatory actions, litigation, bankruptcy and leadership changes. These are candidates for review, not verified facts.

Run:

```powershell
pip install -r data_pipeline/requirements.txt
$env:AEGIS_PG_DSN = "postgresql://USER:PASSWORD@localhost:5432/DBNAME"
python data_pipeline/ingest_rss.py --ticker AAPL --feed-url "https://YOUR-PERMITTED-FEED/rss"
```

Use feeds whose terms permit collection and storage. Avoid scraping sites that prohibit automated access. The pipeline does not bypass paywalls or access controls. Duplicate source URLs are ignored.

## Semantic evidence retrieval

Apply `database/vector/01_pgvector_evidence.sql` on a PostgreSQL server with the pgvector extension available. Install local embedding dependencies:

```powershell
pip install -r data_pipeline/embedding-requirements.txt
python data_pipeline/embed_evidence.py
python data_pipeline/embed_evidence.py --search "regulatory investigation and earnings risk" --limit 5
```

The local `sentence-transformers/all-MiniLM-L6-v2` model emits 384-dimensional vectors, matching the existing pgvector table. First model use downloads model weights; no paid API key is needed. The first run may take time and disk space.

## Provenance and limits

Semantic matches are retrieval candidates, not proof. The application must show the original source URL and publication date and should not present keyword-classified events as verified events. RSS coverage varies by publisher and is not a complete financial-news feed.
