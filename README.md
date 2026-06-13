# 標本採集記錄 App

以 Streamlit 製作的標本採集記錄輸入 / 查詢 / 編輯系統。資料以 CSV 存在這個 **private GitHub repo** 的 `data/` 資料夾，app 直接讀取，新增 / 編輯 / 刪除時自動 commit 回 repo。可在任何裝置透過瀏覽器使用。

## 功能
- 新增記錄：學名、科名、中文名、地名（縣市/鄉鎮連動）、日期、採集人皆為搜尋式下拉，多數欄位自動帶入
- 查詢：跨欄位、多關鍵字搜尋
- 編輯：點選一列帶回上方表單，用既有下拉修改後儲存
- 刪除：點選一列直接刪除
- 進站需密碼
- **每次新增 / 編輯 / 刪除都會 commit 回 GitHub** → 資料自動有版本歷史與備份

## 資料怎麼存
| 工作表 | 檔案 |
|--------|------|
| 採集記錄 | `data/採集記錄.csv` |
| 物種清單 | `data/物種清單.csv` |
| 地名清單 | `data/地名清單.csv` |
| 採集人清單 | `data/採集人清單.csv` |

App 讀本機（容器內）的 CSV；寫入時把整份 CSV 透過 GitHub API 寫回 repo。Streamlit Cloud 重新部署時會重新 checkout，拿到最新的 CSV，所以資料永久保存。

---

## 一次性設定

### A. 把現有 xlsx 匯出成 CSV（已做過可略）
```bash
pip install openpyxl pandas
python export_to_csv.py
```
產生 `data/` 下的 4 個 CSV。

### B. 建立 GitHub Personal Access Token（PAT）
1. GitHub → Settings → Developer settings → **Fine-grained tokens** → Generate new token
2. Resource owner 選你自己；Repository access 選 **Only select repositories** → 選這個 repo
3. Permissions → Repository permissions → **Contents** 設為 **Read and write**
4. 產生後複製 token（只會顯示一次），**不要貼進 repo 或聊天室**

### C. 設定本機 secrets
1. 複製 `.streamlit/secrets.toml.example` 成 `.streamlit/secrets.toml`
2. 填入：
   - `app_password`：自訂進站密碼
   - `github_repo`：`你的帳號/repo名`
   - `github_token`：上一步的 PAT

### D. 本機測試
```bash
pip install -r requirements.txt
streamlit run app.py
```
輸入密碼即可使用；新增/編輯/刪除會 commit 回 GitHub（去 repo 的 commit 紀錄可看到）。

---

## 部署到 Streamlit Community Cloud（免費）

1. 把專案推到 **private** GitHub repo（`.gitignore` 已排除 `.xlsx`、secrets、PAT；`data/*.csv` 會進 repo，這是資料本體）
2. [share.streamlit.io](https://share.streamlit.io/) 用 GitHub 登入，授權讀取 private repo
3. New app → 選 repo / 分支 / `app.py`
4. Advanced settings → **Secrets**：貼上本機 `.streamlit/secrets.toml` 的完整內容
5. Deploy，得到 `https://<名稱>.streamlit.app`，進站需密碼

之後改程式碼 push，Cloud 會自動重新部署；資料在 `data/*.csv`，不受影響。

---

## 檔案說明
| 檔案 | 用途 |
|------|------|
| `app.py` | 主程式 |
| `data/*.csv` | 資料本體（採集記錄與三個對照表） |
| `台灣各行政區列表.py` | 全台縣市/鄉鎮清單（連動下拉用） |
| `export_to_csv.py` | 把 xlsx 匯出成 data/*.csv（一次性，本機用） |
| `requirements.txt` | 雲端相依套件 |
| `.streamlit/secrets.toml` | 機密設定（本機，不進 repo） |
| `標本採集記錄簿_v2.xlsx` | 原始 Excel 備份（本機，不進 repo） |
