import sys
import json
import re
from datetime import datetime

# date format that teacher wants
DATE_FMT = "%Y-%m-%d %H:%M"


def check_flight(parts):
    # this function checks 1 line from csv
    # if valid -> returns (True, flight_dict)
    # if not valid -> returns (False, list_of_errors)

    errs = []

    if len(parts) != 6:
        errs.append("missing required fields")
        return False, errs, None

    flight_id = parts[0].strip()
    origin = parts[1].strip()
    destination = parts[2].strip()
    dep_str = parts[3].strip()
    arr_str = parts[4].strip()
    price_str = parts[5].strip()

    # flight id rule
    if not re.fullmatch(r"[A-Za-z0-9]{2,8}", flight_id):
        if len(flight_id) > 8:
            errs.append("flight_id too long (more than 8 characters)")
        else:
            errs.append("invalid flight_id")

    # origin / destination rule
    if not re.fullmatch(r"[A-Z]{3}", origin):
        errs.append("invalid origin code")
    if not re.fullmatch(r"[A-Z]{3}", destination):
        errs.append("invalid destination code")

    # date rule
    dep_dt = None
    arr_dt = None

    try:
        dep_dt = datetime.strptime(dep_str, DATE_FMT)
    except:
        errs.append("invalid departure datetime")

    try:
        arr_dt = datetime.strptime(arr_str, DATE_FMT)
    except:
        errs.append("invalid arrival datetime")

    if dep_dt and arr_dt:
        if arr_dt <= dep_dt:
            errs.append("arrival before departure")

    # price rule
    try:
        price = float(price_str)
        if price <= 0:
            errs.append("negative price value")
    except:
        errs.append("invalid price")
        price = None

    if len(errs) > 0:
        return False, errs, None

    flight = {
        "flight_id": flight_id,
        "origin": origin,
        "destination": destination,
        "departure_datetime": dep_str,
        "arrival_datetime": arr_str,
        "price": price
    }

    return True, [], flight


def read_csv_file(csv_path):
    good = []
    bad = []

    f = open(csv_path, "r", encoding="utf-8")
    lines = f.readlines()
    f.close()

    for i in range(len(lines)):
        line_no = i + 1
        raw = lines[i].strip()

        # ignore empty lines
        if raw == "":
            continue

        # comments are not data but go to errors
        if raw.startswith("#"):
            bad.append(f"Line {line_no}: {raw} → comment line, ignored for data parsing")
            continue

        parts = raw.split(",")

        # skip header
        if line_no == 1 and parts[0].strip() == "flight_id":
            continue

        ok, errs, flight = check_flight(parts)
        if ok:
            good.append(flight)
        else:
            bad.append(f"Line {line_no}: {raw} → " + ", ".join(errs))

    return good, bad


def save_json(data, path):
    out = open(path, "w", encoding="utf-8")
    json.dump(data, out, indent=2)
    out.close()


def save_errors(errs, path):
    out = open(path, "w", encoding="utf-8")
    for e in errs:
        out.write(e + "\n")
    out.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: python flight_parser.py path/to/file.csv")
        return

    csv_path = sys.argv[1]

    good, bad = read_csv_file(csv_path)

    save_json(good, "db.json")
    save_errors(bad, "errors.txt")

    print("Finished.")
    print("Valid flights:", len(good))
    print("Invalid lines:", len(bad))
    print("Created db.json and errors.txt")


main()
