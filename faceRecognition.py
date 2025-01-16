# written with a help of google gemini
# made by sugarfree90 https://github.com/sugarfree90


import requests
import json
import argparse
# pip install psycopg2-binary < -must be a binary version!!!
import psycopg2
from psycopg2.extensions import adapt, register_adapter, AsIs
import numpy as np
import time


# You need to add user to the database, or use existing one
db_params = {
    "dbname": "immich",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1"
}

# adapting function to convert python list to vector
def adapt_vector(vector):
    return AsIs("'" + str(vector) + "'")

# register adapter
register_adapter(list, adapt_vector)
register_adapter(np.ndarray, adapt_vector)

# sends picture to immich api to detect faces on image
def detect_faces(image_file):


  url = "http://localhost:3003/predict"
  headers = {'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW'}

  dane = {
      "entries": json.dumps({
          "facial-recognition": {
              "recognition": {
                  "modelName": "buffalo_l",
                  "options": {
                      "minScore": 0.7
                  }
              },
              "detection": {
                  "modelName": "buffalo_l"
              }
          }
      })
  }

  files = {'image': open(image_file, 'rb')}

  try:
    timer = time.time()
    response = requests.post(url, data=dane, files=files)
    response.raise_for_status()  # Raise an exception for bad status codes
    persons = []
    print("server response:")
    print(json.dumps(response.json()["facial-recognition"], indent=4))
    print("ai processing time: "+str(time.time() - timer))
    timer = time.time()
    if len(response.json()["facial-recognition"]) > 0:
      for face in response.json()["facial-recognition"]:
        person = get_person_name_by_face_vector(db_params, face["embedding"])
        if person != None:
          if person != '':
            persons.append(person)
    print("db processing time: "+str(time.time() - timer))
    print(persons)

  except requests.exceptions.RequestException as e:
    print(f"error sending request: {e}")


# identify person based on face vector
def get_person_name_by_face_vector(db_params, face_vector):

    try:
        # db connect
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        # 1. find UUID of a face (faceId) in table face_search using vector comparison
        cur.execute("""
            SELECT "faceId"
            FROM face_search
            ORDER BY embedding <=> %s
            LIMIT 1
        """, (face_vector,))

        result = cur.fetchone()

        if result is None:
            print("no matching faces.")
            return None

        face_uuid = result[0]

        # 2. find name (name) in table person using faceUuid
        cur.execute("""
            SELECT name
            FROM person
            WHERE "id" = (SELECT "personId" FROM asset_faces WHERE "id" = %s)
        """, (face_uuid,))

        result = cur.fetchone()

        if result is None:
            print(f"faceUuid not found: {face_uuid}")
            return None

        name = result[0]
        return name

    except (Exception, psycopg2.Error) as error:
        print("db error:", error)
        return None

    finally:
        if conn:
            cur.close()
            conn.close()


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="immich face detection")
  parser.add_argument("image_file", help="path to jpeg file")
  args = parser.parse_args()

  detect_faces(args.image_file)