import datetime
import json
import os
import re
import time


def search_latest_sequence_file(directory, actual_date):
    # Get all filenames in the directory that start with "seq and actual date"
    filenames = [f for f in os.listdir(directory) if f.startswith("seq_{}_".format(actual_date))]

    # Sort the filenames alphabetically in reverse order
    filenames.sort(reverse=True)

    # Check if there are any files that match the criteria
    if not filenames:
        print("No files found starting with 'seq_{}_'.".format(actual_date))
        return None

    # return the first file in thesorted list
    first_file = os.path.join(directory, filenames[0])
    return first_file


def read_sequence_file(sequence_file):
    try:
        with open(sequence_file, "r") as file:
            # Read the JSON content
            json_content = file.read()

            # Remove trailing commas in the JSON content
            json_content = re.sub(r",\s*([}\]])", r"\1", json_content)

            # Parse the JSON content into a list of dictionaries
            data = json.loads(json_content)

            # Check if the data is a list of dictionaries
            if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                return data
            else:
                print("The file does not contain a JSON array of objects.")
                return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def read_last_item_position(last_item_position_file):
    if not os.path.exists(last_item_position_file):
        return (None, None)
    try:
        with open(last_item_position_file, "r") as file:
            # Read the last item position
            json_content = file.read()
            # Remove trailing commas in the JSON content
            json_content = re.sub(r",\s*([}\]])", r"\1", json_content)
            # Parse the JSON content into a list of dictionaries
            data = json.loads(json_content)
            if not isinstance(data, dict):
                print("The file does not contain a JSON object.")
                return (None, None)
            else:
                return (data.get("last_seq_file", None), data.get("last_item_position", None))
    except Exception as e:
        print(f"An error occurred: {e}")
        return (None, None)


def write_last_item_position(last_item_position_file, last_seq_file, last_item_position):
    try:
        with open(last_item_position_file, "w") as file:
            data = {"last_seq_file": last_seq_file, "last_item_position": last_item_position}
            # Write the last item position
            file.write(json.dumps(data))
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


directory = "./test/sequence_file"
last_item_position_file = "./test/sequence_file/last_item_position.txt"

current_sequence_file = None
check_sequence_file = None
data = None
(last_seq_file, last_item_position) = read_last_item_position(last_item_position_file)
current_item = last_item_position + 1
actual_date = None
check_date = None

try:
    while True:
        check_date = datetime.datetime.now().strftime("%Y%m%d")
        if actual_date is None or check_date > actual_date:
            # new day or first start, start reading from the first line
            actual_date = check_date
            current_item = 0
        check_sequence_file = search_latest_sequence_file(directory, actual_date)
        if check_sequence_file is None:
            time.sleep(5)
            continue
        if current_sequence_file != check_sequence_file:
            # new sequence file
            current_sequence_file = check_sequence_file
            # print the log message
            log_msg = {
                "datetime": str(datetime.datetime.now()),
                "event": "reading_sequence_file",
                "file": current_sequence_file,
                "line": current_item,
            }
            print(json.dumps(log_msg))
        data = read_sequence_file(check_sequence_file)
        if data is None:
            time.sleep(5)
            continue
        if len(data) == 0:
            print("The sequence file {} contains no data.".format(current_sequence_file))
            time.sleep(5)
            continue
        if current_item > len(data) - 1:
            print(
                "Current item #{}, sequence file {} contains #{} items, nothing to process".format(
                    current_item, current_sequence_file, len(data)
                )
            )
            time.sleep(5)
            continue

        # process the current item

        # get the production order and target quantity
        production_order = data[current_item].get("production_order", None)
        target_quantity = data[current_item].get("target_quantity", None)

        # log prodcution order started
        log_msg = {
            "datetime": str(datetime.datetime.now()),
            "event": "order_started",
            "production_order": production_order,
            "target_quantity": target_quantity,
        }
        print(json.dumps(log_msg))

        # produce the number of requested items
        production_count = target_quantity
        while production_count > 0:
            log_msg = {
                "datetime": str(datetime.datetime.now()),
                "event": "item_produced",
                "production_order": production_order,
                "quantity_produced": 1,
            }
            print(json.dumps(log_msg))
            production_count -= 1
            time.sleep(2)

        # every item has been produced
        log_msg = {
            "datetime": str(datetime.datetime.now()),
            "event": "order_ended",
            "production_order": data[current_item]["production_order"],
        }
        print(json.dumps(log_msg))

        write_last_item_position(last_item_position_file, current_sequence_file, current_item)

        # proceed with next item in sequence file
        current_item += 1
except KeyboardInterrupt:
    print("The program was interrupted by the user.")
    pass
