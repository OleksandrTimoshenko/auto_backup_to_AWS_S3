from zipfile import BadZipFile
from datetime import date, datetime, timedelta
import os
import sys
from dotenv import load_dotenv
from plyer import notification
import pyzipper
import boto3

def zip_folder_pyzipper(folder_path, password):
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
        zip_file = pyzipper.AESZipFile(
            backup_name,
            "w",
            compression=pyzipper.ZIP_DEFLATED,
            encryption=pyzipper.WZ_AES,
        )
        zip_file.pwd = password.encode("ASCII")
        for root, folders, files in contents:
            # Include all subfolders, including empty ones.
            for folder_name in folders:
                absolute_path = os.path.join(root, folder_name)
                relative_path = absolute_path.replace(parent_folder + "\\", "")
                print(f"Adding {absolute_path} to archive.")
                zip_file.write(absolute_path, relative_path)
            for file_name in files:
                absolute_path = os.path.join(root, file_name)
                relative_path = absolute_path.replace(parent_folder + "\\", "")
                print(f"Adding {absolute_path} to archive.")
                zip_file.write(absolute_path, relative_path)

        print("Created successfully.")

    except IOError:
        desktop_notification("Backup createtion error")
        sys.exit(1)
    except BadZipFile:
        desktop_notification("Backup createtion error")
        sys.exit(1)
    finally:
        zip_file.close()
    return backup_name


def upload_file_to_s3(bucket_name, filename):
    s3.Bucket(bucket_name).upload_file(Filename=filename, Key=filename)
    print("Uploaded successfully.")


def delete_old_objects(bucket_name, deletion_timestamp, minimal_bucket_amount):
    """Delete ZIP archive from host &&
    remove old backups from S3 bucket"""
    os.system("rm -rf backup*.zip")
    print("Successfully delete file from the host")
    bucket = s3.Bucket(bucket_name)
    count_obj = 0
    for _ in bucket.objects.all():
        count_obj = count_obj + 1
    if count_obj > minimal_bucket_amount:
        for obj in bucket.objects.all():
            if (obj.last_modified).replace(tzinfo=None) < deletion_timestamp:
                s3.Object(bucket_name, obj.key).delete()
                print(f"File Name: {obj.key} ---- Date: {obj.last_modified}")


def desktop_notification(message):
    notification.notify(title="Python backup", message=message, timeout=100)


if __name__ == "__main__":
    load_dotenv()
    backup_folder_name = os.getenv("BACKUP_FOLDER_NAME")
    archive_password = os.getenv("ARCHIVE_PASSWORD")
    AWS_bucket_name = os.getenv("AWS_BUCKET_NAME")
    min_bucket_amount = int(os.getenv("MIN_BUCKET_AMOUNT"))
    delete_buckets_older_than = int(os.getenv("DELETE_BUCKETS_OLDER_THAN"))
    s3 = boto3.resource(
        service_name="s3",
        region_name=os.getenv("AWS_REGION_NAME"),
        aws_access_key_id=os.getenv("AWS_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET"),
    )

    full_path_to_the_archive = zip_folder_pyzipper(
        backup_folder_name, archive_password)
    upload_file_to_s3(AWS_bucket_name, full_path_to_the_archive)
    deletion_time = datetime.now() - timedelta(days=delete_buckets_older_than)
    delete_old_objects(AWS_bucket_name, deletion_time, min_bucket_amount)
    desktop_notification("Backup created successfully")
