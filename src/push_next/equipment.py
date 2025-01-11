import json
import os
import re
import time


def get_next_order(directory: str, suffix: list[str] = []) -> str | None:
    filenames: list[str] = []
    for suffix_item in suffix:
        filenames += [f for f in os.listdir(directory) if f.endswith(suffix_item)]

    # Sort the filenames alphabetically in reverse order
    filenames.sort(reverse=True)

    # Check if there are any files that match the criteria
    if not filenames:
        return None

    # return the first file in thesorted list
    first_file = os.path.join(directory, filenames[0])
    return first_file


def read_next_order_file(next_order_file: str) -> dict[str, str] | None:
    try:
        with open(next_order_file, "r") as file:
            # Read the JSON content
            json_content = file.read()

            # Remove trailing commas in the JSON content
            json_content = re.sub(r",\s*([}\]])", r"\1", json_content)

            # Parse the JSON content
            data: dict[str, str] = json.loads(json_content)
    except Exception:
        print("The file does not contain a a valid JSON object of type str, str.")
        return None

    return data


next_order_dir = "./test/next_order"
in_procress_order_dir = "./test/in_process"


try:
    while True:
        next_syn_file = get_next_order(next_order_dir, ["syn"])
        if next_syn_file is None:
            print("No next order found (retry in 5 seconds)")
            time.sleep(5)
            continue

        next_order_file = next_syn_file.removesuffix(".syn")
        print("Next order file: {}".format(next_order_file))

        data = read_next_order_file(next_order_file)
        if data is None or len(data) == 0:
            print("Next order file is empty (ignored and retry in 5 seconds)")
            time.sleep(5)
            continue

        print("Next order file data: {}".format(data))

        # Move the file to another folder
        new_location = os.path.join(in_procress_order_dir, os.path.basename(next_order_file))
        os.rename(next_order_file, new_location)

        # Remove the .syn file
        os.remove(next_order_file + ".syn")

        # Processing
        print("Processing order: {}".format(data["production_order"]))
        time.sleep(5)

except KeyboardInterrupt:
    print("The program was interrupted by the user.")
    pass
