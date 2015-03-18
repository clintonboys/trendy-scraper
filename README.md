## Trendy scraper

This script, written in Python, scrapes Google trends for a certain keyword over a long timescale. Since Google trends only outputs weekly data for periods longer than a few months, it also downloads daily data for small periods throughout the full period and then stitches them together, rescaling for consistency. 