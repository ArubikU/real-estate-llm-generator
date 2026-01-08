-- Initialize pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_properties_embedding ON properties USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_documents_embedding ON documents USING hnsw (embedding vector_cosine_ops);

-- Enable full-text search
CREATE INDEX IF NOT EXISTS idx_properties_search ON properties USING gin(to_tsvector('english', content_for_search));
CREATE INDEX IF NOT EXISTS idx_documents_search ON documents USING gin(to_tsvector('english', content));
