import http.server
import socketserver
import json
import urllib.parse
import subprocess
import os
import time
import sys

PORT = 5050
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROBLEMS_FILE = os.path.join(BASE_DIR, "problems.json")
MAX_CODE_SIZE = 500_000  # 500KB POST body guard

# Module-level problems cache to avoid disk I/O on every request
_PROBLEMS_CACHE = None

def load_problems():
    global _PROBLEMS_CACHE
    if _PROBLEMS_CACHE is not None:
        return _PROBLEMS_CACHE
    if os.path.exists(PROBLEMS_FILE):
        with open(PROBLEMS_FILE, "r", encoding="utf-8") as f:
            _PROBLEMS_CACHE = json.load(f)
            return _PROBLEMS_CACHE
    return []


def normalize_output(text):
    if not text:
        return ""
    lines = text.replace("\r\n", "\n").split("\n")
    lines = [line.rstrip() for line in lines]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)

def call_agy_agent(prompt):
    """Invokes Antigravity CLI (agy) without needing external API keys.
    C1 FIX: Do NOT use text=True/encoding/errors — capture raw bytes and decode
    manually. agy on Windows may output Big5/cp950; try utf-8 first, fallback to cp950.
    """
    try:
        res = subprocess.run(
            ["agy", "--model", "gemini-3.8-flash-low", "--disable-slash-commands", "-p", prompt],
            capture_output=True,
            timeout=90.0
        )
        if res.returncode == 0 and res.stdout.strip():
            try:
                output = res.stdout.decode("utf-8")
            except UnicodeDecodeError:
                output = res.stdout.decode("cp950", errors="replace")
            return output.strip()
        else:
            try:
                err = res.stderr.decode("utf-8").strip() if res.stderr else "CLI 沒有傳回輸出"
            except UnicodeDecodeError:
                err = res.stderr.decode("cp950", errors="replace").strip() if res.stderr else "CLI 沒有傳回輸出"
            return f"【導師提示】agy 執行異常：{err}"
    except subprocess.TimeoutExpired:
        return "【導師提示】思考逾時，請稍後再試或縮短問題範圍。"
    except Exception as e:
        return f"【導師提示】調用 agy 發生錯誤：{str(e)}"

class CPERequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/problems":
            problems = load_problems()
            summary = [
                {
                    "id": p["id"],
                    "uvaId": p.get("uvaId", ""),
                    "title": p["title"],
                    "category": p["category"],
                    "difficulty": p["difficulty"]
                }
                for p in problems
            ]
            self.send_json_response(200, summary)
            return

        elif parsed.path == "/api/problem":
            query = urllib.parse.parse_qs(parsed.query)
            pid = query.get("id", [""])[0]
            problems = load_problems()
            for p in problems:
                if str(p["id"]) == pid:
                    self.send_json_response(200, p)
                    return
            self.send_json_response(404, {"error": "Problem not found"})
            return

        elif parsed.path == "/" or parsed.path == "/index.html":
            self.path = "/index.html"
            return super().do_GET()

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))

        # W2 FIX: Reject oversized POST bodies to prevent memory exhaustion
        if content_length > MAX_CODE_SIZE:
            self.send_json_response(413, {"error": f"Request body too large (max {MAX_CODE_SIZE // 1000}KB)"})
            self.rfile.read(content_length)
            return

        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data.decode("utf-8"))
        except Exception:
            data = {}

        if parsed.path == "/api/judge":
            pid = data.get("id", "")
            code = data.get("code", "")
            custom_input = data.get("customInput", None)

            problems = load_problems()
            target_prob = next((p for p in problems if str(p["id"]) == str(pid)), None)

            if not target_prob and custom_input is None:
                self.send_json_response(400, {"verdict": "ERROR", "message": "Unknown problem ID"})
                return

            judge_input = custom_input if custom_input is not None else target_prob.get("sampleInput", "")
            expected_output = target_prob.get("sampleOutput", "") if target_prob else ""

            temp_c = os.path.join(BASE_DIR, "solution_temp.c")
            temp_exe = os.path.join(BASE_DIR, "solution_temp.exe")

            with open(temp_c, "w", encoding="utf-8") as f:
                f.write(code)

            # Auto sync to solution.c
            sol_c = os.path.join(BASE_DIR, "solution.c")
            try:
                with open(sol_c, "w", encoding="utf-8") as f:
                    f.write(code)
            except Exception:
                pass

            # 1. Compile with GCC (W1 FIX: add timeout=30 to prevent GCC hang)
            try:
                compile_res = subprocess.run(
                    ["gcc", "-O2", "-Wall", temp_c, "-o", temp_exe, "-lm"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=30
                )
            except subprocess.TimeoutExpired:
                self.send_json_response(200, {
                    "verdict": "CE",
                    "title": "Compilation Timeout",
                    "message": "GCC 編譯超過 30 秒，程式碼可能包含異常結構（如超大模板展開），請簡化程式碼。"
                })
                return

            if compile_res.returncode != 0:
                self.send_json_response(200, {
                    "verdict": "CE",
                    "title": "Compilation Error (編譯錯誤)",
                    "message": compile_res.stderr or "GCC Compilation Failed"
                })
                return

            # 2. Run Execution (Custom Input or Multi-case Evaluation)
            time_limit = float(target_prob.get("timeLimit", 3.0)) if target_prob else 3.0

            if custom_input is not None:
                # Custom input execution mode
                try:
                    start_run = time.time()
                    run_res = subprocess.run(
                        [temp_exe],
                        input=custom_input,
                        capture_output=True,
                        text=True,
                        timeout=time_limit,
                        encoding="utf-8",
                        errors="replace"
                    )
                    elapsed_ms = int((time.time() - start_run) * 1000)
                except subprocess.TimeoutExpired:
                    self.send_json_response(200, {
                        "verdict": "TLE",
                        "title": f"Time Limit Exceeded (執行逾時 > {time_limit}s)",
                        "message": f"程式執行超過限制時間 {time_limit} 秒，請檢查是否存在無窮迴圈或需優化時間複雜度。"
                    })
                    return
                except Exception as e:
                    self.send_json_response(200, {
                        "verdict": "RE",
                        "title": "Runtime Error",
                        "message": str(e)
                    })
                    return

                if run_res.returncode != 0:
                    self.send_json_response(200, {
                        "verdict": "RE",
                        "title": f"Runtime Error (Exit Code: {run_res.returncode})",
                        "message": run_res.stderr or "程式異常終止（記憶體越界 / 核心傾印）"
                    })
                    return

                self.send_json_response(200, {
                    "verdict": "DONE",
                    "title": "自訂測資執行完成",
                    "actualOutput": run_res.stdout,
                    "timeMs": elapsed_ms
                })
                return

            # Multi-case Comprehensive Testing
            raw_test_cases = target_prob.get("testCases", []) if target_prob else []
            if not raw_test_cases:
                raw_test_cases = [{
                    "id": 1,
                    "name": "範例測資 1",
                    "input": target_prob.get("sampleInput", ""),
                    "expected": target_prob.get("sampleOutput", "")
                }]

            case_results = []
            passed_count = 0
            overall_verdict = "AC"
            max_elapsed_ms = 0

            for tc in raw_test_cases:
                tc_id = tc.get("id", 1)
                tc_name = tc.get("name", f"測資 {tc_id}")
                tc_input = tc.get("input", "")
                tc_expected = tc.get("expected", "")

                try:
                    t_start = time.time()
                    run_res = subprocess.run(
                        [temp_exe],
                        input=tc_input,
                        capture_output=True,
                        text=True,
                        timeout=time_limit,
                        encoding="utf-8",
                        errors="replace"
                    )
                    t_ms = int((time.time() - t_start) * 1000)
                    if t_ms > max_elapsed_ms:
                        max_elapsed_ms = t_ms
                except subprocess.TimeoutExpired:
                    case_results.append({
                        "id": tc_id,
                        "name": tc_name,
                        "verdict": "TLE",
                        "timeMs": int(time_limit * 1000),
                        "input": tc_input,
                        "actualOutput": "(執行逾時)",
                        "expectedOutput": tc_expected,
                        "message": f"執行超過限時 {time_limit} 秒！"
                    })
                    overall_verdict = "TLE"
                    break
                except Exception as e:
                    case_results.append({
                        "id": tc_id,
                        "name": tc_name,
                        "verdict": "RE",
                        "timeMs": 0,
                        "input": tc_input,
                        "actualOutput": str(e),
                        "expectedOutput": tc_expected,
                        "message": str(e)
                    })
                    overall_verdict = "RE"
                    break

                if run_res.returncode != 0:
                    case_results.append({
                        "id": tc_id,
                        "name": tc_name,
                        "verdict": "RE",
                        "timeMs": t_ms,
                        "input": tc_input,
                        "actualOutput": run_res.stdout,
                        "expectedOutput": tc_expected,
                        "message": run_res.stderr or f"Exit Code {run_res.returncode}"
                    })
                    overall_verdict = "RE"
                    break

                actual_out = run_res.stdout
                norm_act = normalize_output(actual_out)
                norm_exp = normalize_output(tc_expected)

                if norm_act == norm_exp:
                    passed_count += 1
                    case_results.append({
                        "id": tc_id,
                        "name": tc_name,
                        "verdict": "AC",
                        "timeMs": t_ms,
                        "input": tc_input,
                        "actualOutput": actual_out,
                        "expectedOutput": tc_expected
                    })
                else:
                    case_results.append({
                        "id": tc_id,
                        "name": tc_name,
                        "verdict": "WA",
                        "timeMs": t_ms,
                        "input": tc_input,
                        "actualOutput": actual_out,
                        "expectedOutput": tc_expected
                    })
                    if overall_verdict == "AC":
                        overall_verdict = "WA"

            total_cases = len(raw_test_cases)
            failed_case = next((c for c in case_results if c["verdict"] != "AC"), None)
            first_case = case_results[0] if case_results else {}

            self.send_json_response(200, {
                "verdict": overall_verdict,
                "title": f"Accepted ({passed_count}/{total_cases} 測資全數通過)" if overall_verdict == "AC" else f"{overall_verdict} ({passed_count}/{total_cases} 通過)",
                "totalCases": total_cases,
                "passedCases": passed_count,
                "timeMs": max_elapsed_ms,
                "timeLimit": time_limit,
                "cases": case_results,
                "actualOutput": failed_case["actualOutput"] if failed_case else first_case.get("actualOutput", ""),
                "expectedOutput": failed_case["expectedOutput"] if failed_case else first_case.get("expectedOutput", "")
            })
            return

        elif parsed.path == "/api/agent/analyze":
            pid = data.get("problemId", "")
            code = data.get("code", "")
            verdict = data.get("verdict", "未評測")
            actual_output = data.get("actualOutput", "")
            expected_output = data.get("expectedOutput", "")
            message = data.get("message", "")

            problems = load_problems()
            target_prob = next((p for p in problems if str(p["id"]) == str(pid)), None)
            prob_title = target_prob.get("title", f"題目 {pid}") if target_prob else f"題目 {pid}"
            prob_desc = target_prob.get("description", "") if target_prob else ""
            prob_hint = target_prob.get("hint", "") if target_prob else ""

            mentor_prompt = f"""你是一位專業、敏銳且富有教學熱忱的 C 語言程式競賽導師（專精 CPE 大學程式能力檢定）。
學生的目標是藉由你的引導，真正理解問題與自己的思考邏輯，並提升 C 語言解題手感。

【當前題目資訊】：
題號與名稱：{prob_title} (UVA {target_prob.get('uvaId', '') if target_prob else ''})
題目背景簡介：{prob_desc[:300]}
解題陷阱與考點：{prob_hint[:300]}

【學生目前撰寫的 C 語言程式碼】：
```c
{code}
```

【評測系統執行狀態】：
評測結果 (Verdict)：{verdict}
輸出或日誌：
{actual_output[:500] if actual_output else message[:500]}
預期輸出：
{expected_output[:300]}

請依據以下四個核心維度為學生進行精準、犀利且言簡意賅的剖析（請用繁體中文，總字數控制在 350-500 字內直切關鍵，請勿使用 Emoji 表情符號，使用簡潔的 Markdown 標題）：

### 一、 思維意圖剖析（你為什麼會這樣想）
- 站在學生的角度，分析他採取這套寫法的出發點是什麼（例如：直覺單純模擬、以特定變數控制狀態、使用指標或迴圈結構等）。
- 說明他這條邏輯路徑在直覺上是合理的。

### 二、 思維亮點與優勢（肯定做得好的部分）
- 真誠指出他在思維或程式碼結構上的優點（例如：有捕捉到輸入規格、邊界嘗試、語法結構整潔等），給予積極肯定。

### 三、 邏輯盲點與除錯診斷（Debug 分析）
- 若評測結果為 WA：具體分析是哪種測試邊界沒顧到（例如：i > j 未交換、負數餘數問題、EOF 處理、型別溢位等）。
- 若評測結果為 CE：具體指出 GCC 報錯在哪一行，以及 C 語言語法的核心規則。
- 若評測結果為 AC：肯定其正確性，並點評時間/空間複雜度是否有優化空間。

### 四、 後續實現與改進建議（如何落實你的思維）
- 依據他原本的思路給出具體的修改方向與引導，幫助他自己動手改出正確答案。
"""
            reply = call_agy_agent(mentor_prompt)
            self.send_json_response(200, {"status": "ok", "reply": reply})
            return

        elif parsed.path == "/api/agent/chat":
            pid = data.get("problemId", "")
            code = data.get("code", "")
            verdict = data.get("verdict", "")
            user_msg = data.get("message", "")
            history = data.get("history", [])

            problems = load_problems()
            target_prob = next((p for p in problems if str(p["id"]) == str(pid)), None)
            prob_title = target_prob.get("title", f"題目 {pid}") if target_prob else f"題目 {pid}"

            # Format previous history
            history_text = ""
            if history:
                for item in history[-6:]: # keep last 6 turns
                    role = "學生" if item.get("role") == "user" else "導師"
                    history_text += f"{role}: {item.get('content', '')}\n"

            chat_prompt = f"""你是一位專業且極具啟發性的 C 語言演算法程式導師（專精 CPE 檢定）。
你正在與學生一對一對話，回答學生關於程式邏輯、Debug 或 C 語言寫法的問題。
請以親切、專業、循序漸進的語氣回答（使用繁體中文）。如果學生問程式碼問題，請不要只是丟給他整份答案，而是引導他思考或指出關鍵關鍵行。

【當前題目】：{prob_title}
【學生目前的 C 程式碼】：
```c
{code}
```
【評測狀態】：{verdict}

【先前的對話歷史】：
{history_text}

【學生當前提問】：
{user_msg}
"""
            reply = call_agy_agent(chat_prompt)
            self.send_json_response(200, {"status": "ok", "reply": reply})
            return

        elif parsed.path == "/api/sync":
            code = data.get("code", "")
            input_text = data.get("input", "")
            exp_text = data.get("expected", "")

            with open(os.path.join(BASE_DIR, "solution.c"), "w", encoding="utf-8") as f:
                f.write(code)
            with open(os.path.join(BASE_DIR, "input.txt"), "w", encoding="utf-8") as f:
                f.write(input_text)
            with open(os.path.join(BASE_DIR, "expected.txt"), "w", encoding="utf-8") as f:
                f.write(exp_text)

            self.send_json_response(200, {"status": "ok", "message": "Synced to solution.c and input.txt"})
            return

        self.send_json_response(404, {"error": "Not found"})

    def send_json_response(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    print(f"==================================================")
    print(f" CPE C 語言練習場 + AI 程式導師 (agy) 已啟動！")
    print(f" 瀏覽器網址: http://localhost:{PORT}")
    print(f"==================================================")
    with socketserver.TCPServer(("", PORT), CPERequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n伺服器已關閉。")
