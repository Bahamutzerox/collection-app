"""一次性把 標本採集記錄簿_v2.xlsx 的 4 個工作表搬到一份 Google Sheet。

用法：
    python migrate_to_sheets.py \
        --creds service_account.json \
        --sheet-id "<Google Sheet 的網址或 key>"

前置：
    1. 先在 Google 雲端硬碟手動建立一份空白 Google 試算表
    2. 把它「共用」給 service account 的 email（編輯者）
    3. 把該試算表的網址或 key 傳給 --sheet-id
"""
import argparse
import re
import openpyxl
import gspread
from google.oauth2.service_account import Credentials

SHEETS = ['採集記錄', '物種清單', '地名清單', '採集人清單']
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def read_xlsx(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = {}
    for name in SHEETS:
        ws = wb[name]
        rows = [['' if c is None else c for c in row]
                for row in ws.iter_rows(values_only=True)]
        while rows and all(c == '' for c in rows[-1]):   # trim trailing blank rows
            rows.pop()
        out[name] = rows
    wb.close()
    return out


def sheet_key(s):
    m = re.search(r'/d/([a-zA-Z0-9-_]+)', s)
    return m.group(1) if m else s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--xlsx', default='標本採集記錄簿_v2.xlsx')
    ap.add_argument('--creds', required=True, help='service account JSON 路徑')
    ap.add_argument('--sheet-id', required=True, help='目標 Google Sheet 網址或 key')
    args = ap.parse_args()

    data = read_xlsx(args.xlsx)
    creds = Credentials.from_service_account_file(args.creds, scopes=SCOPES)
    book = gspread.authorize(creds).open_by_key(sheet_key(args.sheet_id))

    for name in SHEETS:
        rows = data[name]
        ncols = max((len(r) for r in rows), default=1)
        try:
            ws = book.worksheet(name)
        except gspread.WorksheetNotFound:
            ws = book.add_worksheet(title=name, rows=len(rows) + 50, cols=ncols + 2)
        ws.clear()
        ws.resize(rows=len(rows) + 50, cols=ncols + 2)
        ws.update(range_name='A1', values=rows, value_input_option='RAW')
        print(f'  {name}: 寫入 {len(rows)} 列（含標頭）')

    print('✓ 搬移完成')


if __name__ == '__main__':
    main()
