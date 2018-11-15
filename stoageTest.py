from google.cloud import storage
from google.oauth2 import service_account

sc = storage.Client()
bucket = sc.get_bucket('strawberryfinder.appspot.com')
blob2 = bucket.blob('images/img1.png')
blob2.upload_from_filename(filename='./1.png')