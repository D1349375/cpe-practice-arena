# CPE Practice Arena (CPE 49 題 C 語言實戰練功場)

<div align="center">

![C Language](https://img.shields.io/badge/Language-C11%20%2F%20C99-00599C?logo=c&logoColor=white)
![Python Backend](https://img.shields.io/badge/Backend-Python%203.10+-3776AB?logo=python&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-TailwindCSS%20%7C%20KaTeX-38B2AC?logo=tailwindcss&logoColor=white)
![AI Mentor](https://img.shields.io/badge/AI%20Mentor-Antigravity%20CLI%20(agy)-4285F4?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

專為**大學程式能力檢定（CPE, Collegiate Programming Examination）**一顆星 49 題精選打造的純 C 語言沉浸式練習平台。  
整合本機 MinGW GCC 評測引擎、多測資極端邊界測試、時間/空間複雜度監控，並無縫串接 **Google Antigravity CLI (`agy`)** 免費 AI 程式思維導師。

</div>

---

## 📸 核心特色亮點

- 💻 **純 C 語言競賽環境**：針對 CPE 考生痛點（無 C++ STL、需手刻 `qsort` 與字串指標），使用本地 GCC 14.2+ 編譯器，最逼真的考試體感。
- ⚡ **多測資綜合評測引擎**：每題配置至少 3 組測資：
  - **範例測資 (Sample)**：UVa 官方標準輸入輸出。
  - **極端邊界陷阱 (Corner Cases)**：特別加入 $i > j$ 未交換、負數模除、64-bit 溢位、多組測資殘留換行等經典扣分陷阱。
  - **規模測試 (Scale Cases)**：測試演算法在合理資料上限下的運行耗時。
- ⏱️ **時間與空間限制 (TLE 防護)**：
  - 標註建議之時間複雜度（如 $O(N)$）與空間複雜度。
  - 後端嚴格實施進程超時中斷，防止暴力硬爆解法。
- 🎓 **AI 程式導師 (Powered by Antigravity CLI)**：
  - **免 API Key**：直接調用本機 `agy` CLI，無需額外購買 OpenAI 或 Claude 額度。
  - **四維思維解析**：深入剖析「思維意圖剖析」、「亮點與優勢」、「邏輯盲點與 Debug」、「後續實現建議」。
  - **Session 對話管理**：支援多主題對話、封存歷史對話、切換與即時對話。
- 💾 **解法快照與即時存檔**：
  - 可儲存不同演算法版本（暴力法、雙指標優化版、位元運算法）。
  - 輸入 600ms 自動保存至 LocalStorage，重整網頁程式碼不丟失。
- 🎨 **Cursor 風格深色炭黑 UI**：
  - 溫潤深色工作台（非全黑刺眼，無多餘花俏色彩）。
  - 左右欄位均可自由拖曳調整寬度。
  - 完整支援 **Marked.js** Markdown 排版與 **KaTeX** 數學公式渲染（支援 $O(N \log N)$、$837799$ 等公式）。
  - 極簡 FontAwesome 線條圖示，嚴格零 Emoji。

---

## 🛠️ 環境需求與相依套件

在啟動前，請確認你的電腦已具備以下基本環境：

| 工具 | 必備程度 | 建議版本 | 說明 |
|---|---|---|---|
| **Python** | **必備** | 3.10 或以上 | 運行本地輕量評測伺服器 (`server.py`) |
| **GCC (MinGW)** | **必備** | MinGW-w64 (GCC 10+) | 用於在本地編譯與執行 C 語言程式碼 |
| **Google Antigravity (`agy`)** | *選配 (AI導師專用)* | 最新版 | 提供免 API Key 的 AI 程式導師分析功能 |

> 💡 **重要說明**：如果你的電腦**沒有安裝或未登入** Antigravity CLI，**所有的程式編寫、GCC 編譯、多測資評測、自訂測資執行、解法存檔功能依然 100% 正常運作！** 僅有「AI 導師思維診斷」按鈕會提示需要安裝或登入 `agy`。

---

## 🚀 快速上手教學

### 步驟 1：Clone 本專案
```bash
git clone https://github.com/D1349375/cpe-practice-arena.git
cd cpe-practice-arena
```

### 步驟 2：確認 GCC 與 Python 已加入環境變數
開啟終端機（PowerShell 或 CMD），輸入以下指令確認已安裝：
```bash
gcc --version
python --version
```
> 若提示找不到 `gcc`，可至 [WinLibs](https://winlibs.com/) 或透過 MSYS2 下載安裝 MinGW-w64，並將 `bin` 目錄加入 Windows 環境變數 `PATH`。

### 步驟 3：一鍵啟動！
在 Windows 下直接**雙擊**專案根目錄的：
```cmd
start.bat
```
或使用命令列執行：
```bash
python server.py
```
伺服器啟動後，會自動在預設瀏覽器開啟：  
👉 **`http://localhost:5050`**

---

## 🤖 AI 導師（Antigravity CLI）設定指南

平台上的 AI 程式導師是透過本地 Google Antigravity CLI (`agy`) 運作，因此**完全不需要設定任何 API Key**。

### 如何啟用 AI 導師？

1. **安裝 Google Antigravity**：
   - 請至 [Google Antigravity 官方網站](https://github.com/google/antigravity) 下載安裝 Antigravity。
2. **驗證 CLI 指令**：
   開啟終端機輸入：
   ```bash
   agy --version
   ```
   若能正常印出版本號，代表 CLI 工具已就緒。
3. **完成帳號登入**：
   若尚未登入，請在終端機執行一次性登入：
   ```bash
   agy auth login
   ```
   完成瀏覽器授權後即可正常調用。

### 遇到 AI 導師無法回應或報錯？
- **未安裝 `agy`**：平台會顯示「【導師提示】調用 agy 發生錯誤」，其餘程式碼評測與練習功能完全不受影響。
- **未登入 `agy`**：執行 `agy auth login` 或先啟動一次 Antigravity 應用程式即可恢復正常。
- **超時處理**：後端預設設有 90 秒保護機制，若網路不穩導致思考超時，可點擊「再次發問」。

---

## 📂 專案檔案結構

```
cpe-practice-arena/
├── index.html          # 單頁響應式 IDE 前端 (TailwindCSS + KaTeX + Marked.js)
├── server.py           # 本地評測伺服器 (GCC 進程調度、多測資驗證、agy 串接)
├── problems.json       # 精選題庫（含題目敘述、I/O規格、多測資、陷阱提示、標準解法）
├── setup_problems.py   # 題庫生成與批次擴充腳本
├── start.bat           # Windows 一鍵啟動批次檔
├── test.bat            # 快速本地 GCC 測試腳本
├── .gitignore          # Git 忽略評測產物與執行檔設定
└── README.md           # 專案詳細說明與啟動指引
```

---

## 💡 CPE 一顆星常考題型覆蓋

本練習場目前收錄了 CPE 最常考的經典 1 顆星題目：
- **基礎數論與模擬**：UVa 100 (3n+1)、UVa 10035 (進位)、UVa 10055 (戰士差值)、UVa 10071 (物理位移) 等
- **排序與中位數**：UVa 10041 (Vito's Family)、UVa 299 (Train Swapping) 等
- **字串解析與頻率**：UVa 272 (TeX Quotes)、UVa 10222 (Decode the Mad man)、UVa 10008 (What's Cryptanalysis) 等
- **大數與進制轉換**：UVa 10018 (Reverse and Add)、UVa 10101 (Bangla Numbers) 等
- **二維陣列與模擬**：UVa 10189 (Minesweeper) 等

---

## 📄 開源授權

本專案採用 [MIT License](LICENSE) 授權。歡迎自由 Fork、學習與貢獻！
