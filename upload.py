import firebase_admin
import google.cloud
from firebase_admin import credentials, firestore

cred = credentials.Certificate("gretest-475ba-firebase-adminsdk-m9sgv-243f75e6f1.json")
# cred = credentials.Certificate("gretestchina-2d345-firebase-adminsdk-tfjrk-dc57294d4d.json")
app = firebase_admin.initialize_app(cred)

store = firestore.client()

def batch_data(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        end = min(ndx + n, l)
        yield iterable[ndx:end]

def save(data):
    for batched_data in batch_data(data, 499):
        batch = store.batch()
        for data_item in batched_data:
            doc_ref = store.collection('problems').document()
            batch.set(doc_ref, data_item)
        batch.commit()

    print('Done')

def save_sections(sections):
    for batched_data in batch_data(sections, 499):
        batch = store.batch()
        for data_item in batched_data:
            doc_ref = store.collection('sections').document()
            batch.set(doc_ref, data_item)
        batch.commit()

    print('Done')

def save_alert(data):
    for batched_data in batch_data(data, 499):
        batch = store.batch()
        for data_item in batched_data:
            doc_ref = store.collection('keyKingWords').document()
            batch.set(doc_ref, data_item)
        batch.commit()


