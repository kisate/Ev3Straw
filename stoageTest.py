from google.cloud import storage
from google.oauth2 import service_account

#Don`t forget to do that:
# export GOOGLE_APPLICATION_CREDENTIALS="/home/forester/Documents/klubnikor/ev3/Ev3Straw/StrawberryFinder-afeca06021c9.json"`
#replace with your destination to new json key

sc = storage.Client()
bucket = sc.get_bucket('strawberryfinder.appspot.com')
blob2 = bucket.blob('images/img1.png')
blob2.upload_from_filename(filename='./1.png')