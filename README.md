# PTS

PTS automation scripts using selenium.

# Install dependencies:

pip install -r requierments.txt

edit the conf.txt so that the first line is your username and the second line is your password

# Usage
run submit.py to submit a time

run check.py to analyze a "work period" (15nth of the month till the 15nth of the next month) based on you entries in PTS website and find and submit missing entries.

pts.py will be the integration of above scripts.

chrome driver is also included, feel free to replace the driver.

to-do:
- merge two scripts into one
- change the conf format to json
- set the base URL in conf.txt


