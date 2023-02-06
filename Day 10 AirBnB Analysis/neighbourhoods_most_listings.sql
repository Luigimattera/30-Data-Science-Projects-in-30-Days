SELECT neighbourhood, count(*) as total_listings
FROM listings
GROUP BY neighbourhood
ORDER BY total_listings DESC;