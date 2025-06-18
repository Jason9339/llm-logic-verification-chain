"""
驗證層 (Verification Layer)
模擬教師批改，驗證作答層的結果正確性
實現交叉驗證：每個模型不驗證自己的答案
"""
import asyncio
import json
import os
from typing import List, Dict, Any
import sys
sys.path.append('..')
from llm_client import LLMClient
from config import Config

class VerificationLayer:
    """驗證層處理器"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.config = Config()
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """載入驗證層prompt模板"""
        prompt_path = os.path.join(self.config.PROMPTS_DIR, 'verification_layer.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _get_model_short_name(self, model_key: str) -> str:
        """獲取模型簡短名稱用於交叉驗證判斷"""
        try:
            provider, model = model_key.split('/')
            return model
        except:
            return model_key
    
    async def verify_answers(self, question: str, answers: List[Dict[str, Any]], 
                           verification_models: List[str] = None) -> List[Dict[str, Any]]:
        """
        驗證作答層的答案 - 實現交叉驗證
        
        Args:
            question: 原始問題
            answers: 作答層的結果
            verification_models: 用於驗證的模型列表
        
        Returns:
            包含所有驗證結果的列表
        """
        if verification_models is None:
            verification_models = self.config.DEFAULT_VERIFICATION_MODELS
        
        verification_results = []
        
        # 對每個答案進行交叉驗證（包括失敗的答案）
        for answer in answers:
            target_model_short = self._get_model_short_name(answer['model'])
            
            # 串行處理驗證模型，進行交叉驗證
            for verification_model in verification_models:
                verification_model_short = self._get_model_short_name(verification_model)
                
                # 交叉驗證：不讓模型驗證自己的答案
                if verification_model_short != target_model_short:
                    if self.config.is_model_available(verification_model):
                        print(f"正在使用 {verification_model} 驗證 {answer['model']} 的答案")
                        
                        # 如果作答失敗，驗證失敗原因
                        if not answer['success']:
                            verification_results.append({
                                'verification_model': verification_model,
                                'target_model': answer['model'],
                                'success': True,
                                'verdict': 'Incorrect',
                                'error_reason': f"作答層失敗：{answer['error']}",
                                'raw_response': f"作答失敗，無法驗證：{answer['error']}"
                            })
                        else:
                            verification = await self._verify_single_answer(
                                question, answer, verification_model
                            )
                            verification_results.append(verification)
                        
                        # 在每次驗證之間稍作延遲
                        await asyncio.sleep(2)
        
        return verification_results
    
    async def _verify_single_answer(self, question: str, answer: Dict[str, Any], 
                                  verification_model: str) -> Dict[str, Any]:
        """驗證單個答案 - 只使用答案，不使用推理過程"""
        try:
            # 準備驗證prompt（只包含答案，不包含推理過程）
            prompt = self.prompt_template.format(
                question=question,
                model_name=answer['model'],
                answer=answer['answer']
            )
            
            # 調用驗證LLM
            response = await self.llm_client.call_model(verification_model, prompt)
            
            if not response['success']:
                return {
                    'verification_model': verification_model,
                    'target_model': answer['model'],
                    'success': False,
                    'error': response['error'],
                    'verdict': 'Error',
                    'error_reason': response['error']
                }
            
            # 解析JSON回應
            parsed_response = self.llm_client.parse_json_response(response['response'])
            
            if 'error' in parsed_response:
                return {
                    'verification_model': verification_model,
                    'target_model': answer['model'],
                    'success': False,
                    'error': parsed_response['error'],
                    'verdict': 'Error',
                    'error_reason': parsed_response.get('raw_response', '')
                }
            
            # 返回標準化驗證結果（移除信心分數）
            return {
                'verification_model': verification_model,
                'target_model': parsed_response.get('target_model', answer['model']),
                'success': True,
                'verdict': parsed_response.get('verdict', 'Unknown'),
                'error_reason': parsed_response.get('error_reason', ''),
                'raw_response': response['response']
            }
        
        except Exception as e:
            return {
                'verification_model': verification_model,
                'target_model': answer['model'],
                'success': False,
                'error': str(e),
                'verdict': 'Error',
                'error_reason': str(e)
            }
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """格式化驗證結果"""
        output = []
        output.append("=== 驗證層結果（交叉驗證）===\n")
        
        for i, result in enumerate(results, 1):
            output.append(f"驗證 {i}:")
            output.append(f"驗證模型: {result['verification_model']}")
            output.append(f"目標模型: {result['target_model']}")
            
            if result['success']:
                output.append(f"驗證結果: {result['verdict']}")
                if result['error_reason']:
                    output.append(f"說明: {result['error_reason']}")
            else:
                output.append(f"驗證錯誤: {result['error']}")
            
            output.append("-" * 50)
        
        return "\n".join(output)
    
    def get_verification_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """獲取驗證結果摘要"""
        total_verifications = len(results)
        correct_count = sum(1 for r in results if r.get('verdict') == 'Correct')
        incorrect_count = sum(1 for r in results if r.get('verdict') == 'Incorrect')
        error_count = sum(1 for r in results if not r.get('success', True))
        
        return {
            'total_verifications': total_verifications,
            'correct_count': correct_count,
            'incorrect_count': incorrect_count,
            'error_count': error_count,
            'accuracy_rate': correct_count / total_verifications if total_verifications > 0 else 0
        } 