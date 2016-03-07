## 1.0.0
- Avoid errors when calculating training data score
- Added support for MySQL < 4.1 hashes
- Added support for Apache MD5 hashes
- Added support for standalone passwords in foreign language (Spanish)
- Added support for MD5 salted hashes
- Added warning when a new release is found
- Added support for dump files containing plain passwords
- Added "clean" parameter for the classify job, so you can automatically clean previous results
- Moved the features file up one level for better reading
- Added shortcut to open the current file while training the system
- Added support for SQLmap cracked passwords
- Added support for keylogger files
- Removed the need to press "Enter" while screening for training files
- Added "review" command to quickly review organized files
- Added support for "greedy": a tradoff between data retrieved and amount of false positives
- Added log file for extensive logging

## 0.2.0
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
