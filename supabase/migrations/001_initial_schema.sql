-- DC Gallery Monitoring System Database Schema
-- Version: 1.0.0
-- Date: 2024

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search

-- Create custom types
CREATE TYPE gallery_type AS ENUM ('minjoo', 'kukmin', 'politics', 'other');
CREATE TYPE alert_severity AS ENUM ('critical', 'high', 'medium', 'low', 'info');
CREATE TYPE analysis_status AS ENUM ('pending', 'processing', 'completed', 'failed');
CREATE TYPE job_status AS ENUM ('queued', 'running', 'completed', 'failed', 'cancelled');

-- 1. Posts table (게시글)
CREATE TABLE posts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    gallery_id VARCHAR(50) NOT NULL,
    gallery_type gallery_type NOT NULL,
    post_num BIGINT NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    author VARCHAR(100),
    author_ip VARCHAR(50),
    views INTEGER DEFAULT 0,
    recommends INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    has_image BOOLEAN DEFAULT false,
    post_url TEXT NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    crawled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes for deduplication
    UNIQUE(gallery_id, post_num)
);

-- 2. Analysis Results table (AI 분석 결과)
CREATE TABLE analysis_results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    
    -- AI Analysis
    ai_model VARCHAR(50) NOT NULL,
    importance_score DECIMAL(3,1) CHECK (importance_score >= 0 AND importance_score <= 10),
    sentiment_score DECIMAL(3,2) CHECK (sentiment_score >= -1 AND sentiment_score <= 1),
    sentiment_label VARCHAR(20), -- positive, negative, neutral
    
    -- Classification & Keywords
    classification JSONB, -- {category: 'policy', subcategory: 'economy'}
    keywords TEXT[], -- Array of keywords
    entities JSONB, -- Named entities: people, organizations, locations
    
    -- Frame Analysis
    frame_analysis JSONB, -- Political framing detection
    
    -- Strategy (for important posts)
    strategy_json JSONB, -- AI generated response strategy
    risk_level VARCHAR(20), -- low, medium, high, critical
    
    -- Metadata
    analysis_status analysis_status DEFAULT 'pending',
    processing_time_ms INTEGER,
    token_usage JSONB, -- {input: 100, output: 50, total: 150}
    cost_usd DECIMAL(10,6),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Alerts table (알림)
CREATE TABLE alerts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    post_id UUID REFERENCES posts(id) ON DELETE SET NULL,
    analysis_id UUID REFERENCES analysis_results(id) ON DELETE SET NULL,
    
    severity alert_severity NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    
    -- Alert details
    alert_type VARCHAR(50), -- new_issue, trending, sentiment_shift, etc.
    metadata JSONB, -- Additional context
    
    -- Recipients & Delivery
    recipients TEXT[], -- Telegram user/group IDs
    sent_at TIMESTAMP WITH TIME ZONE,
    sent_count INTEGER DEFAULT 0,
    
    -- Acknowledgment
    acknowledged BOOLEAN DEFAULT false,
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    
    -- Action taken
    action_taken TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Job Queue table (작업 큐)
CREATE TABLE job_queue (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    job_type VARCHAR(50) NOT NULL, -- crawl, analyze, alert, report
    job_status job_status DEFAULT 'queued',
    
    -- Job details
    payload JSONB NOT NULL,
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    
    -- Execution
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    
    -- Retry logic
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    last_error TEXT,
    
    -- Scheduling
    scheduled_for TIMESTAMP WITH TIME ZONE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. API Costs table (API 비용 추적)
CREATE TABLE api_costs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    service VARCHAR(50) NOT NULL, -- openai, telegram, etc.
    endpoint VARCHAR(100),
    model VARCHAR(50),
    
    -- Usage
    tokens_input INTEGER,
    tokens_output INTEGER,
    tokens_total INTEGER,
    requests_count INTEGER DEFAULT 1,
    
    -- Cost
    cost_usd DECIMAL(10,6) NOT NULL,
    
    -- Reference
    reference_id UUID, -- Can reference post_id, analysis_id, etc.
    reference_type VARCHAR(50), -- posts, analysis_results, etc.
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    date DATE DEFAULT CURRENT_DATE
);

-- 6. Keywords Trend table (키워드 트렌드)
CREATE TABLE keyword_trends (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    keyword VARCHAR(100) NOT NULL,
    gallery_type gallery_type,
    
    -- Metrics
    mention_count INTEGER DEFAULT 1,
    sentiment_avg DECIMAL(3,2),
    importance_avg DECIMAL(3,1),
    
    -- Time window
    time_window TIMESTAMP WITH TIME ZONE NOT NULL,
    window_duration INTERVAL DEFAULT '1 hour',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(keyword, gallery_type, time_window)
);

-- 7. System Logs table (시스템 로그)
CREATE TABLE system_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    log_level VARCHAR(20) NOT NULL, -- debug, info, warning, error, critical
    component VARCHAR(50) NOT NULL, -- crawler, analyzer, alerter, etc.
    
    message TEXT NOT NULL,
    details JSONB,
    
    -- Error tracking
    error_type VARCHAR(100),
    stack_trace TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_posts_gallery_created ON posts(gallery_id, created_at DESC);
CREATE INDEX idx_posts_importance ON posts USING btree(created_at DESC) WHERE EXISTS (
    SELECT 1 FROM analysis_results ar 
    WHERE ar.post_id = posts.id AND ar.importance_score > 7
);
CREATE INDEX idx_posts_fulltext ON posts USING gin(to_tsvector('korean', title || ' ' || coalesce(content, '')));

CREATE INDEX idx_analysis_post ON analysis_results(post_id);
CREATE INDEX idx_analysis_importance ON analysis_results(importance_score DESC);
CREATE INDEX idx_analysis_created ON analysis_results(created_at DESC);

CREATE INDEX idx_alerts_severity ON alerts(severity, created_at DESC);
CREATE INDEX idx_alerts_unsent ON alerts(sent_at) WHERE sent_at IS NULL;

CREATE INDEX idx_jobs_status ON job_queue(job_status, priority DESC, created_at);
CREATE INDEX idx_jobs_scheduled ON job_queue(scheduled_for) WHERE job_status = 'queued';

CREATE INDEX idx_costs_date ON api_costs(date DESC, service);
CREATE INDEX idx_costs_reference ON api_costs(reference_id, reference_type);

CREATE INDEX idx_keywords_trend ON keyword_trends(keyword, time_window DESC);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_posts_updated_at BEFORE UPDATE ON posts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_analysis_updated_at BEFORE UPDATE ON analysis_results
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON job_queue
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE OR REPLACE VIEW recent_important_posts AS
SELECT 
    p.*,
    ar.importance_score,
    ar.sentiment_score,
    ar.keywords,
    ar.risk_level
FROM posts p
JOIN analysis_results ar ON p.id = ar.post_id
WHERE ar.importance_score >= 7
    AND p.created_at >= NOW() - INTERVAL '24 hours'
ORDER BY ar.importance_score DESC, p.created_at DESC;

CREATE OR REPLACE VIEW daily_stats AS
SELECT 
    DATE(created_at) as date,
    gallery_type,
    COUNT(*) as post_count,
    AVG(views) as avg_views,
    AVG(recommends) as avg_recommends
FROM posts
GROUP BY DATE(created_at), gallery_type
ORDER BY date DESC;

CREATE OR REPLACE VIEW api_cost_summary AS
SELECT 
    date,
    service,
    model,
    SUM(tokens_total) as total_tokens,
    SUM(requests_count) as total_requests,
    SUM(cost_usd) as total_cost_usd
FROM api_costs
GROUP BY date, service, model
ORDER BY date DESC, total_cost_usd DESC;

-- Row Level Security (RLS) Policies
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE api_costs ENABLE ROW LEVEL SECURITY;
ALTER TABLE keyword_trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (adjust based on your auth strategy)
CREATE POLICY "Enable read access for all users" ON posts
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for service role" ON posts
    FOR INSERT WITH CHECK (auth.jwt() ->> 'role' = 'service_role');

-- Add similar policies for other tables...

-- Function to calculate daily costs
CREATE OR REPLACE FUNCTION get_daily_cost_total(target_date DATE DEFAULT CURRENT_DATE)
RETURNS DECIMAL AS $$
BEGIN
    RETURN (
        SELECT COALESCE(SUM(cost_usd), 0)
        FROM api_costs
        WHERE date = target_date
    );
END;
$$ LANGUAGE plpgsql;

-- Function to check if daily cost limit exceeded
CREATE OR REPLACE FUNCTION is_daily_cost_limit_exceeded(limit_usd DECIMAL DEFAULT 5.0)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN get_daily_cost_total() >= limit_usd;
END;
$$ LANGUAGE plpgsql;

-- Initial data (optional)
INSERT INTO system_logs (log_level, component, message, details) 
VALUES ('info', 'database', 'Database schema initialized', 
    '{"version": "1.0.0", "timestamp": "' || NOW() || '"}');

-- Grant permissions (adjust based on your needs)
GRANT USAGE ON SCHEMA public TO anon;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO authenticated;
