### immichFaceRecognitionScript
#Script to search for people on pictures using immich database

#Usage:
python3 faceRecognition.py image.jpg

Returns names of people found on pictures using immich image recognition and it's database

##Tips about launching this script:

#psycopg2 must be installed in binary version:
pip install psycopg2-binary


#docker-compose.yml - you must add ports to machine learning api and database
for machine learning:
in section "immich-machine-learning" add 
    ports:
      - "3003:3003"

in section "database" add
    ports:
      - "5432:5432"
#I have added that after .env file section

and resart docker or use this:
docker compose up -d

#Accessing the database (to add users etc.)
docker exec -it immich_postgres psql --dbname=immich --username=postgres

#User postgres should be able to do everything
But i have added a new one to be able do login with password

All of the work was done with the help of Google Gemini

###Use it how you like it :)
