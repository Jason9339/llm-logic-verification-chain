#!/usr/bin/env python3
"""
Groq API 簡潔測試程式
測試可用模型的連接和功能
"""

import os
import asyncio
import aisuite as ai

# 設置API密鑰
os.environ['GROQ_API_KEY'] = "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"

async def test_basic_connection():
    """測試基本API連接"""
    print("測試基本連接...")
    
    try:
        client = ai.Client()
        response = client.chat.completions.create(
            model="groq:llama3-70b-8192",
            messages=[{"role": "user", "content": "回答：1+1=?"}],
            max_tokens=50
        )
        print(f"連接成功: {response.choices[0].message.content.strip()}")
        return True
    except Exception as e:
        print(f"連接失敗: {e}")
        return False

async def test_available_models():
    """測試可用模型"""
    print("\n測試可用模型...")
    
    models = [
        "groq:llama3-70b-8192",
        "groq:llama-3.3-70b-versatile"
    ]
    
    client = ai.Client()
    working_models = []
    
    for model in models:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "說一個字"}],
                max_tokens=10
            )
            print(f"  {model}: 可用")
            working_models.append(model)
        except Exception as e:
            print(f"  {model}: 失敗 - {str(e)[:50]}...")
        
        await asyncio.sleep(1)  # 避免速率限制
    
    return working_models

async def test_logic_reasoning():
    """測試邏輯推理"""
    print("\n測試邏輯推理...")
    
    question = """小明說："如果今天下雨，我就不去公園。"
今天小明去了公園。請問今天是否下雨？
請用JSON格式回答：{"answer": "你的答案", "reasoning": "推理過程"}"""
    
    try:
        client = ai.Client()
        response = client.chat.completions.create(
            model="groq:llama3-70b-8192",
            messages=[
                {"role": "system", "content": "你是邏輯推理專家，請用中文回答。"},
                {"role": "user", "content": question}
            ],
            max_tokens=200
        )
        
        result = response.choices[0].message.content.strip()
        print(f"推理結果: {result}")
        return True
        
    except Exception as e:
        print(f"推理測試失敗: {e}")
        return False

async def test_system_integration():
    """測試系統整合"""
    print("\n測試系統整合...")
    
    try:
        from llm_client import LLMClient
        
        llm_client = LLMClient()
        result = await llm_client.call_model(
            'groq/llama-3-70b-8192',
            '簡單回答：2+2=?'
        )
        
        if result['success']:
            print(f"系統整合成功: {result['response'][:50]}...")
            return True
        else:
            print(f"系統整合失敗: {result['error']}")
            return False
            
    except Exception as e:
        print(f"系統整合錯誤: {e}")
        return False

async def main():
    """主測試函數"""
    print("=" * 50)
    print("Groq API 測試程式")
    print("=" * 50)
    
    tests = [
        ("基本連接", test_basic_connection),
        ("可用模型", test_available_models),
        ("邏輯推理", test_logic_reasoning),
        ("系統整合", test_system_integration)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        try:
            result = await test_func()
            if result:
                passed += 1
                print(f"{test_name}: 通過")
            else:
                print(f"{test_name}: 失敗")
        except Exception as e:
            print(f"{test_name}: 錯誤 - {e}")
    
    print(f"\n測試結果: {passed}/{len(tests)} 通過")
    
    if passed == len(tests):
        print("所有測試通過，系統準備就緒")
        print("\n下一步操作:")
        print("  python main.py --question \"你的問題\"")
        print("  python main.py --file \"2星題目/2星_1.txt\"")
    else:
        print("部分測試失敗，請檢查配置")

if __name__ == "__main__":
    asyncio.run(main()) 