-- Sample queries for LegalAI database

-- 1. User Management Queries

-- Get user by email
SELECT * FROM users WHERE email = 'user@example.com';

-- Update user verification status
UPDATE users 
SET is_verified = TRUE, verification_code = NULL, verification_code_expires = NULL 
WHERE email = 'user@example.com' AND verification_code = '123456';

-- Reset password token setup
UPDATE users 
SET reset_password_token = 'reset_token_here', reset_password_expires = NOW() + INTERVAL '1 hour' 
WHERE email = 'user@example.com';

-- Update password and clear reset token
UPDATE users 
SET password_hash = 'new_hashed_password', reset_password_token = NULL, reset_password_expires = NULL 
WHERE email = 'user@example.com' AND reset_password_token = 'reset_token_here';

-- 2. User Preferences Queries

-- Insert or update user preference
INSERT INTO user_preferences (user_email, preference_key, preference_value) 
VALUES ('user@example.com', 'theme', 'dark')
ON CONFLICT (user_email, preference_key) 
DO UPDATE SET preference_value = EXCLUDED.preference_value, updated_at = CURRENT_TIMESTAMP;

-- Get all user preferences
SELECT preference_key, preference_value 
FROM user_preferences 
WHERE user_email = 'user@example.com';

-- Get specific preference
SELECT preference_value 
FROM user_preferences 
WHERE user_email = 'user@example.com' AND preference_key = 'theme';

-- 3. Chat History Queries

-- Create new chat session
INSERT INTO chat_sessions (user_email, session_name) 
VALUES ('user@example.com', 'Legal Consultation - 2025-09-06') 
RETURNING id;

-- Get user's chat sessions
SELECT id, session_name, created_at, updated_at 
FROM chat_sessions 
WHERE user_email = 'user@example.com' 
ORDER BY updated_at DESC;

-- Add message to chat history
INSERT INTO chat_history (session_id, user_email, message_role, message_content, message_metadata) 
VALUES (1, 'user@example.com', 'user', 'What are the property laws in Sri Lanka?', '{"query_type": "legal_question"}');

-- Get chat history for a session
SELECT message_role, message_content, message_metadata, created_at 
FROM chat_history 
WHERE session_id = 1 
ORDER BY created_at ASC;

-- Get recent chat history for user (last 50 messages)
SELECT ch.message_role, ch.message_content, ch.created_at, cs.session_name
FROM chat_history ch
JOIN chat_sessions cs ON ch.session_id = cs.id
WHERE ch.user_email = 'user@example.com'
ORDER BY ch.created_at DESC
LIMIT 50;

-- 4. User Activity Queries

-- Log user activity
INSERT INTO user_activity_logs (user_email, activity_type, activity_description, ip_address, user_agent) 
VALUES ('user@example.com', 'login', 'User logged in successfully', '192.168.1.1', 'Mozilla/5.0...');

-- Get user activity history
SELECT activity_type, activity_description, ip_address, created_at 
FROM user_activity_logs 
WHERE user_email = 'user@example.com' 
ORDER BY created_at DESC 
LIMIT 20;

-- 5. Analytics Queries

-- Count total users
SELECT COUNT(*) as total_users FROM users;

-- Count verified users
SELECT COUNT(*) as verified_users FROM users WHERE is_verified = TRUE;

-- Most active users by chat messages
SELECT user_email, COUNT(*) as message_count 
FROM chat_history 
GROUP BY user_email 
ORDER BY message_count DESC 
LIMIT 10;

-- Chat activity by date
SELECT DATE(created_at) as date, COUNT(*) as message_count 
FROM chat_history 
GROUP BY DATE(created_at) 
ORDER BY date DESC;

-- 6. Cleanup Queries

-- Remove expired verification codes
UPDATE users 
SET verification_code = NULL, verification_code_expires = NULL 
WHERE verification_code_expires < NOW();

-- Remove expired reset tokens
UPDATE users 
SET reset_password_token = NULL, reset_password_expires = NULL 
WHERE reset_password_expires < NOW();

-- Delete old activity logs (older than 6 months)
DELETE FROM user_activity_logs 
WHERE created_at < NOW() - INTERVAL '6 months';

-- 7. Data Maintenance

-- Get database statistics
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats 
WHERE schemaname = 'public' 
ORDER BY tablename, attname;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
