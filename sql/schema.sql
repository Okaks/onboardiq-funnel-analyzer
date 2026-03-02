CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    funnel_name TEXT NOT NULL,
    step_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    channel TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

SELECT * FROM events;

INSERT INTO events (
    user_id,
    funnel_name,
    step_name,
    event_type,
    channel
)
VALUES (
    'user_001',
    'bank_account_onboarding',
    'account_creation',
    'start',
    'web'
);

SELECT * FROM events;

INSERT INTO events (
    user_id,
    funnel_name,
    step_name,
    event_type,
    channel
)
VALUES
    ('user_001', 'bank_account_onboarding', 'identity_verification', 'step', 'web'),
    ('user_001', 'bank_account_onboarding', 'document_upload', 'step', 'web'),
    ('user_001', 'bank_account_onboarding', 'approval', 'complete', 'web');

SELECT * FROM events
ORDER BY created_at;


SELECT
    step_name,
    COUNT(*) AS event_count
FROM events
GROUP BY step_name
ORDER BY event_count DESC;

--- Inserting more data that includes dropoffs
INSERT INTO events (
    user_id,
    funnel_name,
    step_name,
    event_type,
    channel
)
VALUES
    
    ('user_002', 'bank_account_onboarding', 'account_creation', 'start', 'mobile'),
    ('user_002', 'bank_account_onboarding', 'identity_verification', 'step', 'mobile'),

    ('user_003', 'bank_account_onboarding', 'account_creation', 'start', 'web'),
    ('user_003', 'bank_account_onboarding', 'identity_verification', 'step', 'web'),
    ('user_003', 'bank_account_onboarding', 'document_upload', 'step', 'web'),

    ('user_004', 'bank_account_onboarding', 'account_creation', 'start', 'mobile'),
    ('user_004', 'bank_account_onboarding', 'identity_verification', 'step', 'mobile'),
    ('user_004', 'bank_account_onboarding', 'document_upload', 'step', 'mobile'),
    ('user_004', 'bank_account_onboarding', 'approval', 'complete', 'mobile');

---Counting uers in each funnel step
SELECT
    user_id,
    step_name,
    event_type,
    created_at
FROM events
ORDER BY user_id, created_at;

SELECT
    step_name,
    COUNT(DISTINCT user_id) AS users_reached
FROM events
WHERE funnel_name = 'bank_account_onboarding'
GROUP BY step_name
ORDER BY users_reached DESC;



---Inserting some more users
INSERT INTO events (
    user_id,
    funnel_name,
    step_name,
    event_type,
    channel
)
VALUES
    -- User 005 drops immediately after start
    ('user_005', 'bank_account_onboarding', 'account_creation', 'start', 'web'),

    -- User 006 drops after document upload
    ('user_006', 'bank_account_onboarding', 'account_creation', 'start', 'mobile'),
    ('user_006', 'bank_account_onboarding', 'identity_verification', 'step', 'mobile'),
    ('user_006', 'bank_account_onboarding', 'document_upload', 'step', 'mobile'),

    -- User 007 completes onboarding (web)
    ('user_007', 'bank_account_onboarding', 'account_creation', 'start', 'web'),
    ('user_007', 'bank_account_onboarding', 'identity_verification', 'step', 'web'),
    ('user_007', 'bank_account_onboarding', 'document_upload', 'step', 'web'),
    ('user_007', 'bank_account_onboarding', 'approval', 'complete', 'web'),

    -- User 008 drops at identity verification
    ('user_008', 'bank_account_onboarding', 'account_creation', 'start', 'mobile'),
    ('user_008', 'bank_account_onboarding', 'identity_verification', 'step', 'mobile'),
	
	-- User 009 completes onboarding (web)
    ('user_009', 'bank_account_onboarding', 'account_creation', 'start', 'web'),
    ('user_009', 'bank_account_onboarding', 'identity_verification', 'step', 'web'),
    ('user_009', 'bank_account_onboarding', 'document_upload', 'step', 'web'),
    ('user_009', 'bank_account_onboarding', 'approval', 'complete', 'web'),
	
	-- User 010 completes onboarding (web)
    ('user_010', 'bank_account_onboarding', 'account_creation', 'start', 'web'),
    ('user_010', 'bank_account_onboarding', 'identity_verification', 'step', 'web'),
    ('user_010', 'bank_account_onboarding', 'document_upload', 'step', 'web'),
    ('user_0010', 'bank_account_onboarding', 'approval', 'complete', 'web');


	---Check
SELECT COUNT(DISTINCT user_id) AS total_users
FROM events
WHERE funnel_name = 'bank_account_onboarding';



---Count
SELECT
    step_name,
    COUNT(DISTINCT user_id) AS users_reached
FROM events
WHERE funnel_name = 'bank_account_onboarding'
GROUP BY step_name
ORDER BY users_reached DESC;


----Creating step order to see how many users move from tep to the next
WITH step_order AS (
    SELECT
        step_name,
        CASE step_name
            WHEN 'account_creation' THEN 1
            WHEN 'identity_verification' THEN 2
            WHEN 'document_upload' THEN 3
            WHEN 'approval' THEN 4
        END AS step_position
    FROM events
    WHERE funnel_name = 'bank_account_onboarding'
)
SELECT DISTINCT step_name, step_position
FROM step_order
ORDER BY step_position;


----Counting users per step
WITH ordered_steps AS (
    SELECT
        step_name,
        CASE step_name
            WHEN 'account_creation' THEN 1
            WHEN 'identity_verification' THEN 2
            WHEN 'document_upload' THEN 3
            WHEN 'approval' THEN 4
        END AS step_position
    FROM events
    WHERE funnel_name = 'bank_account_onboarding'
),
step_counts AS (
    SELECT
        o.step_name,
        o.step_position,
        COUNT(DISTINCT e.user_id) AS users_reached
    FROM ordered_steps o
    JOIN events e
        ON o.step_name = e.step_name
    WHERE e.funnel_name = 'bank_account_onboarding'
    GROUP BY o.step_name, o.step_position
)
SELECT *
FROM step_counts
ORDER BY step_position;


----conversion rate in %
WITH step_counts AS (
    SELECT
        step_name,
        CASE step_name
            WHEN 'account_creation' THEN 1
            WHEN 'identity_verification' THEN 2
            WHEN 'document_upload' THEN 3
            WHEN 'approval' THEN 4
        END AS step_position,
        COUNT(DISTINCT user_id) AS users_reached
    FROM events
    WHERE funnel_name = 'bank_account_onboarding'
    GROUP BY step_name
),
ordered AS (
    SELECT
        step_name,
        step_position,
        users_reached,
        LAG(users_reached) OVER (ORDER BY step_position) AS previous_step_users
    FROM step_counts
)
SELECT
    step_name,
    users_reached,
    previous_step_users,
    ROUND(
        users_reached::decimal / previous_step_users * 100,
        2
    ) AS conversion_rate_percentage
FROM ordered
ORDER BY step_position;


----- Dropoff %
WITH step_counts AS (
    SELECT
        step_name,
        CASE step_name
            WHEN 'account_creation' THEN 1
            WHEN 'identity_verification' THEN 2
            WHEN 'document_upload' THEN 3
            WHEN 'approval' THEN 4
        END AS step_position,
        COUNT(DISTINCT user_id) AS users_reached
    FROM events
    WHERE funnel_name = 'bank_account_onboarding'
    GROUP BY step_name
),
ordered AS (
    SELECT
        step_name,
        step_position,
        users_reached,
        LEAD(users_reached) OVER (ORDER BY step_position) AS next_step_users
    FROM step_counts
)
SELECT
    step_name,
    users_reached,
    next_step_users,
    (users_reached - next_step_users) AS users_dropped,
    ROUND(
        (users_reached - next_step_users)::decimal / users_reached * 100,
        2
    ) AS drop_off_percentage
FROM ordered
WHERE next_step_users IS NOT NULL
ORDER BY drop_off_percentage DESC;


---Understand dropoffs
WITH step_users AS (
    SELECT DISTINCT user_id, channel
    FROM events
    WHERE funnel_name = 'bank_account_onboarding'
      AND step_name = 'document_upload'
),
next_step_users AS (
    SELECT DISTINCT user_id, channel
    FROM events
    WHERE funnel_name = 'bank_account_onboarding'
      AND step_name = 'approval'
)
SELECT
    s.channel,
    COUNT(DISTINCT s.user_id) AS users_at_document_upload,
    COUNT(DISTINCT n.user_id) AS users_that_reached_approval,
    COUNT(DISTINCT s.user_id) - COUNT(DISTINCT n.user_id) AS users_dropped,
    ROUND(
        (COUNT(DISTINCT s.user_id) - COUNT(DISTINCT n.user_id))::decimal
        / COUNT(DISTINCT s.user_id) * 100,
        2
    ) AS drop_off_percentage
FROM step_users s
LEFT JOIN next_step_users n
    ON s.user_id = n.user_id
GROUP BY s.channel
ORDER BY drop_off_percentage DESC;


---- Time from verification to document upload
WITH step_times AS (
    SELECT
        user_id,
        MIN(created_at) FILTER (WHERE step_name = 'identity_verification') AS identity_time,
        MIN(created_at) FILTER (WHERE step_name = 'document_upload') AS document_time
    FROM events
    WHERE funnel_name = 'bank_account_onboarding'
    GROUP BY user_id
)
SELECT
    COUNT(*) FILTER (WHERE identity_time IS NOT NULL AND document_time IS NOT NULL) AS users_with_both_steps,
    ROUND(AVG(EXTRACT(EPOCH FROM (document_time - identity_time)) / 60), 2) AS avg_minutes_identity_to_document,
    ROUND(MIN(EXTRACT(EPOCH FROM (document_time - identity_time)) / 60), 2) AS min_minutes_identity_to_document,
    ROUND(MAX(EXTRACT(EPOCH FROM (document_time - identity_time)) / 60), 2) AS max_minutes_identity_to_document
FROM step_times
WHERE identity_time IS NOT NULL
  AND document_time IS NOT NULL;



WITH step_times AS (
    SELECT
        user_id,
        MIN(created_at) FILTER (WHERE step_name = 'document_upload') AS document_time,
        MIN(created_at) FILTER (WHERE step_name = 'approval') AS approval_time
    FROM events
    WHERE funnel_name = 'bank_account_onboarding'
    GROUP BY user_id
)
SELECT
    COUNT(*) FILTER (WHERE document_time IS NOT NULL AND approval_time IS NOT NULL) AS users_with_both_steps,
    ROUND(AVG(EXTRACT(EPOCH FROM (approval_time - document_time)) / 60), 2) AS avg_minutes_document_to_approval,
    ROUND(MIN(EXTRACT(EPOCH FROM (approval_time - document_time)) / 60), 2) AS min_minutes_document_to_approval,
    ROUND(MAX(EXTRACT(EPOCH FROM (approval_time - document_time)) / 60), 2) AS max_minutes_document_to_approval
FROM step_times
WHERE document_time IS NOT NULL
  AND approval_time IS NOT NULL;




------ Fix
UPDATE events
SET created_at = created_at + INTERVAL '50 minutes'
WHERE step_name = 'document_upload'
  AND channel = 'mobile';

----- Second Fix
UPDATE events
SET created_at = created_at + INTERVAL '70 minutes'
WHERE step_name = 'approval'
AND channel = 'mobile';


----Complet report
WITH step_counts AS (
    SELECT
        step_name,
        CASE step_name
            WHEN 'account_creation' THEN 1
            WHEN 'identity_verification' THEN 2
            WHEN 'document_upload' THEN 3
            WHEN 'approval' THEN 4
        END AS step_position,
        COUNT(DISTINCT user_id) AS users_reached
    FROM events
    WHERE funnel_name = 'bank_account_onboarding'
    GROUP BY step_name
),
ordered AS (
    SELECT
        step_name,
        step_position,
        users_reached,
        LAG(users_reached) OVER (ORDER BY step_position) AS previous_step_users,
        LEAD(users_reached) OVER (ORDER BY step_position) AS next_step_users
    FROM step_counts
)
SELECT
    step_position,
    step_name,
    users_reached,
    previous_step_users,
    CASE
        WHEN previous_step_users IS NULL THEN NULL
        ELSE ROUND(users_reached::decimal / previous_step_users * 100, 2)
    END AS conversion_rate_percentage,
    next_step_users,
    CASE
        WHEN next_step_users IS NULL THEN NULL
        ELSE (users_reached - next_step_users)
    END AS users_dropped,
    CASE
        WHEN next_step_users IS NULL THEN NULL
        ELSE ROUND((users_reached - next_step_users)::decimal / users_reached * 100, 2)
    END AS drop_off_percentage
FROM ordered
ORDER BY step_position;



----View Once report
CREATE OR REPLACE VIEW funnel_report AS
WITH step_counts AS (
    SELECT
        step_name,
        CASE step_name
            WHEN 'account_creation' THEN 1
            WHEN 'identity_verification' THEN 2
            WHEN 'document_upload' THEN 3
            WHEN 'approval' THEN 4
        END AS step_position,
        COUNT(DISTINCT user_id) AS users_reached
    FROM events
    WHERE funnel_name = 'bank_account_onboarding'
    GROUP BY step_name
),
ordered AS (
    SELECT
        step_name,
        step_position,
        users_reached,
        LAG(users_reached) OVER (ORDER BY step_position) AS previous_step_users,
        LEAD(users_reached) OVER (ORDER BY step_position) AS next_step_users
    FROM step_counts
)
SELECT
    step_position,
    step_name,
    users_reached,
    previous_step_users,
    CASE
        WHEN previous_step_users IS NULL THEN NULL
        ELSE ROUND(users_reached::decimal / previous_step_users * 100, 2)
    END AS conversion_rate_percentage,
    next_step_users,
    CASE
        WHEN next_step_users IS NULL THEN NULL
        ELSE (users_reached - next_step_users)
    END AS users_dropped,
    CASE
        WHEN next_step_users IS NULL THEN NULL
        ELSE ROUND((users_reached - next_step_users)::decimal / users_reached * 100, 2)
    END AS drop_off_percentage
FROM ordered
ORDER BY step_position;

----FastAPI Check
SELECT id, user_id, 
funnel_name, 
step_name, 
event_type, 
channel, created_at
FROM events
ORDER BY id DESC
LIMIT 10;


----Check
SELECT id, user_id, funnel_name, step_name, event_type, channel, created_at
FROM events
ORDER BY id DESC
LIMIT 15;



----Count check
SELECT event_type, COUNT(*) 
FROM events
GROUP BY event_type
ORDER BY COUNT(*) DESC;


-----
CREATE TABLE IF NOT EXISTS funnels (
    id SERIAL PRIMARY KEY,
    funnel_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS funnel_steps (
    id SERIAL PRIMARY KEY,
    funnel_id INT NOT NULL REFERENCES funnels(id) ON DELETE CASCADE,
    step_name VARCHAR(100) NOT NULL,
    step_order INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (funnel_id, step_order),
    UNIQUE (funnel_id, step_name)
);



----Insert funnel step
INSERT INTO funnels (funnel_name, description)
VALUES ('bank_account_onboarding', 'Bank onboarding funnel for new users')
ON CONFLICT (funnel_name) DO NOTHING;


-----
INSERT INTO funnel_steps (funnel_id, step_name, step_order)
SELECT id, 'account_creation', 1 FROM funnels WHERE funnel_name = 'bank_account_onboarding'
ON CONFLICT DO NOTHING;

INSERT INTO funnel_steps (funnel_id, step_name, step_order)
SELECT id, 'identity_verification', 2 FROM funnels WHERE funnel_name = 'bank_account_onboarding'
ON CONFLICT DO NOTHING;

INSERT INTO funnel_steps (funnel_id, step_name, step_order)
SELECT id, 'document_upload', 3 FROM funnels WHERE funnel_name = 'bank_account_onboarding'
ON CONFLICT DO NOTHING;

INSERT INTO funnel_steps (funnel_id, step_name, step_order)
SELECT id, 'approval', 4 FROM funnels WHERE funnel_name = 'bank_account_onboarding'
ON CONFLICT DO NOTHING;


----Confirmation check
SELECT f.id, f.funnel_name, s.step_order, s.step_name
FROM funnels f
JOIN funnel_steps s ON f.id = s.funnel_id
ORDER BY f.id, s.step_order;





