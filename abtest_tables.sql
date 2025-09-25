-- Add AB group if not present
ALTER TABLE airbnb_kaggle
ADD COLUMN IF NOT EXISTS ab_group CHAR(1);

UPDATE airbnb_kaggle
SET ab_group = CASE WHEN RANDOM() < 0.5 THEN 'A' ELSE 'B' END
WHERE ab_group IS NULL;

-- Summary by AB group (with immediate booking feature)
DROP TABLE IF EXISTS ab_group_summary;
CREATE TABLE ab_group_summary AS
SELECT
    ab_group,
    COUNT(*)::int AS n_listings,
    AVG(price)::numeric(10,2) AS avg_price,
    AVG(number_of_reviews)::numeric(10,2) AS avg_reviews,
    AVG(CASE WHEN review_rate_number IS NOT NULL THEN 1 ELSE 0 END)::numeric(5,4) AS conv_rate,
    AVG(CASE WHEN instant_bookable = 't' THEN 1 ELSE 0 END)::numeric(5,4) AS immediate_booking_rate
FROM airbnb_kaggle
GROUP BY ab_group;

-- Lift table
DROP TABLE IF EXISTS ab_group_lift;
CREATE TABLE ab_group_lift AS
SELECT
    'avg_price' AS metric,
    (MAX(CASE WHEN ab_group='B' THEN avg_price END) -
     MAX(CASE WHEN ab_group='A' THEN avg_price END)) /
     MAX(CASE WHEN ab_group='A' THEN avg_price END) AS lift
FROM ab_group_summary
UNION ALL
SELECT
    'avg_reviews',
    (MAX(CASE WHEN ab_group='B' THEN avg_reviews END) -
     MAX(CASE WHEN ab_group='A' THEN avg_reviews END)) /
     MAX(CASE WHEN ab_group='A' THEN avg_reviews END)
FROM ab_group_summary
UNION ALL
SELECT
    'conv_rate',
    (MAX(CASE WHEN ab_group='B' THEN conv_rate END) -
     MAX(CASE WHEN ab_group='A' THEN conv_rate END)) /
     MAX(CASE WHEN ab_group='A' THEN conv_rate END)
FROM ab_group_summary
UNION ALL
SELECT
    'immediate_booking_rate',
    (MAX(CASE WHEN ab_group='B' THEN immediate_booking_rate END) -
     MAX(CASE WHEN ab_group='A' THEN immediate_booking_rate END)) /
     MAX(CASE WHEN ab_group='A' THEN immediate_booking_rate END)
FROM ab_group_summary;

-- City-level summary
DROP TABLE IF EXISTS ab_neighborhood_summary;
CREATE TABLE ab_neighborhood_summary AS
SELECT
    neighbourhood,
    ab_group,
    COUNT(*)::int AS n_listings,
    AVG(price)::numeric(10,2) AS avg_price
FROM airbnb_kaggle
GROUP BY neighbourhood, ab_group;

SELECT * FROM ab_neighborhood_summary;
SELECT * FROM ab_group_summary;
SELECT * FROM ab_group_lift;
