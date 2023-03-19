import pandas as pd
import requests
from requests.auth import HTTPBasicAuth


API_KEY = "TZLtGWHwHmYJ3Jwljssu2s4Q0h25TqoDUzgAKyVlrWT9"
API_APP_URL = "https://api.au-syd.assistant.watson.cloud.ibm.com/instances/b2c3e81c-654d-404e-aede-41d74026d039/"
API_ASSISTANT_ID = "3165df54-0baf-47fe-aa58-3999ee99c8ce"
API_VERSION = "2021-11-27"

CSV_INPUT_FILE="query.csv"

def api_get_session_id():
    bAuth = HTTPBasicAuth('apikey', API_KEY)
    req = requests.post(API_APP_URL + 'v2/assistants/' + API_ASSISTANT_ID + '/sessions?version=' + API_VERSION, auth=bAuth)
    session_id = req.json()["session_id"]
    return session_id

def test_file(session_id):
    print("Loading csv file...")
    data_frame = pd.read_csv(CSV_INPUT_FILE, sep=',', header=None, names=["message", "intent"])
    numOfRows = data_frame.shape[0]
    print("Total rows: " + str(numOfRows))
    valid_messages = []
    invalid_messages = []
    for index, row in data_frame.iterrows():
        #if index > 100: #if testing lower amount of rows
        #    break
        printProgressBar(index, numOfRows)
        response = api_send_input(session_id, row["message"])
        if len(response["output"]["intents"]) > 0:
            if response["output"]["intents"][0]["intent"] == row["intent"]:
                valid_messages.append({"rowindex" : index, "message": row["message"]})
            else:
                invalid_messages.append({"rowindex" : index, "message": row["message"], "response_intent": row["intent"]})
        else:
            invalid_messages.append({"rowindex" : index, "message": row["message"], "response_intent": "None"})
    printProgressBar(numOfRows, numOfRows) #end of progress bar

    return (valid_messages, invalid_messages)


def api_send_input(session_id, input_text):
    bAuth = HTTPBasicAuth('apikey', API_KEY)
    headers = {'Content-Type': 'application/json'}
    data = {"input": {"text": input_text}}
    req = requests.post(API_APP_URL + 'v2/assistants/' + API_ASSISTANT_ID + '/sessions/' + session_id + '/message?version=' + API_VERSION, json=data, auth=bAuth)
    response = req.json()
    return response

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = 'â–', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

if __name__ == '__main__':
    print("Running data validation test from file: " + CSV_INPUT_FILE)
    print("Getting session...")
    session_id = api_get_session_id()
    print("session_id: ", session_id)
    print("Testing data...")
    (valid_messages, invalid_messages) = test_file(session_id)
    print("-----Results-----")
    print("Valid messages: " + str(len(valid_messages)))
    print("Invalid messages: " + str(len(invalid_messages)))
    if len(invalid_messages) > 0:
        print("Invalid messages:")
        for message in invalid_messages:
            print(str(message["rowindex"]) + ": " + message["message"] + " | " + message["response_intent"])

    print("------DONE-----")