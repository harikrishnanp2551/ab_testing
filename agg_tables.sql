DROP TABLE IF EXISTS agg_listings_by_neighbourhood;
CREATE TABLE agg_listings_by_neighbourhood AS
SELECT 
    neighbourhood,
    COUNT(*) AS total_listings,
    AVG(price) AS avg_price,
    AVG("reviews per month") AS avg_reviews
FROM airbnb_kaggle
GROUP BY neighbourhood;

SELECT * FROM agg_listings_by_neighbourhood;

DROP TABLE IF EXISTS agg_listings_by_roomtype;
CREATE TABLE agg_listings_by_roomtype AS
SELECT 
    "room type",
    COUNT(*) AS total_listings,
    AVG(price) AS avg_price,
    AVG("minimum nights") AS avg_minimum_nights
FROM airbnb_kaggle
GROUP BY "room type";
SELECT * FROM agg_listings_by_roomtype;

DROP TABLE IF EXISTS agg_host_activity;
CREATE TABLE agg_host_activity AS
SELECT 
    "host id",
    "host name",
    COUNT(*) AS total_listings,
    AVG(price) AS avg_price,
    SUM("number of reviews") AS total_reviews
FROM airbnb_kaggle
GROUP BY "host id", "host name";
SELECT * FROM agg_host_activity;

DROP TABLE IF EXISTS agg_reviews;
CREATE TABLE agg_reviews AS
SELECT 
    neighbourhood,
    SUM("number of reviews") AS total_reviews,
    AVG("reviews per month") AS avg_reviews_per_month
FROM airbnb_kaggle
GROUP BY neighbourhood;
SELECT * FROM agg_reviews;

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
SELECT * FROM agg_price_distribution;