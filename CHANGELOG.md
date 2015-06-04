## 0.3.0 [Unreleased]
- Added support for MySQL < 4.1 hashes
- Added support for standalone passwords in foreign language (Spanish)

## 0.2.0 [Unreleased]
### Added
- Skip all numbers password
- Added script to scrape old tweets
- Added more checks on input, print an useful error instead of the whole call stack
- Treat hash:plain has plain files, not hash ones
- Added colors to the output
- More friendly view while selecting training data

### Changed
- Fixed Twitter scraping when results are paginated (more results than the configured limit)
- Skip empty lines while calculating occurrence ratio

## 0.1.0
First release