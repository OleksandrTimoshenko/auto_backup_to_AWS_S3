import pyzipper, os, sys, boto3
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
from plyer import notification

def zip_folderPyzipper(folder_path, password):
    """Zip the contents of an entire folder (with that folder included
    in the archive). Empty subfolders will be included in the archive
    as well.
    """
    parent_folder = os.path.dirname(folder_path)
    # Retrieve the paths of the folder contents.
    contents = os.walk(folder_path)
    today = date.today()
    backup_name = "backup" + today.strftime("%b-%d-%Y") + ".zip"
    try:
        zip_file = pyzipper.AESZipFile(backup_name,'w',compression=pyzipper.ZIP_DEFLATED,encryption=pyzipper.WZ_AES)
        zip_file.pwd=password.encode('ASCII')
        for root, folders, files in contents:
            # Include all subfolders, including empty ones.
            for folder_name in folders:
                absolute_path = os.path.join(root, folder_name)
                relative_path = absolute_path.replace(parent_folder + '\\',
                                                      '')
                print ("Adding '%s' to archive." % absolute_path)
                zip_file.write(absolute_path, relative_path)
            for file_name in files:
                absolute_path = os.path.join(root, file_name)
                relative_path = absolute_path.replace(parent_folder + '\\',
                                                      '')
                print ("Adding '%s' to archive." % absolute_path)
                zip_file.write(absolute_path, relative_path)

        print ("Created successfully.")

    except IOError as message:
        decktop_notification("Backup createtion error")
        sys.exit(1)
    except OSError as message:
        decktop_notification("Backup createtion error")
        sys.exit(1)
    except zipfile.BadZipfile as message:
        decktop_notification("Backup createtion error")
        sys.exit(1)
    finally:
        zip_file.close()
        return backup_name

def upload_file_to_AWS_s3(AWS_busket_name, filename):
    s3.Bucket(AWS_busket_name).upload_file(Filename=filename, Key=filename)
    print("Uploaded successfully.")

def delete_old_objects(AWS_busket_name, deletion_time, min_bucket_amount):
    os.system("rm -rf backup*.zip")
    print("Successfully delete file from the host")
    bucket = s3.Bucket(AWS_busket_name)
    count_obj = 0
    for i in bucket.objects.all():
        count_obj = count_obj + 1
    if count_obj > min_bucket_amount:
        for obj in bucket.objects.all():
            if (obj.last_modified).replace(tzinfo = None) < deletion_time:
                s3.Object(AWS_busket_name, obj.key).delete()
                print('File Name: %s ---- Date: %s' % (obj.key,obj.last_modified))

def decktop_notification(message):
    notification.notify(
        title = 'Python backup',
        message = message,
        timeout = 100
    )

if __name__ == '__main__':
    load_dotenv()
    backup_folder_name = os.getenv("BACKUP_FOLDER_NAME")
    archive_password = os.getenv("ARCHIVE_PASSWORD")
    AWS_busket_name = os.getenv("AWS_BUSKET_NAME")
    min_bucket_amount = int(os.getenv("MIN_BUCKET_AMOUNT"))
    delete_buckets_older_than = int(os.getenv("DELETE_BUCKETS_OLDER_THAN"))
    s3 = boto3.resource(
        service_name='s3',
        region_name='eu-central-1',
        aws_access_key_id=os.getenv("AWS_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET")
    )
    
    full_path_to_the_archive = zip_folderPyzipper(backup_folder_name, archive_password)
    upload_file_to_AWS_s3(AWS_busket_name, full_path_to_the_archive)
    deletion_time = datetime.now() - timedelta(days=delete_buckets_older_than)
    delete_old_objects(AWS_busket_name, deletion_time, min_bucket_amount)
    decktop_notification("Backup created successfully")