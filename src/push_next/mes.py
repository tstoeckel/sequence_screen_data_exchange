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


def write_next_order_file(next_order_file: str, payload: dict[str, str]) -> bool:
    try:
        with open(next_order_file, "w") as datafile:
            datafile.write(json.dumps(payload))
        with open(next_order_file + ".syn", "w") as synfile:
            synfile.write("")
        # print("The data and syn file have been written successfully.")
    except Exception as e:
        print("An error occurred while writing the data or syn file: {}".format(e))
        return False

    return True


next_order_dir = "./test/next_order"
in_procress_order_dir = "./test/in_process"
counter = 0

try:
    while True:
        next_syn_file = get_next_order(next_order_dir, ["syn"])
        if next_syn_file is None:
            write_next_order_file(f"{next_order_dir}/{counter:03}.data", {"production_order": "4711"})
            print("Next order file pushed (sleeping for 2 seconds)")
            counter += 1
        else:
            print("Next order file already exists (sleeping for 2 seconds)")
        time.sleep(2)

except KeyboardInterrupt:
    print("The program was interrupted by the user.")
    pass
