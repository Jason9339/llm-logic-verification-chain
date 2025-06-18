#!/usr/bin/env python3
"""
多層次LLM邏輯題驗證系統 - 測試腳本
用於驗證系統功能和配置
"""
import asyncio
import os
from colorama import init, Fore, Style

# 初始化colorama
init()

from config import Config
from system_coordinator import SystemCoordinator

def test_config():
    """測試配置是否正確加載"""
    print(f"{Fore.CYAN}🔧 測試系統配置...{Style.RESET_ALL}")
    
    config = Config()
    
    # 檢查API密鑰（重點檢查OpenRouter）
    api_keys = {
        'OpenRouter': config.OPENROUTER_API_KEY,
        'OpenAI': config.OPENAI_API_KEY,
        'Anthropic': config.ANTHROPIC_API_KEY,
        'Google': config.GOOGLE_API_KEY,
        'Groq': config.GROQ_API_KEY,
        'Cohere': config.COHERE_API_KEY
    }
    
    available_keys = []
    for name, key in api_keys.items():
        if key and key != 'your_*_api_key_here':
            available_keys.append(name)
            print(f"{Fore.GREEN}✅ {name} API密鑰已配置{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️  {name} API密鑰未配置{Style.RESET_ALL}")
    
    if not config.OPENROUTER_API_KEY:
        print(f"{Fore.RED}❌ OpenRouter API密鑰未配置，系統無法正常運行{Style.RESET_ALL}")
        return False
    
    # 檢查默認模型配置
    print(f"\n{Fore.CYAN}🤖 檢查模型配置...{Style.RESET_ALL}")
    print(f"{Fore.BLUE}作答模型: {', '.join(config.DEFAULT_ANSWERING_MODELS)}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}驗證模型: {', '.join(config.DEFAULT_VERIFICATION_MODELS)}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}訂正模型: {config.DEFAULT_CORRECTION_MODEL}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}決策模型: {config.DEFAULT_DECISION_MODEL}{Style.RESET_ALL}")
    
    # 檢查目錄
    directories = {
        'Prompts': config.PROMPTS_DIR,
        'Questions': config.QUESTIONS_DIR,
        'Results': config.RESULTS_DIR
    }
    
    for name, path in directories.items():
        if os.path.exists(path):
            print(f"{Fore.GREEN}✅ {name}目錄存在: {path}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ {name}目錄不存在: {path}{Style.RESET_ALL}")
            return False
    
    # 檢查prompt文件
    prompt_files = [
        'answering_layer.txt',
        'verification_layer.txt',
        'correction_layer.txt',
        'decision_layer.txt'
    ]
    
    for prompt_file in prompt_files:
        path = os.path.join(config.PROMPTS_DIR, prompt_file)
        if os.path.exists(path):
            print(f"{Fore.GREEN}✅ Prompt文件存在: {prompt_file}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Prompt文件不存在: {prompt_file}{Style.RESET_ALL}")
            return False
    
    print(f"{Fore.GREEN}✅ 配置檢查完成{Style.RESET_ALL}\n")
    return True

def test_question_files():
    """測試題目文件"""
    print(f"{Fore.CYAN}📁 測試題目文件...{Style.RESET_ALL}")
    
    config = Config()
    question_files = []
    
    if os.path.exists(config.QUESTIONS_DIR):
        for file in os.listdir(config.QUESTIONS_DIR):
            if file.endswith('.txt'):
                question_files.append(file)
                print(f"{Fore.GREEN}✅ 找到題目文件: {file}{Style.RESET_ALL}")
    
    if not question_files:
        print(f"{Fore.YELLOW}⚠️  沒有找到題目文件{Style.RESET_ALL}")
        return False
    
    print(f"{Fore.GREEN}✅ 總共找到 {len(question_files)} 個題目文件{Style.RESET_ALL}\n")
    return True

async def test_simple_question():
    """測試簡單的邏輯問題"""
    print(f"{Fore.CYAN}🧠 測試簡單邏輯問題...{Style.RESET_ALL}")
    
    test_question = """
小明說："如果今天下雨，我就不去公園。"
今天小明去了公園。
請問今天是否下雨？
"""
    
    try:
        system = SystemCoordinator()
        
        # 首先嘗試使用默認配置
        try:
            result = await system.process_question(
                test_question.strip(),
                verbose=False
            )
            
            if result['summary']['overall_success']:
                print(f"{Fore.GREEN}✅ 系統測試成功{Style.RESET_ALL}")
                decision = result['layer_results']['decision']
                print(f"{Fore.BLUE}📋 最終答案: {decision['final_answer']}{Style.RESET_ALL}")
                print(f"{Fore.BLUE}📊 信心程度: {decision['answer_confidence']:.2%}{Style.RESET_ALL}")
                print(f"{Fore.BLUE}🤝 驗證共識度: {decision['verification_consensus']['consensus_rate']:.2%}{Style.RESET_ALL}")
                return True
            else:
                print(f"{Fore.RED}❌ 系統測試失敗{Style.RESET_ALL}")
                if 'error' in result['layer_results']['decision']:
                    print(f"{Fore.RED}錯誤: {result['layer_results']['decision']['error']}{Style.RESET_ALL}")
                return False
                
        except Exception as e:
            error_str = str(e)
            if "free-models-per-day" in error_str:
                print(f"{Fore.YELLOW}⚠️  遇到每日免費額度限制，嘗試單模型測試...{Style.RESET_ALL}")
                
                # 嘗試單模型測試
                from layers.answering_layer import AnsweringLayer
                answering_layer = AnsweringLayer()
                
                # 只測試一個模型的基本功能
                single_model_result = await answering_layer.process_question(
                    test_question.strip(),
                    models=['openrouter/deepseek-r1']  # 只使用一個模型
                )
                
                if single_model_result and len(single_model_result) > 0 and single_model_result[0]['success']:
                    print(f"{Fore.GREEN}✅ 單模型基本功能測試成功{Style.RESET_ALL}")
                    print(f"{Fore.BLUE}📋 答案: {single_model_result[0]['answer'][:100]}...{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}💡 由於每日額度限制，無法進行完整的四層測試{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}   明天重新運行可進行完整測試{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}❌ 單模型測試也失敗{Style.RESET_ALL}")
                    return False
            else:
                # 重新拋出其他錯誤
                raise e
        
    except Exception as e:
        print(f"{Fore.RED}❌ 測試過程中發生錯誤: {str(e)}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}錯誤類型: {type(e).__name__}{Style.RESET_ALL}")
        import traceback
        print(f"{Fore.YELLOW}詳細錯誤信息:{Style.RESET_ALL}")
        traceback.print_exc()
        return False
    
    print(f"{Fore.GREEN}✅ 系統功能測試完成{Style.RESET_ALL}\n")
    return True

async def main():
    """主測試函數"""
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}🧪 多層次LLM邏輯題驗證系統 - 測試程序{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")
    
    tests = [
        ("配置測試", test_config),
        ("題目文件測試", test_question_files),
        ("系統功能測試", test_simple_question)
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
        print(f"{Fore.GREEN}系統已準備就緒，可以開始使用。{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  部分測試未通過 ({passed}/{total}){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}請檢查失敗的測試項目並修復相關問題。{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}💡 使用提示：{Style.RESET_ALL}")
    print(f"   - 查看幫助: python main.py --help")
    print(f"   - 處理單個題目: python main.py --file \"2星題目/2星_1.txt\" --verbose")
    print(f"   - 批量處理: python main.py --batch --verbose")
    print(f"   - 交互模式: python main.py")
    print(f"   - 直接問題: python main.py --question \"你的問題\" --verbose")

if __name__ == "__main__":
    asyncio.run(main()) 