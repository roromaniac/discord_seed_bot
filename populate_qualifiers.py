import os
import json
import pandas as pd

from collections import OrderedDict
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# Read AND write access is required.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Keep your existing private/source settings if they differ.
PRIVATE_SHEET_ID = os.getenv("PRIVATE_QUALIFIER_SHEET_ID")
RANGE_NAME = "Simplified Responses!A2:G"
NUM_QUALIFIERS = 24

PUBLIC_QUALIFIER_SHEET_ID = os.getenv("PUBLIC_QUALIFIER_SHEET_ID")


def get_sheetname_from_qual_num(qual_num: int) -> str:
    match qual_num:
        case qual_num if 1 <= qual_num <= 4:
            return f"Qual #1-4"
        case qual_num if 5 <= qual_num <= 8:
            return f"Qual #5-8"
        case qual_num if 9 <= qual_num <= 12:
            return f"Qual #9-12"
        case qual_num if 13 <= qual_num <= 16:
            return f"Qual #13-16"
        case qual_num if 17 <= qual_num <= 20:
            return f"Qual #17-20"
        case qual_num if 21 <= qual_num <= 24:
            return f"Qual #21-24"
        case _:
            raise ValueError(f"Invalid qualifier number: {qual_num}")

def get_column_range_from_qual_num(qual_num: int, is_waitlist: bool) -> str:
    if qual_num in [1, 5, 9, 13, 17, 21] and not is_waitlist:
        return f"A3:A26"
    elif qual_num in [1, 5, 9, 13, 17, 21] and is_waitlist:
        return f"B3:B"
    elif qual_num in [2, 6, 10, 14, 18, 22] and not is_waitlist:
        return f"F3:F26"
    elif qual_num in [2, 6, 10, 14, 18, 22] and is_waitlist:
        return f"G3:G"
    elif qual_num in [3, 7, 11, 15, 19, 23] and not is_waitlist:
        return f"K3:K26"
    elif qual_num in [3, 7, 11, 15, 19, 23] and is_waitlist:
        return f"L3:L"
    elif qual_num in [4, 8, 12, 16, 20, 24] and not is_waitlist:
        return f"P3:P26"
    elif qual_num in [4, 8, 12, 16, 20, 24] and is_waitlist:
        return f"Q3:Q"
    else:
        raise ValueError(f"Invalid qualifier number: {qual_num}")

def qualifier_population(qualifier_dataframe: pd.DataFrame, creds):
    """
    Creates the Excel file and publishes all qualifiers using batch requests.
    MAIN and WAITLIST keep their separate ranges, with no added headers.
    """
    OUTDIR = "data"
    OUTPATH = os.path.join(OUTDIR, "qualifiers.xlsx")

    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)

    # Sort once so both MAIN and WAITLIST follow timestamp order.
    df = qualifier_dataframe.copy()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df = df.sort_values("Timestamp", kind="stable")

    # Collect all Google Sheets updates here.
    public_updates = []

    with pd.ExcelWriter(OUTPATH, engine="xlsxwriter") as writer:
        for qualifier_num in range(1, NUM_QUALIFIERS + 1):
            qstr = str(qualifier_num)

            # All three choices have equal rank.
            mask_choices = (
                (df["Choice 1"] == qstr)
                | (df["Choice 2"] == qstr)
                | (df["Choice 3"] == qstr)
            )
            mask_waitlist = (df["Waitlist"] == qstr)

            # Duplicate registrations must not consume extra MAIN slots.
            choice_signups = df[mask_choices].drop_duplicates(
                subset=["Twitch"], keep="first"
            )
            main_df = choice_signups.iloc[:24]
            main_names = list(main_df["Twitch"])

            # Combine explicit waitlist signups and overflow signups.
            waitlist_df = df[
                (mask_waitlist | mask_choices)
                & ~df["Twitch"].isin(main_names)
            ]
            waitlist_df = waitlist_df.drop_duplicates(
                subset=["Twitch"], keep="first"
            )
            waitlist_names = list(waitlist_df["Twitch"])

            # Excel file layout.
            sheet_dict = OrderedDict()
            max_rows = max(len(main_names), len(waitlist_names))
            sheet_dict["MAIN"] = (
                main_names + [""] * (max_rows - len(main_names))
            )
            sheet_dict["WAITLIST"] = (
                waitlist_names + [""] * (max_rows - len(waitlist_names))
            )
            sheet_df = pd.DataFrame(sheet_dict)

            sheet_name = f"Qualifier {qualifier_num}"
            sheet_df.to_excel(writer, index=False, sheet_name=sheet_name)

            # Prepare this qualifier's two Google Sheets ranges.
            public_sheet_name = get_sheetname_from_qual_num(qualifier_num)
            escaped_sheet_name = public_sheet_name.replace("'", "''")

            main_range = get_column_range_from_qual_num(
                qualifier_num, is_waitlist=False
            )
            waitlist_range = get_column_range_from_qual_num(
                qualifier_num, is_waitlist=True
            )

            # Names only: MAIN fits the 24 cells in rows 3–26.
            public_updates.append({
                "range": f"'{escaped_sheet_name}'!{main_range}",
                "values": [[name] for name in main_names],
            })
            public_updates.append({
                "range": f"'{escaped_sheet_name}'!{waitlist_range}",
                "values": [[name] for name in waitlist_names],
            })

    # Run once, after all qualifiers and Excel tabs have been prepared.
    write_ranges_to_sheet(creds, public_updates)


def write_ranges_to_sheet(creds, updates: list[dict]):
    """
    Clears all output ranges in one request, then writes all populated lists
    in one request.
    """
    if not updates:
        return

    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    # Request 1: clear all ranges, including lists that are now empty.
    sheet.values().batchClear(
        spreadsheetId=PUBLIC_QUALIFIER_SHEET_ID,
        body={"ranges": [item["range"] for item in updates]},
    ).execute()

    # Empty lists have already been cleared; only write populated lists.
    populated_updates = [item for item in updates if item["values"]]

    if populated_updates:
        # Request 2: write all populated MAIN and WAITLIST lists together.
        sheet.values().batchUpdate(
            spreadsheetId=PUBLIC_QUALIFIER_SHEET_ID,
            body={
                "valueInputOption": "RAW",
                "data": populated_updates,
            },
        ).execute()

def main():
    if not PRIVATE_SHEET_ID:
        raise RuntimeError("Missing PRIVATE_SHEET_ID")
    if not PUBLIC_QUALIFIER_SHEET_ID:
        raise RuntimeError("Missing PUBLIC_QUALIFIER_SHEET_ID")

    # Load credentials info as a dict from env variable exactly as in visit_state.py
    raw_creds = os.getenv("SERVICE_ACCOUNT_JSON")
    if not raw_creds:
        raise RuntimeError("Missing SERVICE_ACCOUNT_JSON")
    creds_info = json.loads(raw_creds)

    try:
        from google.oauth2 import service_account
        creds = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=SCOPES,
        )

        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()

        result = (
            sheet.values()
            .get(spreadsheetId=PRIVATE_SHEET_ID, range=RANGE_NAME)
            .execute()
        )
        columns = [
            "Timestamp",
            "Twitch",
            "Discord",
            "Choice 1",
            "Choice 2",
            "Choice 3",
            "Waitlist",
        ]
        values = result.get("values", [])

        # Google Sheets may omit trailing blank cells.
        values = [row + [""] * (len(columns) - len(row)) for row in values]

        qual_df = pd.DataFrame(values, columns=columns)
        qualifier_population(qual_df, creds)
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()