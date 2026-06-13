# 標本採集記錄 App

以 Streamlit 製作的標本採集記錄輸入 / 查詢 / 編輯系統，資料存在 Google Sheets，可在任何裝置透過瀏覽器使用。

## 功能
- 新增記錄：學名、科名、中文名、地名（縣市/鄉鎮連動）、日期、採集人皆為搜尋式下拉，多數欄位自動帶入
- 查詢：跨欄位、多關鍵字搜尋
- 編輯：點選一列帶回上方表單，用既有下拉修改後儲存
- 刪除：點選一列直接刪除
- 進站需密碼

---

## 一次性設定（部署前做一次）

### A. 建立 Google service account 與 Google Sheet
1. 到 [Google Cloud Console](https://console.cloud.google.com/) 建立一個專案
2. 「API 和服務 → 程式庫」啟用 **Google Sheets API** 和 **Google Drive API**
3. 「API 和服務 → 憑證 → 建立憑證 → 服務帳戶」建立 service account
4. 進入該服務帳戶 → 「金鑰 → 新增金鑰 → JSON」，下載金鑰檔，存成本機的 `service_account.json`（**不要進 repo**）
5. 在 Google 雲端硬碟手動建立一份空白 Google 試算表
6. 把試算表「共用」給服務帳戶的 email（在 JSON 裡的 `client_email`），權限選「編輯者」
7. 複製試算表網址（含 `/d/<KEY>/`）

### B. 搬移現有資料到 Google Sheet
```bash
pip install gspread google-auth openpyxl
python migrate_to_sheets.py --creds service_account.json --sheet-id "貼上試算表網址"
```
完成後 Google Sheet 會有 4 個工作表：採集記錄 / 物種清單 / 地名清單 / 採集人清單。

### C. 設定本機 secrets（本機測試用）
1. 複製 `.streamlit/secrets.toml.example` 成 `.streamlit/secrets.toml`
2. 填入：
   - `app_password`：自訂進站密碼
   - `sheet_id`：試算表網址或 key
   - `[gcp_service_account]`：把 `service_account.json` 內容逐欄填入（`private_key` 內的換行保留 `\n`）

### D. 本機測試
```bash
pip install -r requirements.txt
streamlit run app.py
```
輸入密碼後即可使用；新增/編輯/刪除會直接寫進 Google Sheet。

---

## 部署到 Streamlit Community Cloud（免費、永久保存）

1. 把專案推到一個 **private** GitHub repo（`.gitignore` 已排除 `.xlsx`、secrets、JSON 金鑰）
2. 到 [share.streamlit.io](https://share.streamlit.io/) 用 GitHub 登入，授權讀取 private repo
3. New app → 選 repo / 分支 / `app.py`
4. Advanced settings → **Secrets**：把本機 `.streamlit/secrets.toml` 的完整內容貼上
5. Deploy，取得 `https://<名稱>.streamlit.app` 網址，進站需密碼

之後改了程式碼 push 到 GitHub，Streamlit Cloud 會自動重新部署；資料在 Google Sheet 不受影響。

---

## 檔案說明
| 檔案 | 用途 |
|------|------|
| `app.py` | 主程式 |
| `台灣各行政區列表.py` | 全台縣市/鄉鎮清單（縣市鄉鎮連動用） |
| `migrate_to_sheets.py` | 一次性資料搬移腳本（本機用） |
| `requirements.txt` | 雲端相依套件 |
| `.streamlit/secrets.toml` | 機密設定（本機，不進 repo） |
| `標本採集記錄簿_v2.xlsx` | 原始資料備份（本機，不進 repo） |
