#!/bin/sh

# Define email parameters
TO="jeneen348@gmail.com"
SUBJECT="Test Email with Attachment"
BODY="This is a test email with an attachment."
#ATTACHMENT="/path/to/attachment.txt"

# Send the email with attachment
#echo "$BODY" | mutt -s "$SUBJECT" "$TO" -a "$ATTACHMENT" --
echo "$BODY" | mutt -s "$SUBJECT" "$TO" --
