"""
多層次LLM邏輯題驗證與訂正系統
主協調器 - 整合四個層級的處理流程
"""
import asyncio
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from colorama import init, Fore, Style
import sys

# 初始化colorama
init()

from config import Config
from layers.answering_layer import AnsweringLayer
from layers.verification_layer import VerificationLayer
from layers.correction_layer import CorrectionLayer
from layers.decision_layer import DecisionLayer

class LLMLogicSystem:
    """多層次LLM邏輯題驗證系統"""
    
    def __init__(self):
        self.config = Config()
        self.answering_layer = AnsweringLayer()
        self.verification_layer = VerificationLayer()
        self.correction_layer = CorrectionLayer()
        self.decision_layer = DecisionLayer()
        
        # 確保結果目錄存在
        os.makedirs(self.config.RESULTS_DIR, exist_ok=True)
    
    async def process_question(self, question: str, 
                             answering_models: List[str] = None,
                             verification_models: List[str] = None,
                             correction_model: str = None,
                             decision_model: str = None,
                             save_results: bool = True) -> Dict[str, Any]:
        """
        處理單個邏輯題目
        
        Args:
            question: 邏輯題目
            answering_models: 作答層使用的模型列表
            verification_models: 驗證層使用的模型列表
            correction_model: 訂正層使用的模型
            decision_model: 決策層使用的模型
            save_results: 是否保存結果
        
        Returns:
            包含所有層級結果的字典
        """
        start_time = time.time()
        
        print(f"{Fore.CYAN}🚀 開始處理邏輯題目...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}題目: {question[:100]}...{Style.RESET_ALL}\n")
        
        results = {
            'question': question,
            'timestamp': datetime.now().isoformat(),
            'processing_time': 0,
            'answering_results': [],
            'verification_results': [],
            'correction_results': [],
            'final_decision': {},
            'success': False
        }
        
        try:
            # 第一層：作答層
            print(f"{Fore.GREEN}📝 第一層：作答層處理中...{Style.RESET_ALL}")
            answering_results = await self.answering_layer.process_question(
                question, answering_models
            )
            results['answering_results'] = answering_results
            
            successful_answers = [r for r in answering_results if r['success']]
            print(f"{Fore.BLUE}✅ 作答層完成，成功答案數: {len(successful_answers)}/{len(answering_results)}{Style.RESET_ALL}")
            
            if not successful_answers:
                print(f"{Fore.RED}❌ 沒有成功的答案，終止處理{Style.RESET_ALL}")
                results['success'] = False
                return results
            
            # 第二層：驗證層
            print(f"{Fore.GREEN}🔍 第二層：驗證層處理中...{Style.RESET_ALL}")
            verification_results = await self.verification_layer.verify_answers(
                question, successful_answers, verification_models
            )
            results['verification_results'] = verification_results
            
            verification_summary = self.verification_layer.get_verification_summary(verification_results)
            print(f"{Fore.BLUE}✅ 驗證層完成，準確率: {verification_summary['accuracy_rate']*100:.1f}%{Style.RESET_ALL}")
            
            # 第三層：訂正層
            print(f"{Fore.GREEN}🔧 第三層：訂正層處理中...{Style.RESET_ALL}")
            correction_results = await self.correction_layer.correct_answers(
                question, successful_answers, verification_results, correction_model
            )
            results['correction_results'] = correction_results
            
            correction_summary = self.correction_layer.get_correction_summary(correction_results)
            print(f"{Fore.BLUE}✅ 訂正層完成，總體成功率: {correction_summary['overall_success_rate']*100:.1f}%{Style.RESET_ALL}")
            
            # 第四層：最終決策層
            print(f"{Fore.GREEN}🎯 第四層：最終決策層處理中...{Style.RESET_ALL}")
            final_decision = await self.decision_layer.make_final_decision(
                question, successful_answers, verification_results, correction_results, decision_model
            )
            results['final_decision'] = final_decision
            
            if final_decision['success']:
                print(f"{Fore.MAGENTA}🎉 最終決策完成！答案: {final_decision['final_answer']} (信心: {final_decision['confidence_level']}/10){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 最終決策失敗: {final_decision['error']}{Style.RESET_ALL}")
            
            results['success'] = final_decision['success']
            
        except Exception as e:
            print(f"{Fore.RED}❌ 處理過程中發生錯誤: {str(e)}{Style.RESET_ALL}")
            results['error'] = str(e)
            results['success'] = False
        
        finally:
            # 計算處理時間
            results['processing_time'] = time.time() - start_time
            print(f"\n{Fore.CYAN}⏱️ 總處理時間: {results['processing_time']:.2f}秒{Style.RESET_ALL}")
            
            # 保存結果
            if save_results:
                self._save_results(results)
        
        return results
    
    async def process_question_file(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        處理題目文件
        
        Args:
            file_path: 題目文件路徑
            **kwargs: 傳遞給process_question的其他參數
        
        Returns:
            處理結果
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                question = f.read().strip()
            
            print(f"{Fore.CYAN}📁 正在處理文件: {file_path}{Style.RESET_ALL}")
            return await self.process_question(question, **kwargs)
        
        except Exception as e:
            print(f"{Fore.RED}❌ 讀取文件失敗: {str(e)}{Style.RESET_ALL}")
            return {
                'error': f"Failed to read file: {str(e)}",
                'success': False,
                'file_path': file_path
            }
    
    async def batch_process_questions(self, question_files: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        批量處理多個題目文件
        
        Args:
            question_files: 題目文件路徑列表
            **kwargs: 傳遞給process_question的其他參數
        
        Returns:
            所有處理結果的列表
        """
        print(f"{Fore.CYAN}🔄 開始批量處理 {len(question_files)} 個題目...{Style.RESET_ALL}\n")
        
        results = []
        for i, file_path in enumerate(question_files, 1):
            print(f"{Fore.YELLOW}{'='*50}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}處理題目 {i}/{len(question_files)}: {os.path.basename(file_path)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}{'='*50}{Style.RESET_ALL}")
            
            result = await self.process_question_file(file_path, **kwargs)
            result['file_path'] = file_path
            result['question_number'] = i
            results.append(result)
            
            print(f"\n{Fore.GREEN}✅ 題目 {i} 處理完成{Style.RESET_ALL}\n")
        
        # 保存批量結果摘要
        self._save_batch_summary(results)
        
        return results
    
    def _save_results(self, results: Dict[str, Any]):
        """保存單個處理結果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"result_{timestamp}.json"
        filepath = os.path.join(self.config.RESULTS_DIR, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"{Fore.GREEN}💾 結果已保存: {filepath}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ 保存結果失敗: {str(e)}{Style.RESET_ALL}")
    
    def _save_batch_summary(self, batch_results: List[Dict[str, Any]]):
        """保存批量處理摘要"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_summary_{timestamp}.json"
        filepath = os.path.join(self.config.RESULTS_DIR, filename)
        
        # 準備摘要統計
        total_questions = len(batch_results)
        successful_questions = sum(1 for r in batch_results if r.get('success', False))
        total_time = sum(r.get('processing_time', 0) for r in batch_results)
        
        summary = {
            'batch_info': {
                'total_questions': total_questions,
                'successful_questions': successful_questions,
                'success_rate': successful_questions / total_questions if total_questions > 0 else 0,
                'total_processing_time': total_time,
                'average_processing_time': total_time / total_questions if total_questions > 0 else 0,
                'timestamp': datetime.now().isoformat()
            },
            'detailed_results': batch_results
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            print(f"{Fore.GREEN}📊 批量摘要已保存: {filepath}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}📈 批量處理統計: {successful_questions}/{total_questions} 成功 ({successful_questions/total_questions*100:.1f}%){Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ 保存批量摘要失敗: {str(e)}{Style.RESET_ALL}")
    
    def display_formatted_results(self, results: Dict[str, Any]):
        """格式化顯示處理結果"""
        print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}📊 詳細結果報告{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")
        
        # 顯示題目
        print(f"{Fore.CYAN}📋 題目:{Style.RESET_ALL}")
        print(f"{results['question']}\n")
        
        # 顯示作答層結果
        if results['answering_results']:
            print(self.answering_layer.format_results(results['answering_results']))
            print()
        
        # 顯示驗證層結果
        if results['verification_results']:
            print(self.verification_layer.format_results(results['verification_results']))
            print()
        
        # 顯示訂正層結果
        if results['correction_results']:
            print(self.correction_layer.format_results(results['correction_results']))
            print()
        
        # 顯示最終決策結果
        if results['final_decision']:
            print(self.decision_layer.format_result(results['final_decision']))
            print()
        
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}") 