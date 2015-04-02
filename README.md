# Dump Scraper

Believe it or not, Internet is full of passwords (plain and hashed ones):
when a leak occurs, usually it's posted to [PasteBin](http://pastebin.com/).  
The pace of these dumps is so high that it's not humanly possible to collect them all, so we have to rely on a bot, scraping PasteBin site for interesting files.  

[Dump Monitor](https://twitter.com/dumpmon) will exactly do this: every time some leaked information are posted on PasteBin, he will tweet the link. 

## So why this repository?
Sadly Dump Monitor is not very efficient: inside its tweets you will find a lot of "false positives" (debug data, log files, Antivirus scan results) or stuff we're not interested into (RSA private keys, API keys, list of email addresses).

Moreover, once you have the raw data you need to extract such information and remove all the garbage.

That's the reason why Dump Scraper was born: inside this repository you will find several scripts to fetch the latest tweets from Dump Monitor, analyze them (discarding useless files) and extract the hashes or the passwords.  

If you are using an Amazon EC2 spot instance to crack hashes, you will find some useful scripts for handling the termination notice.  
Finally, there are a couple of scripts for dealing with plain passwords and create your own wordlist.

## Requirements
 There are no requirements, just run the executable file from CLI
