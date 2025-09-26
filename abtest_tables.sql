-- abtest_tables.sql
-- Clean feature engineering for analysis

ALTER TABLE airbnb_kaggle
ADD COLUMN IF NOT EXISTS instant_bookable_flag BOOLEAN,
ADD COLUMN IF NOT EXISTS room_type_flag TEXT,
ADD COLUMN IF NOT EXISTS cancellation_flag TEXT,
ADD COLUMN IF NOT EXISTS price_bucket TEXT,
ADD COLUMN IF NOT EXISTS service_fee_bucket TEXT,
ADD COLUMN IF NOT EXISTS neighbourhood_group_flag TEXT;

-- Price median (for service_fee split) — adjust column name if needed
WITH med AS (
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY service_fee) AS median_fee
    FROM airbnb_kaggle
)
UPDATE airbnb_kaggle
SET service_fee_bucket = CASE
    WHEN service_fee IS NULL THEN 'unknown'
    WHEN service_fee < (SELECT median_fee FROM med) THEN 'below_median'
    ELSE 'above_median'
END;

-- Populate feature categories
UPDATE airbnb_kaggle
SET instant_bookable_flag = (instant_bookable = 't'),
    room_type_flag = CASE
        WHEN room_type ILIKE '%Entire%' THEN 'entire_home'
        WHEN room_type ILIKE '%Private%' THEN 'private_room'
        ELSE 'other'
    END,
    cancellation_flag = CASE
        WHEN cancellation_policy ILIKE '%flex%' THEN 'flexible'
        WHEN cancellation_policy ILIKE '%strict%' THEN 'strict'
        ELSE 'other'
    END,
    price_bucket = CASE
        WHEN price IS NULL THEN 'unknown'
        WHEN price < 100 THEN '<100'
        ELSE '>=100'
    END,
    neighbourhood_group_flag = CASE
        WHEN neighbourhood_group ILIKE 'Brooklyn' THEN 'Brooklyn'
        WHEN neighbourhood_group ILIKE 'Manhattan' THEN 'Manhattan'
        ELSE 'Other'
    END;
