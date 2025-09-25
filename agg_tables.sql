DROP TABLE IF EXISTS agg_listings_by_neighbourhood;
CREATE TABLE agg_listings_by_neighbourhood AS
SELECT
    neighbourhood,
    COUNT(*) AS total_listings,
    AVG(price) AS avg_price,
    AVG(reviews_per_month) AS avg_reviews
FROM airbnb_kaggle
GROUP BY neighbourhood;

DROP TABLE IF EXISTS agg_listings_by_roomtype;
CREATE TABLE agg_listings_by_roomtype AS
SELECT
    room_type,
    COUNT(*) AS total_listings,
    AVG(price) AS avg_price,
    AVG(minimum_nights) AS avg_minimum_nights
FROM airbnb_kaggle
GROUP BY room_type;

DROP TABLE IF EXISTS agg_host_activity;
CREATE TABLE agg_host_activity AS
SELECT
    host_id,
    host_name,
    COUNT(*) AS total_listings,
    AVG(price) AS avg_price,
    SUM(number_of_reviews) AS total_reviews
FROM airbnb_kaggle
GROUP BY host_id, host_name;

DROP TABLE IF EXISTS agg_reviews;
CREATE TABLE agg_reviews AS
SELECT
    neighbourhood,
    SUM(number_of_reviews) AS total_reviews,
    AVG(reviews_per_month) AS avg_reviews_per_month
FROM airbnb_kaggle
GROUP BY neighbourhood;

DROP TABLE IF EXISTS agg_price_distribution;
CREATE TABLE agg_price_distribution AS
SELECT
    CASE
        WHEN price < 50 THEN '<50'
        WHEN price BETWEEN 50 AND 100 THEN '50-100'
        WHEN price BETWEEN 101 AND 200 THEN '101-200'
        WHEN price BETWEEN 201 AND 500 THEN '201-500'
        ELSE '500+'
    END AS price_range,
    COUNT(*) AS listings
FROM airbnb_kaggle
GROUP BY price_range;
