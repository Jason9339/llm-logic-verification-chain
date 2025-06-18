"""
訂正層 (Correction Layer)
模擬學生根據教師回饋修正錯誤
"""
import asyncio
import json
import os
from typing import List, Dict, Any
import sys
sys.path.append('..')
from llm_client import LLMClient
from config import Config

class CorrectionLayer:
    """訂正層處理器"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.config = Config()
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """載入訂正層prompt模板"""
        prompt_path = os.path.join(self.config.PROMPTS_DIR, 'correction_layer.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    async def correct_answers(self, question: str, original_answers: List[Dict[str, Any]], 
                            verification_results: List[Dict[str, Any]], 
                            correction_model: str = None) -> List[Dict[str, Any]]:
        """
        根據驗證結果訂正錯誤答案
        
        Args:
            question: 原始問題
            original_answers: 作答層的原始答案
            verification_results: 驗證層的結果
            correction_model: 用於訂正的模型
        
        Returns:
            包含所有訂正結果的列表
        """
        if correction_model is None:
            correction_model = self.config.DEFAULT_CORRECTION_MODEL
        
        correction_results = []
        
        # 建立驗證結果的索引，便於查找
        verification_map = {}
        for verification in verification_results:
            target_model = verification['target_model']
            if target_model not in verification_map:
                verification_map[target_model] = []
            verification_map[target_model].append(verification)
        
        # 對需要訂正的答案進行處理
        tasks = []
        for original_answer in original_answers:
            if not original_answer['success']:
                continue
            
            model_name = original_answer['model']
            model_verifications = verification_map.get(model_name, [])
            
            # 檢查是否有Incorrect的驗證結果
            incorrect_verifications = [v for v in model_verifications if v.get('verdict') == 'Incorrect']
            
            if incorrect_verifications:
                # 需要訂正，選擇第一個錯誤驗證結果
                verification_to_use = incorrect_verifications[0]
                
                task = self._correct_single_answer(
                    question, original_answer, verification_to_use, correction_model
                )
                tasks.append(task)
            else:
                # 不需要訂正，保留原答案
                correction_results.append({
                    'model': model_name,
                    'needs_correction': False,
                    'original_answer': original_answer['answer'],
                    'revised_answer': original_answer['answer'],
                    'original_reasoning': original_answer['reasoning'],
                    'revised_reasoning': original_answer['reasoning'],
                    'correction_applied': False
                })
        
        # 串行處理訂正任務
        for task in tasks:
            print(f"正在進行訂正...")
            correction = await task
            correction_results.append(correction)
            # 在每次訂正之間稍作延遲
            await asyncio.sleep(2)
        
        return correction_results
    
    async def _correct_single_answer(self, question: str, original_answer: Dict[str, Any], 
                                   verification_result: Dict[str, Any], 
                                   correction_model: str) -> Dict[str, Any]:
        """訂正單個答案"""
        try:
            # 準備訂正prompt
            prompt = self.prompt_template.format(
                question=question,
                original_reasoning=original_answer['reasoning'],
                original_answer=original_answer['answer'],
                verdict=verification_result['verdict'],
                error_reason=verification_result['error_reason']
            )
            
            # 調用訂正LLM
            response = await self.llm_client.call_model(correction_model, prompt)
            
            if not response['success']:
                return {
                    'model': original_answer['model'],
                    'needs_correction': True,
                    'success': False,
                    'error': response['error'],
                    'correction_applied': False
                }
            
            # 解析JSON回應
            parsed_response = self.llm_client.parse_json_response(response['response'])
            
            if 'error' in parsed_response:
                return {
                    'model': original_answer['model'],
                    'needs_correction': True,
                    'success': False,
                    'error': parsed_response['error'],
                    'raw_response': parsed_response.get('raw_response', ''),
                    'correction_applied': False
                }
            
            # 返回標準化訂正結果（移除信心分數）
            return {
                'model': original_answer['model'],
                'needs_correction': True,
                'success': True,
                'original_answer': original_answer['answer'],
                'revised_answer': parsed_response.get('revised_answer', ''),
                'original_reasoning': original_answer['reasoning'],
                'revised_reasoning': parsed_response.get('revised_reasoning', ''),
                'original_error_acknowledgment': parsed_response.get('original_error_acknowledgment', ''),
                'correction_applied': True,
                'verification_error_reason': verification_result['error_reason'],
                'raw_response': response['response']
            }
        
        except Exception as e:
            return {
                'model': original_answer['model'],
                'needs_correction': True,
                'success': False,
                'error': str(e),
                'correction_applied': False
            }
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """格式化訂正結果"""
        output = []
        output.append("=== 訂正層結果 ===\n")
        
        for i, result in enumerate(results, 1):
            output.append(f"訂正 {i}: {result['model']}")
            
            if not result['needs_correction']:
                output.append("✓ 無需訂正，答案已正確")
                output.append(f"答案: {result['revised_answer']}")
            elif result.get('success', False):
                output.append("⚠ 已進行訂正")
                output.append(f"原答案: {result['original_answer']}")
                output.append(f"修正答案: {result['revised_answer']}")
                if result.get('original_error_acknowledgment'):
                    output.append(f"錯誤認知: {result['original_error_acknowledgment'][:100]}...")
            else:
                output.append("✗ 訂正失敗")
                output.append(f"錯誤: {result.get('error', 'Unknown error')}")
            
            output.append("-" * 50)
        
        return "\n".join(output)
    
    def get_correction_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """獲取訂正結果摘要"""
        total_answers = len(results)
        needed_correction = sum(1 for r in results if r.get('needs_correction', False))
        successful_corrections = sum(1 for r in results if r.get('correction_applied', False))
        
        return {
            'total_answers': total_answers,
            'needed_correction': needed_correction,
            'successful_corrections': successful_corrections,
            'correction_success_rate': successful_corrections / needed_correction if needed_correction > 0 else 1,
            'overall_success_rate': (total_answers - needed_correction + successful_corrections) / total_answers if total_answers > 0 else 0
        } 