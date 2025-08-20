import os
from google.cloud import firestore

def get_db():
    # On GCP, ADC (Application Default Credentials) is used automatically.
    # Locally, either:
    # 1) `gcloud auth application-default login`, or
    # 2) set GOOGLE_APPLICATION_CREDENTIALS to your service-account JSON.
    return firestore.Client()
