# CPE Practice Arena (CPE 49 題 C 語言實戰練功場)

專為大學程式能力檢定（CPE, Collegiate Programming Examination）打造的純 C 語言實戰練習平台與 AI 程式導師。
內建 MinGW GCC 本地評測系統、多組極端邊界測試資料、時間與空間複雜度檢測，並整合 Antigravity CLI 扮演專業程式思維導師。

---

## ✨ 核心特色

1. **純 C 語言專屬環境**：針對 CPE 考生量身打造，使用本地 GCC 14.2+ 編譯器，嚴格模擬競賽考試環境。
2. **多測資綜合評測引擎**：每題配置範例（Sample）、極端邊界（Corner Cases，如 $i > j$、負數模除）及規模測試（Scale Cases），杜絕硬爆暴力解。
3. **時間與空間限制保護**：
   - 即時限制執行逾時（TLE）與記憶體限制。
   - 標註建議時間與空間複雜度指標。
4. **AI 程式導師 (Powered by Antigravity CLI)**：
   - **免 API Key**：直接調用本機 `agy` CLI。
   - **四維思維解析**：思維意圖剖析、亮點優勢、邏輯盲點除錯、後續實現建議。
   - **對話框即時答疑**：支援 Session 對話管理（新增、封存、切換、刪除）。
5. **解法版本管理**：
   - 支援隨時儲存不同解法版本（初版、雙指標版等）。
   - 支援 600ms 即時自動存檔，刷新或重啟不掉 Code。
6. **Cursor 風格質感介面**：
   - 舒適溫潤的深色炭黑主題（IDE Dark）。
   - 三欄可自由拖曳調整寬度。
   - 支援 Marked.js 完整 Markdown 渲染與 KaTeX 數學公式解析。
   - 極簡線條圖示（FontAwesome），嚴格零 Emoji。

---

## 🛠️ 系統需求

- **作業系統**：Windows 10 / 11
- **Python**：Python 3.10+
- **C 編譯器**：GCC (MinGW-w64) 已加入系統環境變數 PATH
- **AI 導師依賴（可選）**：安裝並登入 [Google Antigravity CLI](https://github.com/google/antigravity) (`agy`)

---

## 🚀 快速啟動

### 方式一：直接雙擊批次檔（推薦）
雙擊專案目錄下的 `start.bat`：
```cmd
start.bat
```
或桌面上的「開啟CPE練習場.bat」。腳本會自動啟動後端並在預設瀏覽器中開啟 `http://localhost:5050`。

### 方式二：命令列啟動
```bash
python server.py
```
啟動後在瀏覽器開啟：`http://localhost:5050`

---

## 📁 專案架構

```
CPE_Practice/
├── server.py           # 本地 HTTP 評測伺服器與 API 端點 (Port 5050)
├── index.html          # 單頁響應式 IDE 前端 (Tailwind + Marked + KaTeX)
├── problems.json       # CPE 精選題庫（題目規格、測資、解答、複雜度）
├── setup_problems.py   # 題庫生成與擴充腳本
├── start.bat           # 一鍵啟動批次檔
├── .gitignore          # Git 忽略設定
└── README.md           # 專案說明文件
```

---

## 🧪 支援題型

- **基礎數論與模擬**（3n+1、進位計算、Hashmat 戰士差值、物理位移等）
- **大數運算與進制轉換**（斐波那契進制、2的冪次等）
- **排序與中位數統計**（Vito's family、火車車廂調換等）
- **字串解析與頻率統計**（鍵盤位移、字元出現次數等）
- **二維陣列與狀態模擬**（旋轉矩陣、踩地雷等）

---

## 📄 授權條款

MIT License
