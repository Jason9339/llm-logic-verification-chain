#!/usr/bin/env python3
"""
多層次LLM邏輯題驗證系統 - aisuite版本測試腳本
測試aisuite統一接口的功能
"""
import asyncio
import os
from colorama import init, Fore, Style

# 初始化colorama
init()

from config import Config
from llm_client import LLMClient


def test_aisuite_setup():
    """測試aisuite設置"""
    print(f"{Fore.CYAN}🔧 測試aisuite設置...{Style.RESET_ALL}")
    
    try:
        import aisuite as ai
        print(f"{Fore.GREEN}✅ aisuite模組載入成功{Style.RESET_ALL}")
        
        client = ai.Client()
        print(f"{Fore.GREEN}✅ aisuite客戶端創建成功{Style.RESET_ALL}")
        
        return True
    except ImportError:
        print(f"{Fore.RED}❌ aisuite模組未安裝{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}請運行: pip install aisuite{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}❌ aisuite設置失敗: {str(e)}{Style.RESET_ALL}")
        return False


def test_api_keys():
    """測試API密鑰配置"""
    print(f"{Fore.CYAN}🔑 測試API密鑰配置...{Style.RESET_ALL}")
    
    config = Config()
    
    # 檢查各個API密鑰
    api_keys = {
        'OpenAI': config.OPENAI_API_KEY,
        'Anthropic': config.ANTHROPIC_API_KEY,
        'Google': config.GOOGLE_API_KEY,
        'Groq': config.GROQ_API_KEY,
        'OpenRouter (備用)': config.OPENROUTER_API_KEY
    }
    
    available_apis = []
    for name, key in api_keys.items():
        if key and key != 'your_*_api_key_here':
            available_apis.append(name)
            print(f"{Fore.GREEN}✅ {name} API密鑰已配置{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  {name} API密鑰未配置{Style.RESET_ALL}")
    
    if not available_apis:
        print(f"{Fore.RED}❌ 沒有配置任何API密鑰{Style.RESET_ALL}")
        return False
    
    print(f"{Fore.GREEN}✅ 共有 {len(available_apis)} 個API可用{Style.RESET_ALL}")
    return True


async def test_model_connection():
    """測試模型連接"""
    print(f"{Fore.CYAN}🤖 測試模型連接...{Style.RESET_ALL}")
    
    llm_client = LLMClient()
    config = Config()
    
    # 測試順序：優先測試便宜和免費的模型
    test_models = [
        'openai/gpt-4o-mini',
        'google/gemini-flash', 
        'groq/llama-3-70b',
        'openai/gpt-4o',
        'anthropic/claude-3-5-sonnet'
    ]
    
    successful_models = []
    
    for model_key in test_models:
        if config.is_model_available(model_key):
            print(f"{Fore.BLUE}測試模型: {model_key}{Style.RESET_ALL}")
            
            try:
                result = await llm_client.call_model(
                    model_key, 
                    "請回答：1+1等於多少？"
                )
                
                if result['success']:
                    print(f"{Fore.GREEN}✅ {model_key} 連接成功{Style.RESET_ALL}")
                    print(f"   回應: {result['response'][:50]}...")
                    successful_models.append(model_key)
                else:
                    print(f"{Fore.RED}❌ {model_key} 連接失敗: {result['error']}{Style.RESET_ALL}")
                
                # 短暫延遲避免速率限制
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"{Fore.RED}❌ {model_key} 測試出錯: {str(e)}{Style.RESET_ALL}")
    
    if successful_models:
        print(f"{Fore.GREEN}✅ 共有 {len(successful_models)} 個模型可用{Style.RESET_ALL}")
        return True
    else:
        print(f"{Fore.RED}❌ 沒有可用的模型{Style.RESET_ALL}")
        return False


async def test_simple_logic():
    """測試簡單邏輯推理"""
    print(f"{Fore.CYAN}🧠 測試邏輯推理功能...{Style.RESET_ALL}")
    
    test_question = """
小明說："如果今天下雨，我就不去公園。"
今天小明去了公園。
請問今天是否下雨？請用JSON格式回答，包含reasoning和answer字段。
"""
    
    try:
        from system_coordinator import SystemCoordinator
        system = SystemCoordinator()
        
        result = await system.process_question(
            test_question.strip(),
            verbose=False
        )
        
        if result['summary']['overall_success']:
            print(f"{Fore.GREEN}✅ 邏輯推理測試成功{Style.RESET_ALL}")
            decision = result['layer_results']['decision']
            print(f"{Fore.BLUE}📋 最終答案: {decision['final_answer']}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}📊 信心程度: {decision['answer_confidence']:.2%}{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.RED}❌ 邏輯推理測試失敗{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}❌ 邏輯推理測試出錯: {str(e)}{Style.RESET_ALL}")
        return False


def print_usage_guide():
    """打印使用指南"""
    print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}🚀 aisuite版本使用指南{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}📋 推薦配置（大規模實驗）:{Style.RESET_ALL}")
    print(f"1. {Fore.GREEN}OpenAI gpt-4o-mini{Style.RESET_ALL} - 成本效益最佳")
    print(f"2. {Fore.GREEN}OpenAI gpt-4o{Style.RESET_ALL} - 質量最高")
    print(f"3. {Fore.GREEN}Google Gemini{Style.RESET_ALL} - 免費額度大")
    print(f"4. {Fore.GREEN}Anthropic Claude{Style.RESET_ALL} - 邏輯推理強")
    
    print(f"\n{Fore.CYAN}💰 成本優化建議:{Style.RESET_ALL}")
    print(f"• 日常測試: gpt-4o-mini ($0.15/1M tokens)")
    print(f"• 重要實驗: gpt-4o ($2.5/1M tokens)")
    print(f"• 邏輯推理: claude-3.5-sonnet")
    print(f"• 快速驗證: Google Gemini (免費)")
    
    print(f"\n{Fore.CYAN}🎯 使用命令:{Style.RESET_ALL}")
    print(f"• 單題測試: python main.py --question \"你的問題\" --verbose")
    print(f"• 批量處理: python main.py --batch --verbose")
    print(f"• 檔案處理: python main.py --file \"2星題目/2星_1.txt\"")
    
    print(f"\n{Fore.CYAN}⚙️  性能調優:{Style.RESET_ALL}")
    print(f"• 並行處理: 修改config.py中的模型列表")
    print(f"• 速度優先: 使用Groq模型")
    print(f"• 質量優先: 使用OpenAI gpt-4o")


async def main():
    """主測試函數"""
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}🧪 多層次LLM邏輯驗證系統 - aisuite版本測試{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")
    
    tests = [
        ("aisuite設置測試", test_aisuite_setup),
        ("API密鑰配置測試", test_api_keys),
        ("模型連接測試", test_model_connection),
        ("邏輯推理功能測試", test_simple_logic)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"{Fore.YELLOW}🔍 開始{test_name}...{Style.RESET_ALL}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                success = await test_func()
            else:
                success = test_func()
            
            if success:
                passed += 1
                print(f"{Fore.GREEN}✅ {test_name}通過{Style.RESET_ALL}\n")
            else:
                print(f"{Fore.RED}❌ {test_name}失敗{Style.RESET_ALL}\n")
        
        except Exception as e:
            print(f"{Fore.RED}❌ {test_name}過程中發生錯誤: {str(e)}{Style.RESET_ALL}\n")
    
    # 總結
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}📊 測試結果摘要{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    
    if passed == total:
        print(f"{Fore.GREEN}🎉 所有測試通過！({passed}/{total}){Style.RESET_ALL}")
        print(f"{Fore.GREEN}aisuite版本已準備就緒，可以開始大規模實驗。{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  部分測試未通過 ({passed}/{total}){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}請檢查失敗的測試項目並修復相關問題。{Style.RESET_ALL}")
    
    print_usage_guide()


if __name__ == "__main__":
    asyncio.run(main()) 