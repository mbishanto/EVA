-- EVA AI Assistant - Supabase Database Schema
-- Run this in your Supabase SQL Editor to set up tables

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==================== USERS ====================

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name TEXT DEFAULT '',
    notes JSONB DEFAULT '[]'::jsonb,
    summary TEXT DEFAULT '',
    emotions JSONB DEFAULT '[]'::jsonb,
    relationship JSONB DEFAULT '{"favorite_topics": [], "friendship_level": 0}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ==================== CONVERSATIONS ====================

CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title TEXT DEFAULT 'New Chat',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id
    ON conversations(user_id);

CREATE INDEX IF NOT EXISTS idx_conversations_updated_at
    ON conversations(updated_at DESC);

-- ==================== MESSAGES ====================

CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    token_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
    ON messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_messages_created_at
    ON messages(created_at ASC);

-- ==================== ROW LEVEL SECURITY ====================

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- Users can only see their own data
CREATE POLICY user_own_data ON users
    FOR ALL
    USING (user_id = auth.uid()::text);

CREATE POLICY user_own_conversations ON conversations
    FOR ALL
    USING (user_id = auth.uid()::text);

CREATE POLICY user_own_messages ON messages
    FOR ALL
    USING (
        conversation_id IN (
            SELECT id FROM conversations WHERE user_id = auth.uid()::text
        )
    );
