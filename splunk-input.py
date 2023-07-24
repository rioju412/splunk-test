import json
import logging
import requests
import urllib3
import time

# No SSL certificate verification checks
urllib3.disable_warnings()

# Create Debugging log
logging.basicConfig(level=logging.DEBUG)

with open('./conf/conf.json', 'r', encoding='utf-8') as mainconf:
    conf = json.load(mainconf)

SPLUNK_SERVER = conf['splunk']['server']
SPLUNK_HEC_TOKEN = conf['splunk']['token']
SPLUNK_HEADER = {"Authorization": "Splunk " + SPLUNK_HEC_TOKEN}
SPLUNK_HEC_URL = f'https://{SPLUNK_SERVER}:8088/services/collector/event'

# Start Session with HTTP Keep-Alive
session = requests.session()

log_count = 1

def input_splunk(input_data, filepath=None):
    """Splunk HEC Input"""
    global log_count
    try:
        if filepath:
            with open(filepath, 'r', encoding='utf-8') as input_file:
                input_data = json.load(input_file)
                response = session.post(SPLUNK_HEC_URL, json=input_data, verify=False,
                                         headers=SPLUNK_HEADER, timeout=10)
        else:
            response = session.post(SPLUNK_HEC_URL, json=input_data, verify=False,
                                     headers=SPLUNK_HEADER, timeout=10)

        if response.status_code != 200:
            logging.error("HTTP error %s: %s", response.status_code, response.text)
            return False

        logging.debug("The %sth message has been sent.", log_count)
        log_count += 1
        return True

    except Exception as error:
        logging.error("Exception occurred", exc_info=True)
        return False

if __name__ == '__main__':
    for i in range(150):
        test_dict = {
            "time": int(time.time()),
            "event": {
                "event": f"Event number{i}"
            },
            "index": "bob12",
            "source": "my_source",
            "sourcetype": "my_sourcetype",
            "host": "my_host"
        }
        if not input_splunk(test_dict):
            break
        time.sleep(1)

# Close Session
session.close()
logging.info('Session has been closed')
