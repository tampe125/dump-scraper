## 0.3.0 [Unreleased]
- Avoid errors when calculating training data score
- Added support for MySQL < 4.1 hashes
- Added support for Apache MD5 hashes
- Added support for standalone passwords in foreign language (Spanish)
- Added support for MD5 salted hashes
- Added warning when a new release is found
- Added support for dump files containing plain passwords
- Added "clean" parameter for the classify job, so you can automatically clean previous results

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