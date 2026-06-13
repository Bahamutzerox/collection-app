# 標本採集記錄 App

以 Streamlit 製作的標本採集記錄輸入 / 查詢 / 編輯系統。採**兩個 private repo**：

- **程式 repo**（這個）— 部署到 Streamlit Cloud，存檔時不會變動 → app 不會被重開
- **資料 repo** — 放 4 個 CSV 資料檔（採集記錄 / 物種清單 / 地名清單 / 採集人清單）

App 透過 GitHub API 讀寫資料 repo，每次新增 / 編輯 / 刪除都會 commit 回資料 repo（資料自動有版本歷史與備份），而程式 repo 不動，所以 app 不會每次存檔就重開。

## 功能
- 新增：學名 / 科名 / 中文名 / 地名（縣市·鄉鎮連動）/ 日期 / 採集人 皆為搜尋式下拉，多數欄位自動帶入
- 查詢：跨欄位、多關鍵字搜尋
- 編輯：點選一列帶回上方表單，用既有下拉修改後儲存
- 刪除：點選一列直接刪除
- 進站需密碼

---

## 一次性設定

### A. 產生 CSV（已做過可略）
```bash
pip install openpyxl pandas
python export_to_csv.py        # 由 標本採集記錄簿_v2.xlsx 產生 data/*.csv
```

### B. 建立兩個 private repo
1. **資料 repo**（例：`collection-data`）：建立 private repo，把本機 `data/` 裡的 4 個 CSV 放進去
   - 最簡單：在 repo 頁面 **Add file → Upload files**，把 4 個 CSV 拖進去 commit
   - 路徑要維持 `data/採集記錄.csv` 等（即 repo 內也放在 `data/` 資料夾）
2. **程式 repo**（例：`collection-app`）：把這個資料夾推上去（`.gitignore` 已排除 `data/`、`.xlsx`、secrets）

### C. 建立 GitHub Token（PAT）
1. GitHub → Settings → Developer settings → **Fine-grained tokens** → Generate new token
2. Repository access → Only select repositories → 選 **資料 repo**
3. Permissions → Repository permissions → **Contents = Read and write**
4. 複製 token（只顯示一次），**不要貼進任何 repo 或聊天室**

### D. 設定本機 secrets
複製 `.streamlit/secrets.toml.example` 成 `.streamlit/secrets.toml`，填入：
- `app_password`：進站密碼
- `data_repo`：`你的帳號/資料repo名`
- `github_token`：上一步的 PAT

### E. 本機測試
```bash
pip install -r requirements.txt
streamlit run app.py
```
輸入密碼後新增/編輯/刪除一筆，到「資料 repo」的 commit 紀錄確認有寫回。

---

## 部署到 Streamlit Community Cloud（免費）

1. [share.streamlit.io](https://share.streamlit.io/) 用 GitHub 登入，授權讀取 private repo
2. New app → 選 **程式 repo** / 分支 / `app.py`
3. Advanced settings → **Secrets**：貼上本機 `.streamlit/secrets.toml` 的內容
4. Deploy → 取得 `https://<名稱>.streamlit.app`，進站需密碼

之後改程式碼 push 到程式 repo，Cloud 自動重新部署；資料在資料 repo，不受影響。

---

## 檔案說明
| 檔案 | 用途 |
|------|------|
| `app.py` | 主程式 |
| `台灣各行政區列表.py` | 全台縣市/鄉鎮清單（連動下拉用） |
| `export_to_csv.py` | 由 xlsx 產生 data/*.csv（一次性，本機用） |
| `data/*.csv` | 資料（**放資料 repo**，程式 repo 已排除） |
| `requirements.txt` | 雲端相依套件 |
| `.streamlit/secrets.toml` | 機密設定（本機，不進 repo） |
| `標本採集記錄簿_v2.xlsx` | 原始 Excel 備份（本機，不進 repo） |
