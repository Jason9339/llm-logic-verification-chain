"""
決策層 (Decision Layer)
整合前面三層的結果，作出最終決策
"""
import asyncio
import json
import os
from typing import List, Dict, Any
import sys
sys.path.append('..')
from llm_client import LLMClient
from config import Config

class DecisionLayer:
    """決策層處理器"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.config = Config()
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """載入決策層prompt模板"""
        prompt_path = os.path.join(self.config.PROMPTS_DIR, 'decision_layer.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    async def make_final_decision(self, question: str, 
                                original_answers: List[Dict[str, Any]],
                                verification_results: List[Dict[str, Any]],
                                correction_results: List[Dict[str, Any]],
                                decision_model: str = None) -> Dict[str, Any]:
        """
        根據所有層的結果作出最終決策
        
        Args:
            question: 原始問題
            original_answers: 作答層結果
            verification_results: 驗證層結果
            correction_results: 訂正層結果
            decision_model: 決策模型
        
        Returns:
            最終決策結果
        """
        if decision_model is None:
            decision_model = self.config.DEFAULT_DECISION_MODEL
        
        # 準備決策所需的所有信息
        decision_context = self._prepare_decision_context(
            question, original_answers, verification_results, correction_results
        )
        
        # 準備決策prompt
        prompt = self.prompt_template.format(**decision_context)
        
        try:
            # 調用決策LLM
            response = await self.llm_client.call_model(decision_model, prompt)
            
            if not response['success']:
                return {
                    'success': False,
                    'error': response['error'],
                    'decision_model': decision_model
                }
            
            # 解析JSON回應
            parsed_response = self.llm_client.parse_json_response(response['response'])
            
            if 'error' in parsed_response:
                return {
                    'success': False,
                    'error': parsed_response['error'],
                    'raw_response': parsed_response.get('raw_response', ''),
                    'decision_model': decision_model
                }
            
            # 返回標準化決策結果（移除信心分數）
            final_decision = {
                'success': True,
                'decision_model': decision_model,
                'final_answer': parsed_response.get('final_answer', ''),
                'reasoning': parsed_response.get('reasoning', ''),
                'evidence_analysis': parsed_response.get('evidence_analysis', ''),
                'answer_confidence': self._calculate_answer_confidence(verification_results),
                'verification_consensus': self._calculate_consensus(verification_results),
                'raw_response': response['response']
            }
            
            return final_decision
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'decision_model': decision_model
            }
    
    def _prepare_decision_context(self, question: str, 
                                original_answers: List[Dict[str, Any]],
                                verification_results: List[Dict[str, Any]],
                                correction_results: List[Dict[str, Any]]) -> Dict[str, str]:
        """準備決策上下文"""
        
        # 格式化原始答案
        original_summary = []
        for answer in original_answers:
            if answer['success']:
                original_summary.append(f"模型: {answer['model']}")
                original_summary.append(f"答案: {answer['answer']}")
                original_summary.append("---")
        
        # 格式化驗證結果
        verification_summary = []
        for verification in verification_results:
            if verification['success']:
                verification_summary.append(f"驗證模型: {verification['verification_model']}")
                verification_summary.append(f"目標: {verification['target_model']}")
                verification_summary.append(f"結果: {verification['verdict']}")
                if verification['error_reason']:
                    verification_summary.append(f"說明: {verification['error_reason']}")
                verification_summary.append("---")
        
        # 格式化訂正結果
        correction_summary = []
        for correction in correction_results:
            if correction.get('needs_correction', False):
                correction_summary.append(f"模型: {correction['model']}")
                if correction.get('success', False):
                    correction_summary.append(f"原答案: {correction['original_answer']}")
                    correction_summary.append(f"修正答案: {correction['revised_answer']}")
                else:
                    correction_summary.append("訂正失敗")
                correction_summary.append("---")
            else:
                correction_summary.append(f"模型: {correction['model']} - 無需訂正")
                correction_summary.append("---")
        
        return {
            'question': question,
            'original_answers': '\n'.join(original_summary) if original_summary else '無可用答案',
            'verification_results': '\n'.join(verification_summary) if verification_summary else '無驗證結果',
            'correction_results': '\n'.join(correction_summary) if correction_summary else '無訂正結果'
        }
    
    def _calculate_answer_confidence(self, verification_results: List[Dict[str, Any]]) -> float:
        """基於驗證結果計算答案信心度"""
        if not verification_results:
            return 0.5
        
        correct_count = sum(1 for v in verification_results if v.get('verdict') == 'Correct')
        total_count = len(verification_results)
        
        return correct_count / total_count if total_count > 0 else 0.5
    
    def _calculate_consensus(self, verification_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """計算驗證共識度"""
        if not verification_results:
            return {'consensus_rate': 0, 'agreement_level': 'No Data'}
        
        verdict_counts = {}
        for verification in verification_results:
            verdict = verification.get('verdict', 'Unknown')
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
        
        total_verifications = len(verification_results)
        max_agreement = max(verdict_counts.values()) if verdict_counts else 0
        consensus_rate = max_agreement / total_verifications
        
        # 定義共識程度
        if consensus_rate >= 0.8:
            agreement_level = 'High Consensus'
        elif consensus_rate >= 0.6:
            agreement_level = 'Moderate Consensus'
        else:
            agreement_level = 'Low Consensus'
        
        return {
            'consensus_rate': consensus_rate,
            'agreement_level': agreement_level,
            'verdict_distribution': verdict_counts
        }
    
    def format_results(self, result: Dict[str, Any]) -> str:
        """格式化決策結果"""
        output = []
        output.append("=== 決策層結果 ===\n")
        
        if result['success']:
            output.append(f"決策模型: {result['decision_model']}")
            output.append(f"最終答案: {result['final_answer']}")
            output.append(f"決策信心度: {result['answer_confidence']:.2%}")
            output.append(f"驗證共識度: {result['verification_consensus']['consensus_rate']:.2%}")
            output.append(f"共識程度: {result['verification_consensus']['agreement_level']}")
            output.append("\n決策推理:")
            output.append(result['reasoning'])
            
            if result['evidence_analysis']:
                output.append("\n證據分析:")
                output.append(result['evidence_analysis'])
        else:
            output.append("✗ 決策失敗")
            output.append(f"錯誤: {result['error']}")
        
        return "\n".join(output) 