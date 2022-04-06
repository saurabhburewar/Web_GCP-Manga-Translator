import base64
import json
import os

from google.cloud import pubsub_v1
from google.cloud import storage
from google.cloud import translate_v2
from google.cloud import vision


vis_client = vision.ImageAnnotatorClient()
trans_client = translate_v2.Client()
publisher = pubsub_v1.PublisherClient()
st_client = storage.Client()

project = os.environ["GCP_PROJECT"]


def validate_mes(message, param):
    var = message.get(param)
    if not var:
        raise ValueError(
            "{} is not provided. Make sure you have property {} in the request".format(param, param))

    return var


def process_img(file, context):
    bucket = validate_mes(file, "bucket")
    name = validate_mes(file, "name")

    detect(bucket, name)

    print("File {} processed".format(file["name"]))


def detect(bucket, filename):

    futures = []

    img = vision.Image(source=vision.ImageSource(
        gcs_image_uri=f"gs://{bucket}/{filename}"))
    text_res = vis_client.text_detection(image=img)
    annot = text_res.text_annotations
    if len(annot) > 0:
        text = annot[0].description
    else:
        text = ""
    print("Extracted text {} from image {} chars.".format(text, len(text)))

    det_lang_res = trans_client.detect_language(text)
    src_lang = det_lang_res["language"]
    print("Detected language {}".format(src_lang))

    to_langs = os.environ["TO_LANG"].split(",")
    for target_lang in to_langs:
        topic = os.environ["TRANSLATE_TOPIC"]
        if src_lang == target_lang or src_lang == "und":
            topic = os.environ["RESULT_TOPIC"]
        message = {
            "text": text,
            "filename": filename,
            "lang": target_lang,
            "src_lang": src_lang,
        }
        message_data = json.dumps(message).encode("utf-8")
        topicpath = publisher.topic_path(project, topic)
        future = publisher.publish(topicpath, data=message_data)
        futures.append(future)

    for future in futures:
        future.result()


def translate(event, context):
    if event.get("data"):
        message_data = base64.b64decode(event["data"]).decode("utf-8")
        message = json.loads(message_data)
    else:
        raise ValueError("Data sector is missing in Pub/Sub message")

    text = validate_mes(message, "text")
    filename = validate_mes(message, "filename")
    target_lang = validate_mes(message, "lang")
    src_lang = validate_mes(message, "src_lang")

    print("Translating text to {}".format(target_lang))
    trans_text = trans_client.translate(
        text, target_language=target_lang, source_language=src_lang)
    topic = os.environ["RESULT_TOPIC"]
    message = {
        "text": trans_text["translatedText"],
        "filename": filename,
        "lang": target_lang,
    }
    message_data = json.dumps(message).encode("utf-8")
    topicpath = publisher.topic_path(project, topic)
    future = publisher.publish(topicpath, data=message_data)
    future.result()


def save(event, context):
    if event.get("data"):
        message_data = base64.b64decode(event["data"]).decode("utf-8")
        message = json.loads(message_data)
    else:
        raise ValueError("Data sector is missing in Pub/Sub message")

    text = validate_mes(message, "text")
    filename = validate_mes(message, "filename")
    lang = validate_mes(message, "lang")

    print("Received request to save {}".format(filename))

    bucket_name = os.environ["RESULT_BUCKET"]
    result_file = "{}_{}.txt".format(filename, lang)
    bucket = st_client.get_bucket(bucket_name)
    blob = bucket.blob(result_file)

    print("Saved to {} in {}".format(result_file, bucket_name))
    blob.upload_from_string(text)
    print("File saved")
