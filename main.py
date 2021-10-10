import requests, json
import base64
from columnar import columnar
from requests.api import get


authentication_url = "https://accounts.spotify.com/api/token"
authentication_header = {}
authentication_data = {}


def getAccessToken(clientID, clientSecret):
    # Encode Client ID & Client Secret
    message = clientID + ":" + clientSecret
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')

    # Create URL and get response status
    authentication_header["Authorization"] = "Basic " + base64_message
    authentication_data["grant_type"] = "client_credentials"
    url_response = requests.post(authentication_url, headers=authentication_header, data=authentication_data)

    # Return useful data (access token or None)
    if url_response.status_code != 200:
        return None
    else:
        # Get Access Token
        url_data = url_response.json()
        access_token = url_data["access_token"]
        return access_token


# Function to get the playlist by athenticating with the access token
def getArtistInfo(access_token, artistName):
    # Create Endpoint URL
    artistEndpoint = "https://api.spotify.com/v1/search"

    # Create GET Header
    getHeader = {"Authorization": "Bearer " + access_token}
    getParams = {'q': artistName, 'type': 'artist', 'limit': 1, "offset": 0}

    # Get the Response
    url_request = requests.get(artistEndpoint, headers=getHeader, params=getParams)

    # Save json Data
    url_data = url_request.json()

    if url_data["artists"]["total"] == 0:
        return None
    else:
        artist_list = [
            url_data["artists"]["items"][0]["id"],
            url_data["artists"]["items"][0]["name"],
            url_data["artists"]["items"][0]["genres"],
            url_data["artists"]["items"][0]["popularity"],
            url_data["artists"]["items"][0]["followers"]["total"],
            url_data["artists"]["items"][0]["images"][0]["url"]
        ]
        return artist_list



def getArtistTracks(artistID):
    # Create Endpoint URL
    trackEndpoint = "https://api.spotify.com/v1/artists/" + artistID + "/top-tracks"

    # Create GET Header
    getHeader = {"Authorization": "Bearer " + access_token}
    getParams = {'market': 'BE'}

    # Get the Response
    url_request = requests.get(trackEndpoint, headers=getHeader, params=getParams)

    # Save json Data
    url_data = url_request.json()
    return url_data



################################################
##     Main Programe                          ##
################################################

# API Requests + Check User Authentication
user_clientID = input("Enter your Spotify Client ID: ")
user_ClientSecret = input("Enter your Spotify Client Secret code: ")
access_token = getAccessToken(user_clientID, user_ClientSecret)


# Check for return value of getAccesToken()
if not access_token:
    print("Authentication Failed!")
else:
    # Get user playlist
    user_search = input("Which artist are you looking for (enter 'quit' or 'exit' to stop): ")

    # While user doesn't enter "quit" or "exit" keep asking for a playlist url
    while user_search:
        if user_search.lower() in ["quit", "exit"]:
            user_search = False
        else:
            # Json Data from playlist
            artistInfo = getArtistInfo(access_token, user_search)

            if not artistInfo:
                print("Artist not found!" + "\n")
                user_search = input("Which artist are you looking for (enter 'quit' or 'exit' to stop): ")
            else:
                artistTracks = getArtistTracks(artistInfo[0])

                # Create artist data table
                headersArtist = ["NAME", "GENRE", "POPULARITY", "FOLLOWERS"]
                dataArtist = [[artistInfo[1], artistInfo[2], artistInfo[3], artistInfo[4]]]

                tableArtist = columnar(dataArtist, headersArtist, no_borders=False)
                print("\n" + tableArtist + "\n")

                # Create data table
                headersTracks = ["NUMBER", "TITLE", "ALBUM", "RELEASE"]
                track_counter = 0
                dataTracks = []

                for track in artistTracks['tracks']:
                    track_counter += 1
                    song_name = track["name"].capitalize()
                    album_name = track["album"]["name"].capitalize()
                    release_date = track["album"]["release_date"]
                    current_data = [track_counter, song_name, album_name, release_date]
                    dataTracks.append(current_data)

                tableTrack = columnar(dataTracks, headersTracks, no_borders=False)
                print(tableTrack)
                print()
                user_search = input("Enter the playlist url (enter 'quit' or 'exit' to stop): ")

    # End
    print("\nBye, see you soon!")



















# Write to json data to file
# with open("artist.txt", "w", encoding="UTF-8") as txtfile, open("file.json", "w", encoding="UTF-8") as jsonfile:
#     txtfile.write(str(artistInfo))
#     json.dump(artistTracks, jsonfile)