CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    source VARCHAR(300) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL
        REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    n_chars INTEGER NOT NULL,
    embedding VECTOR(1536) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (document_id, chunk_index)
);

CREATE INDEX IF NOT EXISTS chunks_embedding_idx
ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE TABLE IF NOT EXISTS signatures (
    id SERIAL PRIMARY KEY,

    document_id INTEGER
        REFERENCES documents(id)
        ON DELETE CASCADE,

    filename TEXT NOT NULL,

    signature_png BYTEA NOT NULL,

    created_at TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW(),

    updated_at TIMESTAMPTZ
        NOT NULL
        DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS signatures_document_id_idx
    ON signatures(document_id);

CREATE INDEX IF NOT EXISTS signatures_filename_idx
    ON signatures(filename);