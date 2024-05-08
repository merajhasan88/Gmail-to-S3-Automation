import imaplib
import email
import os
import boto3
import shutil

# Gmail IMAP server address and port
imap_server = 'imap.gmail.com'
imap_port = 993

# Your Gmail credentials
email_user = 'youremail@gmail.com'
email_pass = 'yourapp-password'

# Email address of the sender you want to fetch emails from
sender_email = 'sender@gmail.com'

# Desired subject of the email
desired_subject = 'Desired Email Subject'

try:
    # Connect to Gmail IMAP server
    mail = imaplib.IMAP4_SSL(imap_server, imap_port)

    # Login to your account
    mail.login(email_user, email_pass)

    # Select the mailbox (inbox)
    mail.select('inbox')

    # Search for emails from the specified sender
    result, data = mail.search(None, f'(FROM "{sender_email}")')

    # Get the list of email IDs
    email_ids = data[0].split()

    # Fetch the most recent email (assumed to be the last one in the list)
    latest_email_id = email_ids[-1]

    # Fetch the email message by ID
    result, email_data = mail.fetch(latest_email_id, '(RFC822)')
    raw_email = email_data[0][1]

    # Parse the raw email data
    msg = email.message_from_bytes(raw_email)

    # Check if the subject matches the desired subject
    if msg['Subject'] == desired_subject:
        # Print the sender's name and email address
        sender_name, sender_address = email.utils.parseaddr(msg['From'])
        print("Sender Name:", sender_name)
        print("Sender Email:", sender_address)

        # Iterate through each part of the email (including attachments)
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue

            # Download the attachment
            filename = part.get_filename()
            if filename:
                filepath = os.path.join('calldataset_files', filename)
                with open(filepath, 'wb') as f:
                    f.write(part.get_payload(decode=True))
                print("Attachment downloaded:", filename)

        print("Email and attachments downloaded successfully!")
    else:
        print("The subject of the most recent email does not match the desired subject.")

except Exception as e:
    print("Error:", e)



def get_latest_unique_data(folder_path):
    files = os.listdir(folder_path)
    if not files:
        return None

    # Filter out non-CSV files
    csv_files = [os.path.join(folder_path, f) for f in files if f.endswith('.csv')]
    if not csv_files:
        return None
    df_old=pd.read_csv(min(csv_files, key=lambda f: os.path.getmtime(f))) # Previous file
    df_new=pd.read_csv(max(csv_files, key=lambda f: os.path.getmtime(f))) # New file with some new data
    s = set(df_new['ID']) # Assuming every row has a unique ID
    dict_difference=(s ^ set(df_old['ID']))
    final_df=df_new[df_new['ID'].isin(dict_difference)]
    final_df
    from unidecode import unidecode
    final_df[['Contact Name','Subject']]=final_df[['Contact Name','Subject']].apply(lambda x : x.replace("\'"," ")) # Replace apostrophe
    final_df[['Contact Name','Subject']]=final_df[['Contact Name','Subject']].apply(lambda x : x.replace(","," ")) # Replace comma
    final_df['Contact Name']=final_df['Contact Name'].apply(lambda x : unidecode(x)) # Replace european alphabets
    # Now delete all previous files
    for root, dirs, files in os.walk('your-folder'):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    print('Deleted previous files')
    from datetime import datetime
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y %H-%M-%S")
    file_name='your-folder\DeltaFile'+dt_string+'.csv' # When a new file comes, this will be the old file
    print('Created ',file_name)
    final_df.to_csv(file_name,index=False)
    return file_name

# Example usage:
folder_path = 'your-folder'  # Specify the folder path
unique_csv_path=get_latest_unique_data(folder_path)


if unique_csv_path:
    print("File to be uploaded:", unique_csv_path)


def list_objects_in_folder(bucket_name, folder_name):
    
    # Recursive function to list and delete objects
    def list_and_delete_objects(prefix):
        response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix
        )
        for obj in response.get('Contents', []):
            print("Deleting:", obj['Key'])
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
        for common_prefix in response.get('CommonPrefixes', []):
            list_and_delete_objects(common_prefix['Prefix'])

    # Start listing and deleting objects
    list_and_delete_objects(folder_name)


# Example usage:
# Create an S3 client
s3 = boto3.client('s3', aws_access_key_id='your-access-key', aws_secret_access_key='your-secret-key',region_name='your-region')
bucket_name='your-bucket'
folder_name='your-folder/'  # Don't forget to include the trailing slash
list_objects_in_folder(bucket_name, folder_name)
print('finished')



key = os.path.join(folder_name, unique_csv_path)  # Combine folder name and filename as the key
s3.upload_file(unique_csv_path, bucket_name, key)
print ('File uploaded Successfully')


