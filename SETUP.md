# 快速安裝和設置指南

## 📦 安裝步驟

### 1. 安裝Python依賴
```bash
pip install -r requirements.txt
```

### 2. 配置API密鑰
```bash
# 複製環境變量範例
cp env_example.txt .env

# 編輯.env文件，添加至少一個API密鑰
# 推薦使用免費的Google Gemini或Groq
```

### 3. 測試系統
```bash
python test_system.py
```

## 🔑 推薦的免費API獲取

### Google Gemini (推薦)
1. 訪問 https://ai.google.dev/
2. 點擊 "Get API key"
3. 創建新項目或選擇現有項目
4. 生成API密鑰
5. 在.env中設置：`GOOGLE_API_KEY=your_api_key_here`

### Groq (推薦)
1. 訪問 https://console.groq.com/
2. 註冊並登錄
3. 在API Keys頁面生成新密鑰
4. 在.env中設置：`GROQ_API_KEY=your_api_key_here`

### 其他選項
- **OpenAI**: 新用戶有$5免費額度
- **Anthropic**: 新用戶有$5免費額度
- **Cohere**: 每月1000次免費請求

## 🚀 快速開始

### 處理單個題目
```bash
python main.py --file "2星題目/2星_1.txt" --verbose
```

### 批量處理所有題目
```bash
python main.py --batch --verbose
```

### 自定義題目
```bash
python main.py --question "你的邏輯題目" --verbose
```

### 指定模型
```bash
python main.py --file "題目.txt" --models google/gemini-pro groq/mixtral-8x7b
```

## 📁 重要文件說明

- `main.py` - 主程序入口
- `config.py` - 系統配置
- `prompts/` - 各層prompt模板（可自由修改）
- `results/` - 處理結果輸出目錄
- `2星題目/` - 邏輯題目文件

## 🛠️ 自定義Prompt

修改 `prompts/` 目錄中的文件來調整各層的行為：
- `answering_layer.txt` - 作答層提示
- `verification_layer.txt` - 驗證層提示
- `correction_layer.txt` - 訂正層提示
- `decision_layer.txt` - 決策層提示

## 🆘 常見問題

**Q: API密鑰錯誤**
A: 檢查.env文件格式，確認密鑰有效

**Q: 沒有題目文件**
A: 確認 `2星題目/` 目錄中有.txt文件

**Q: 處理速度慢**
A: 使用Groq模型（速度最快）

**Q: JSON解析錯誤**
A: 檢查prompt模板格式，嘗試不同模型

## 📊 查看結果

處理結果保存在 `results/` 目錄：
- 單次處理：`result_YYYYMMDD_HHMMSS.json`
- 批量處理：`batch_summary_YYYYMMDD_HHMMSS.json`

使用 `--verbose` 參數可在命令行直接查看詳細結果。 