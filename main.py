#!/usr/bin/env python3
"""
多層次LLM邏輯題驗證系統 - 主程序
"""
import asyncio
import argparse
import os
import glob
from colorama import Fore, Style, init
from system_coordinator import SystemCoordinator
from config import Config

# 初始化colorama
init(autoreset=True)

async def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='多層次LLM邏輯題驗證系統')
    
    # 輸入選項
    parser.add_argument('--file', '-f', type=str, help='處理單個題目文件')
    parser.add_argument('--batch', '-b', action='store_true', help='批量處理2星題目目錄中的所有文件')
    parser.add_argument('--question', '-q', type=str, help='直接輸入問題文本')
    
    # 模型選擇
    parser.add_argument('--models', '-m', type=str, nargs='+', 
                       help='指定作答模型（例如：openrouter/deepseek-r1 openrouter/gemini-2-flash）')
    parser.add_argument('--verification-models', type=str, nargs='+',
                       help='指定驗證模型')
    parser.add_argument('--correction-model', type=str, help='指定訂正模型')
    parser.add_argument('--decision-model', type=str, help='指定決策模型')
    
    # 其他選項
    parser.add_argument('--verbose', '-v', action='store_true', help='顯示詳細處理過程')
    parser.add_argument('--save', '-s', type=str, help='指定保存結果的文件名')
    
    args = parser.parse_args()
    
    # 檢查API配置
    config = Config()
    if not config.OPENROUTER_API_KEY:
        print(f"{Fore.RED}錯誤: OpenRouter API密鑰未配置")
        print(f"{Fore.YELLOW}請在.env文件中設置 OPENROUTER_API_KEY")
        return
    
    # 創建系統協調器
    system = SystemCoordinator()
    
    try:
        if args.question:
            # 直接處理問題文本
            await process_single_question(system, args.question, args)
            
        elif args.file:
            # 處理單個文件
            if not os.path.exists(args.file):
                print(f"{Fore.RED}錯誤: 文件不存在: {args.file}")
                return
            
            with open(args.file, 'r', encoding='utf-8') as f:
                question = f.read().strip()
            
            print(f"{Fore.CYAN}處理文件: {args.file}")
            await process_single_question(system, question, args)
            
        elif args.batch:
            # 批量處理
            await process_batch(system, args)
            
        else:
            # 交互模式
            await interactive_mode(system, args)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}用戶中斷程序")
    except Exception as e:
        print(f"{Fore.RED}程序錯誤: {str(e)}")

async def process_single_question(system: SystemCoordinator, question: str, args):
    """處理單個問題"""
    # 準備模型參數
    answering_models = args.models
    verification_models = args.verification_models
    correction_model = args.correction_model
    decision_model = args.decision_model
    
    # 處理問題
    result = await system.process_question(
        question=question,
        answering_models=answering_models,
        verification_models=verification_models,
        correction_model=correction_model,
        decision_model=decision_model,
        verbose=args.verbose
    )
    
    # 顯示結果
    if not args.verbose:  # 如果verbose模式已經顯示了過程，這裡只顯示摘要
        print(system.format_complete_results(result))
    
    # 保存結果
    saved_path = system.save_results(result, args.save)
    print(f"\n{Fore.GREEN}結果已保存到: {saved_path}")

async def process_batch(system: SystemCoordinator, args):
    """批量處理"""
    config = Config()
    pattern = os.path.join(config.QUESTIONS_DIR, '*.txt')
    files = glob.glob(pattern)
    
    if not files:
        print(f"{Fore.RED}錯誤: 在 {config.QUESTIONS_DIR} 目錄中未找到.txt文件")
        return
    
    print(f"{Fore.CYAN}找到 {len(files)} 個題目文件")
    print(f"{Fore.CYAN}開始批量處理...")
    
    batch_results = []
    
    for i, file_path in enumerate(files, 1):
        print(f"\n{Fore.YELLOW}{'='*60}")
        print(f"{Fore.YELLOW}處理文件 {i}/{len(files)}: {os.path.basename(file_path)}")
        print(f"{Fore.YELLOW}{'='*60}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                question = f.read().strip()
            
            result = await system.process_question(
                question=question,
                answering_models=args.models,
                verification_models=args.verification_models,
                correction_model=args.correction_model,
                decision_model=args.decision_model,
                verbose=args.verbose
            )
            
            result['file_path'] = file_path
            result['file_number'] = i
            batch_results.append(result)
            
            print(f"{Fore.GREEN}✓ 文件 {i} 處理完成")
            
        except Exception as e:
            print(f"{Fore.RED}✗ 文件 {i} 處理失敗: {str(e)}")
            batch_results.append({
                'file_path': file_path,
                'file_number': i,
                'error': str(e),
                'success': False
            })
    
    # 保存批量結果
    batch_summary = {
        'batch_info': {
            'total_files': len(files),
            'successful_files': sum(1 for r in batch_results if r.get('summary', {}).get('overall_success', False)),
            'timestamp': result['timestamp']
        },
        'results': batch_results
    }
    
    batch_path = system.save_results(batch_summary, f"batch_results_{len(files)}_files.json")
    print(f"\n{Fore.GREEN}批量處理完成，結果已保存到: {batch_path}")

async def interactive_mode(system: SystemCoordinator, args):
    """交互模式"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}多層次LLM邏輯題驗證系統 - 交互模式")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}輸入 'quit' 或 'exit' 退出程序")
    print(f"{Fore.YELLOW}輸入 'help' 查看幫助信息")
    
    config = Config()
    print(f"\n{Fore.MAGENTA}當前模型配置:")
    print(f"作答模型: {', '.join(config.DEFAULT_ANSWERING_MODELS)}")
    print(f"驗證模型: {', '.join(config.DEFAULT_VERIFICATION_MODELS)}")
    print(f"訂正模型: {config.DEFAULT_CORRECTION_MODEL}")
    print(f"決策模型: {config.DEFAULT_DECISION_MODEL}")
    
    while True:
        try:
            question = input(f"\n{Fore.WHITE}請輸入邏輯題目: ").strip()
            
            if question.lower() in ['quit', 'exit']:
                print(f"{Fore.GREEN}再見！")
                break
            elif question.lower() == 'help':
                print_help()
                continue
            elif not question:
                continue
            
            await process_single_question(system, question, args)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}程序已退出")
            break
        except EOFError:
            break

def print_help():
    """顯示幫助信息"""
    print(f"\n{Fore.CYAN}=== 幫助信息 ===")
    print(f"{Fore.WHITE}可用命令:")
    print(f"  help  - 顯示此幫助信息")
    print(f"  quit  - 退出程序")
    print(f"  exit  - 退出程序")
    print(f"\n{Fore.WHITE}輸入邏輯題目後，系統將通過四層處理:")
    print(f"  1. 作答層 - 多個LLM給出答案")
    print(f"  2. 驗證層 - 交叉驗證答案正確性")
    print(f"  3. 訂正層 - 根據驗證結果修正答案")
    print(f"  4. 決策層 - 綜合所有信息做出最終決策")

if __name__ == '__main__':
    asyncio.run(main()) 