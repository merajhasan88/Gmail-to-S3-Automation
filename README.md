# Gmail-to-S3-Automation
Automatically forward specific Gmail attachments to S3 bucket

1. `simply.py` finds latest attachment from a specific sender with specific email subject and uploads it to s3 bucket. 
2. `find-new-data-between-two-attachments.py` compares recent with previous attachment and extracts the new data and uploads only that to s3.

# Steps:
1. Enable IMAP on Gmail
2. Find your app password (not gmail password)
3. Put your AWS access key and secret key here (or use a credentials file)
4. Automate it using Task Scheduler or cronjob.
