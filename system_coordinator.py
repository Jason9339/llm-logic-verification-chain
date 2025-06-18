"""
多層次LLM邏輯題驗證系統 - 系統協調器
協調四個層次的處理流程：作答層、驗證層、訂正層、決策層
"""
import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from colorama import Fore, Style, init

from config import Config
from layers.answering_layer import AnsweringLayer
from layers.verification_layer import VerificationLayer
from layers.correction_layer import CorrectionLayer
from layers.decision_layer import DecisionLayer

# 初始化colorama
init(autoreset=True)

class SystemCoordinator:
    """系統協調器 - 整合四層處理流程"""
    
    def __init__(self):
        self.config = Config()
        self.answering_layer = AnsweringLayer()
        self.verification_layer = VerificationLayer()
        self.correction_layer = CorrectionLayer()
        self.decision_layer = DecisionLayer()
    
    async def process_question(self, question: str, 
                             answering_models: Optional[List[str]] = None,
                             verification_models: Optional[List[str]] = None,
                             correction_model: Optional[str] = None,
                             decision_model: Optional[str] = None,
                             verbose: bool = False) -> Dict[str, Any]:
        """
        處理單個邏輯題目，通過四層處理流程
        
        Args:
            question: 邏輯題目
            answering_models: 作答模型列表
            verification_models: 驗證模型列表
            correction_model: 訂正模型
            decision_model: 決策模型
            verbose: 是否顯示詳細過程
            
        Returns:
            包含所有層處理結果的字典
        """
        start_time = time.time()
        
        if verbose:
            print(f"{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}開始處理問題: {question[:50]}...")
            print(f"{Fore.CYAN}{'='*60}")
        
        # 第一層：作答層
        if verbose:
            print(f"\n{Fore.YELLOW}第一層：作答層處理中...")
        
        answering_results = await self.answering_layer.process_question(
            question, answering_models
        )
        
        if verbose:
            print(f"{Fore.GREEN}✓ 作答層完成，共 {len(answering_results)} 個回答")
            for i, result in enumerate(answering_results, 1):
                if result['success']:
                    print(f"  {i}. {result['model']}: {result['answer']}")
                else:
                    print(f"  {i}. {result['model']}: {Fore.RED}錯誤 - {result['error']}")
        
        # 第二層：驗證層（交叉驗證）
        if verbose:
            print(f"\n{Fore.YELLOW}第二層：驗證層處理中（交叉驗證）...")
        
        verification_results = await self.verification_layer.verify_answers(
            question, answering_results, verification_models
        )
        
        if verbose:
            print(f"{Fore.GREEN}✓ 驗證層完成，共 {len(verification_results)} 個驗證結果")
            correct_count = sum(1 for v in verification_results if v.get('verdict') == 'Correct')
            incorrect_count = sum(1 for v in verification_results if v.get('verdict') == 'Incorrect')
            print(f"  正確: {correct_count}, 錯誤: {incorrect_count}")
        
        # 第三層：訂正層
        if verbose:
            print(f"\n{Fore.YELLOW}第三層：訂正層處理中...")
        
        correction_results = await self.correction_layer.correct_answers(
            question, answering_results, verification_results, correction_model
        )
        
        if verbose:
            print(f"{Fore.GREEN}✓ 訂正層完成，共 {len(correction_results)} 個處理結果")
            corrected_count = sum(1 for c in correction_results if c.get('correction_applied', False))
            print(f"  已訂正: {corrected_count}")
        
        # 第四層：決策層
        if verbose:
            print(f"\n{Fore.YELLOW}第四層：決策層處理中...")
        
        decision_result = await self.decision_layer.make_final_decision(
            question, answering_results, verification_results, correction_results, decision_model
        )
        
        if verbose:
            print(f"{Fore.GREEN}✓ 決策層完成")
            if decision_result['success']:
                print(f"  最終答案: {decision_result['final_answer']}")
                print(f"  信心度: {decision_result['answer_confidence']:.2%}")
            else:
                print(f"  {Fore.RED}決策失敗: {decision_result['error']}")
        
        # 計算總處理時間
        processing_time = time.time() - start_time
        
        # 整合所有結果
        final_result = {
            'question': question,
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat(),
            'layer_results': {
                'answering': answering_results,
                'verification': verification_results,
                'correction': correction_results,
                'decision': decision_result
            },
            'summary': self._generate_summary(
                answering_results, verification_results, correction_results, decision_result
            ),
            'system_config': {
                'answering_models': answering_models or self.config.DEFAULT_ANSWERING_MODELS,
                'verification_models': verification_models or self.config.DEFAULT_VERIFICATION_MODELS,
                'correction_model': correction_model or self.config.DEFAULT_CORRECTION_MODEL,
                'decision_model': decision_model or self.config.DEFAULT_DECISION_MODEL
            }
        }
        
        if verbose:
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}處理完成！總耗時: {processing_time:.2f}秒")
            print(f"{Fore.CYAN}{'='*60}")
        
        return final_result
    
    def _generate_summary(self, answering_results: List[Dict[str, Any]],
                         verification_results: List[Dict[str, Any]],
                         correction_results: List[Dict[str, Any]],
                         decision_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成處理結果摘要"""
        
        # 作答層摘要
        successful_answers = sum(1 for a in answering_results if a['success'])
        total_answers = len(answering_results)
        
        # 驗證層摘要
        verification_summary = self.verification_layer.get_verification_summary(verification_results)
        
        # 訂正層摘要
        correction_summary = self.correction_layer.get_correction_summary(correction_results)
        
        # 決策層摘要
        decision_summary = {
            'success': decision_result['success'],
            'final_answer': decision_result.get('final_answer', 'N/A'),
            'confidence': decision_result.get('answer_confidence', 0)
        }
        
        return {
            'answering_success_rate': successful_answers / total_answers if total_answers > 0 else 0,
            'verification_summary': verification_summary,
            'correction_summary': correction_summary,
            'decision_summary': decision_summary,
            'overall_success': decision_result['success']
        }
    
    def format_complete_results(self, result: Dict[str, Any]) -> str:
        """格式化完整結果用於顯示"""
        output = []
        
        # 標題
        output.append(f"{Fore.CYAN}{'='*80}")
        output.append(f"{Fore.CYAN}多層次LLM邏輯驗證系統 - 處理結果")
        output.append(f"{Fore.CYAN}{'='*80}")
        
        # 基本信息
        output.append(f"\n{Fore.WHITE}問題: {result['question']}")
        output.append(f"{Fore.WHITE}處理時間: {result['processing_time']:.2f}秒")
        output.append(f"{Fore.WHITE}時間戳: {result['timestamp']}")
        
        # 系統配置
        output.append(f"\n{Fore.MAGENTA}系統配置:")
        config = result['system_config']
        output.append(f"  作答模型: {', '.join(config['answering_models'])}")
        output.append(f"  驗證模型: {', '.join(config['verification_models'])}")
        output.append(f"  訂正模型: {config['correction_model']}")
        output.append(f"  決策模型: {config['decision_model']}")
        
        # 各層結果
        layer_results = result['layer_results']
        
        # 作答層結果
        output.append(f"\n{Fore.YELLOW}=== 第一層：作答層結果 ===")
        for i, answer in enumerate(layer_results['answering'], 1):
            if answer['success']:
                output.append(f"{Fore.GREEN}{i}. {answer['model']}: {answer['answer']}")
            else:
                output.append(f"{Fore.RED}{i}. {answer['model']}: 錯誤 - {answer['error']}")
        
        # 驗證層結果
        output.append(f"\n{Fore.YELLOW}=== 第二層：驗證層結果（交叉驗證）===")
        for i, verification in enumerate(layer_results['verification'], 1):
            if verification['success']:
                verdict_color = Fore.GREEN if verification['verdict'] == 'Correct' else Fore.RED
                output.append(f"{i}. {verification['verification_model']} → {verification['target_model']}: {verdict_color}{verification['verdict']}")
                if verification['error_reason']:
                    output.append(f"   說明: {verification['error_reason'][:100]}...")
            else:
                output.append(f"{Fore.RED}{i}. 驗證錯誤: {verification['error']}")
        
        # 訂正層結果
        output.append(f"\n{Fore.YELLOW}=== 第三層：訂正層結果 ===")
        for i, correction in enumerate(layer_results['correction'], 1):
            if not correction.get('needs_correction', False):
                output.append(f"{Fore.GREEN}{i}. {correction['model']}: 無需訂正")
            elif correction.get('correction_applied', False):
                output.append(f"{Fore.YELLOW}{i}. {correction['model']}: 已訂正")
                output.append(f"   原答案: {correction['original_answer']}")
                output.append(f"   修正答案: {correction['revised_answer']}")
            else:
                output.append(f"{Fore.RED}{i}. {correction['model']}: 訂正失敗")
        
        # 決策層結果
        output.append(f"\n{Fore.YELLOW}=== 第四層：決策層結果 ===")
        decision = layer_results['decision']
        if decision['success']:
            output.append(f"{Fore.GREEN}最終答案: {decision['final_answer']}")
            output.append(f"信心度: {decision['answer_confidence']:.2%}")
            output.append(f"驗證共識度: {decision['verification_consensus']['consensus_rate']:.2%}")
            output.append(f"共識程度: {decision['verification_consensus']['agreement_level']}")
        else:
            output.append(f"{Fore.RED}決策失敗: {decision['error']}")
        
        # 摘要
        output.append(f"\n{Fore.CYAN}=== 處理摘要 ===")
        summary = result['summary']
        output.append(f"作答成功率: {summary['answering_success_rate']:.2%}")
        output.append(f"驗證準確率: {summary['verification_summary']['accuracy_rate']:.2%}")
        output.append(f"訂正成功率: {summary['correction_summary']['correction_success_rate']:.2%}")
        output.append(f"整體成功: {'是' if summary['overall_success'] else '否'}")
        
        output.append(f"\n{Fore.CYAN}{'='*80}")
        
        return "\n".join(output)
    
    def save_results(self, results: Dict[str, Any], filename: Optional[str] = None) -> str:
        """保存結果到文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"logic_verification_result_{timestamp}.json"
        
        # 確保結果目錄存在
        results_dir = self.config.RESULTS_DIR
        os.makedirs(results_dir, exist_ok=True)
        
        # 保存結果
        filepath = os.path.join(results_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return filepath 