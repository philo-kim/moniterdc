-- Migration 402: Remove deprecated tables
-- Purpose: Clean up old system tables that are no longer used in v2.0

-- Remove old perception system (replaced by layered_perceptions)
DROP TABLE IF EXISTS perceptions CASCADE;

-- Remove belief patterns system (not used in UI)
DROP TABLE IF EXISTS belief_patterns CASCADE;

-- Remove perception connections (not used)
DROP TABLE IF EXISTS perception_connections CASCADE;

-- Remove old logic cluster system (replaced by worldview system)
DROP TABLE IF EXISTS logic_clusters CASCADE;
DROP TABLE IF EXISTS logic_repository CASCADE;
DROP TABLE IF EXISTS logic_matches CASCADE;

-- Remove counter argument system (not implemented in UI)
DROP TABLE IF EXISTS counter_arguments CASCADE;
DROP TABLE IF EXISTS rebuttals CASCADE;
DROP TABLE IF EXISTS rebuttal_votes CASCADE;
DROP TABLE IF EXISTS counter_argument_votes CASCADE;

-- Remove unused utility tables
DROP TABLE IF EXISTS alerts CASCADE;
DROP TABLE IF EXISTS system_stats CASCADE;

-- Clean up any related views
DROP VIEW IF EXISTS cluster_with_logics CASCADE;
DROP VIEW IF EXISTS attack_logic_with_counters CASCADE;

COMMENT ON DATABASE postgres IS 'MoniterDC v2.0 - Cleaned up deprecated tables, focusing on layered_perceptions and worldviews system';
