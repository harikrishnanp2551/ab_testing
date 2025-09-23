SELECT * FROM airbnb_kaggle LIMIT 10;

SELECT COUNT (*) FROM airbnb_kaggle;

DROP TABLE IF EXISTS data_quality_metrics;

CREATE TABLE data_quality_metrics (
    step TEXT,
    metric_name TEXT,
    metric_value NUMERIC,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row count before cleaning
INSERT INTO data_quality_metrics (step, metric_name, metric_value)
SELECT 'initial', 'total_rows', COUNT(*) FROM airbnb_kaggle;


SELECT id, COUNT(*)
FROM airbnb_kaggle
GROUP By id
HAVING COUNT(*)>1;

-- Duplicates count
INSERT INTO data_quality_metrics (step, metric_name, metric_value)
SELECT 'check', 'duplicates_found', COUNT(*) 
FROM (
  SELECT id, COUNT(*) c FROM airbnb_kaggle GROUP BY id HAVING COUNT(*) > 1
) t;

--Remove duplicates (keeping first occurrence)
DELETE FROM airbnb_kaggle a
USING (
  SELECT id, MIN(ctid) as min_ctid
  FROM airbnb_kaggle
  GROUP BY id
) b
WHERE a.id = b.id AND a.ctid <> b.min_ctid;


-- Null name count
INSERT INTO data_quality_metrics (step, metric_name, metric_value)
SELECT 'check', 'null_names', COUNT(*) FROM airbnb_kaggle WHERE "NAME" IS NULL;

-- Remove rows with null names
DELETE FROM airbnb_kaggle WHERE "NAME" IS NULL;


-- Host identity nulls
INSERT INTO data_quality_metrics (step, metric_name, metric_value)
SELECT 'check', 'null_host_identity_verified', COUNT(*) 
FROM airbnb_kaggle WHERE host_identity_verified IS NULL;

-- Price outliers (> 99th percentile)
WITH price_limit AS (
  SELECT PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY price) AS p99
  FROM airbnb_kaggle
)
DELETE FROM airbnb_kaggle
WHERE price > (SELECT p99 FROM price_limit);

-- Track nulls in major columns
INSERT INTO data_quality_metrics (step, metric_name, metric_value)
SELECT 'check', 'null_price', COUNT(*) FROM airbnb_kaggle WHERE price IS NULL;

INSERT INTO data_quality_metrics (step, metric_name, metric_value)
SELECT 'check', 'null_reviews', COUNT(*) FROM airbnb_kaggle WHERE "number of reviews" IS NULL;

-- Row count after cleaning
INSERT INTO data_quality_metrics (step, metric_name, metric_value)
SELECT 'final', 'total_rows_after_cleaning', COUNT(*) FROM airbnb_kaggle;

-- % retained
INSERT INTO data_quality_metrics (step, metric_name, metric_value)
SELECT 'summary', 'pct_retained',
       (COUNT(*) * 100.0) / (SELECT metric_value FROM data_quality_metrics WHERE metric_name='total_rows')
FROM airbnb_kaggle;

select * from data_quality_metrics;

