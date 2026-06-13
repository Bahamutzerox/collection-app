"""把 標本採集記錄簿_v2.xlsx 的 4 個工作表匯出成 data/*.csv（純本機，無需任何憑證）。

    python export_to_csv.py

之後 data/ 裡的 4 個 CSV 就是 app 在 repo 裡讀寫的資料來源。
"""
import os
import openpyxl
import pandas as pd

SRC = os.path.join(os.path.dirname(__file__), '標本採集記錄簿_v2.xlsx')
OUT = os.path.join(os.path.dirname(__file__), 'data')
SHEETS = ['採集記錄', '物種清單', '地名清單', '採集人清單']


def clean(c):
    if c is None:
        return ''
    if isinstance(c, float) and c.is_integer():
        return str(int(c))      # 5273.0 -> "5273"
    return c


def main():
    os.makedirs(OUT, exist_ok=True)
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    for name in SHEETS:
        rows = [[clean(c) for c in r] for r in wb[name].iter_rows(values_only=True)]
        while rows and all(c == '' for c in rows[-1]):   # trim trailing blank rows
            rows.pop()
        header = rows[0]
        # drop phantom trailing columns whose header is empty
        ncols = max((i + 1 for i, h in enumerate(header) if str(h).strip()),
                    default=len(header))
        header = header[:ncols]
        data = [r[:ncols] for r in rows[1:]]
        df = pd.DataFrame(data, columns=header)
        df.to_csv(os.path.join(OUT, f'{name}.csv'), index=False, encoding='utf-8')
        print(f'  {name}.csv: {len(data)} 列')
    wb.close()
    print('✓ 匯出完成 → data/')


if __name__ == '__main__':
    main()
