# 多層次大型語言模型邏輯題驗證與訂正系統

一個基於多個LLM協作的邏輯推理驗證系統，通過四層架構提升邏輯題解答的可靠性和準確性。

## 🎯 系統特色

- **四層協作架構**：作答→驗證→訂正→決策，層層把關
- **多模型支持**：支持OpenAI、Anthropic、Google Gemini、Groq等多個LLM提供商
- **免費方案友好**：優先推薦免費LLM服務，降低使用成本
- **模組化設計**：每層prompt獨立，便於修改和優化
- **批量處理**：支持單題處理和批量處理
- **詳細日誌**：完整記錄每層的推理過程和結果

## 🏗️ 系統架構

### 第一層：作答層 (Answering Layer)
- **角色**：模擬學生作答
- **功能**：多個LLM對同一題目給出獨立答案
- **輸出**：包含推理過程、答案和信心程度的JSON格式

### 第二層：驗證層 (Verification Layer)  
- **角色**：模擬教師批改
- **功能**：交叉驗證其他模型的答案，指出邏輯錯誤
- **特點**：只驗證不提供正確答案，避免偏見

### 第三層：訂正層 (Correction Layer)
- **角色**：模擬學生根據批改修正錯誤
- **功能**：基於驗證層回饋重新推理和修正答案
- **輸出**：修正後的推理過程和答案

### 第四層：最終決策層 (Decision Layer)
- **角色**：資深專家綜合決策
- **功能**：整合所有信息，做出最終判斷
- **考量**：邏輯嚴謹性、一致性、置信度等多維度

## 🚀 快速開始

### 1. 環境配置

```bash
# 克隆項目
git clone <your-repo-url>
cd "NLP final project"

# 安裝依賴
pip install -r requirements.txt

# 配置API密鑰
cp env_example.txt .env
# 編輯.env文件，填入至少一個LLM的API密鑰
```

### 2. 推薦的免費LLM服務

| 服務商 | 模型 | 免費額度 | 註冊連結 |
|--------|------|----------|----------|
| Google | Gemini Pro | 每天1500次請求 | https://ai.google.dev/ |
| Groq | Mixtral-8x7B | 每分鐘30次請求 | https://console.groq.com/ |
| Cohere | Command | 每月1000次請求 | https://cohere.ai/ |
| OpenAI | GPT-3.5/4 | 新用戶$5額度 | https://platform.openai.com/ |
| Anthropic | Claude 3 | 新用戶$5額度 | https://console.anthropic.com/ |

### 3. 基本使用

```bash
# 查看幫助
python main.py --help-system

# 處理單個題目文件
python main.py --file "2星題目/2星_1.txt" --verbose

# 批量處理所有題目
python main.py --batch --verbose

# 處理自定義題目
python main.py --question "某研討會上有誠實國和說謊國的學者..." --verbose

# 指定使用的模型
python main.py --file "2星題目/2星_1.txt" --models google/gemini-pro groq/mixtral-8x7b
```

## 📁 文件結構

```
NLP final project/
├── main.py                 # 主程序入口
├── config.py              # 系統配置
├── system_coordinator.py  # 系統協調器
├── llm_client.py          # 統一LLM客戶端
├── requirements.txt       # Python依賴
├── env_example.txt        # 環境變量範例
├── prompts/              # Prompt模板目錄
│   ├── answering_layer.txt
│   ├── verification_layer.txt  
│   ├── correction_layer.txt
│   └── decision_layer.txt
├── layers/               # 各層處理器
│   ├── __init__.py
│   ├── answering_layer.py
│   ├── verification_layer.py
│   ├── correction_layer.py
│   └── decision_layer.py
├── 2星題目/              # 題目文件
├── results/              # 結果輸出目錄
└── README.md
```

## ⚙️ 配置說明

### 模型配置
系統支持以下模型格式：
- `google/gemini-pro` - Google Gemini Pro
- `groq/mixtral-8x7b` - Groq Mixtral 8x7B  
- `groq/llama2-70b` - Groq LLaMA 2 70B
- `openai/gpt-3.5-turbo` - OpenAI GPT-3.5 Turbo
- `openai/gpt-4` - OpenAI GPT-4
- `anthropic/claude-3-haiku` - Anthropic Claude 3 Haiku

### Prompt自定義
每層的prompt模板位於`prompts/`目錄中，支持：
- 修改角色設定和指令
- 調整輸出格式要求
- 添加專業領域知識
- 優化推理引導邏輯

## 🔄 工作流程

1. **題目輸入**：從文件或命令行讀取邏輯題
2. **並行作答**：多個LLM同時分析和作答
3. **交叉驗證**：驗證模型檢查其他模型的推理
4. **錯誤訂正**：根據驗證回饋修正錯誤推理
5. **綜合決策**：整合所有信息得出最終答案
6. **結果保存**：保存完整的推理鏈和決策過程

## 📊 輸出格式

系統會生成詳細的JSON結果文件，包含：
- 每個模型的原始推理過程
- 驗證結果和錯誤分析
- 訂正後的推理過程  
- 最終決策和信心程度
- 處理時間和統計信息

## 🛠️ 自定義擴展

### 添加新的LLM提供商
1. 在`config.py`中添加模型配置
2. 在`llm_client.py`中實現API調用方法
3. 測試和驗證功能

### 修改處理邏輯
1. 編輯對應層級的處理器文件
2. 調整prompt模板
3. 測試修改效果

### 批量實驗
系統支持大規模批量處理，適合：
- 模型性能對比實驗
- Prompt工程優化
- 邏輯推理能力評估

## 🤝 貢獻指南

歡迎提交Issue和Pull Request來改進系統！

## 📄 授權條款

MIT License

## 🆘 故障排除

### 常見問題

1. **API密鑰錯誤**
   - 檢查.env文件是否正確配置
   - 確認API密鑰有效且有足夠額度

2. **模型不可用**
   - 檢查網絡連接
   - 確認選用的模型在配置中可用

3. **處理速度慢**
   - 考慮使用更快的模型（如Groq）
   - 調整timeout設置

4. **JSON解析錯誤**
   - 檢查prompt模板格式
   - 嘗試調整溫度參數

### 獲取幫助
- 查看系統內建幫助：`python main.py --help-system`
- 檢查results目錄中的詳細日誌
- 提交GitHub Issue描述問題
