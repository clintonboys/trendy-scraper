# Trendy scraper

This script, written in Python, scrapes Google trends for a certain keyword over a long timescale. Since Google trends only outputs weekly data for periods longer than a few months, it also pulls daily data for small periods throughout the full period and then stitches them together, rescaling for consistency. 

This is a new version of the scraper, developed in February 2017 after changes to the API behind the scenes meant the initial version (still available as gt_scraper.py) was deprecated. 

## Usage

Run as

```
python gt_scraper_v2.py 2016-01-01 2017-02-18 donald trump
```

## Dependencies

- Python 2.7
- pandas

## Note

Please do not use for any purposes that will violate Google's [terms of use](https://www.google.com/policies/terms/). 
