"""
作答層 (Answering Layer)
模擬學生作答，多個LLM對同一題目給出答案
"""
import asyncio
import json
import os
from typing import List, Dict, Any
import sys
sys.path.append('..')
from llm_client import LLMClient
from config import Config

class AnsweringLayer:
    """作答層處理器"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.config = Config()
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """載入作答層prompt模板"""
        prompt_path = os.path.join(self.config.PROMPTS_DIR, 'answering_layer.txt')
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    async def process_question(self, question: str, models: List[str] = None) -> List[Dict[str, Any]]:
        """
        處理問題，獲取多個模型的答案
        
        Args:
            question: 邏輯題目
            models: 要使用的模型列表，如果為None則使用默認模型
        
        Returns:
            包含所有模型回答的列表
        """
        if models is None:
            models = self.config.DEFAULT_ANSWERING_MODELS
        
        # 準備prompt
        prompt = self.prompt_template.format(question=question)
        
        # 串行調用模型以避免速率限制
        results = []
        for model in models:
            if self.config.is_model_available(model):
                print(f"正在處理模型: {model}")
                result = await self._get_model_answer(model, prompt)
                results.append(result)
                # 在每次調用之間稍作延遲
                await asyncio.sleep(2)
        
        # 處理結果（由於現在是串行處理，不需要檢查Exception）
        answers = results
        
        return answers
    
    async def _get_model_answer(self, model: str, prompt: str) -> Dict[str, Any]:
        """獲取單個模型的答案"""
        try:
            # 調用LLM
            response = await self.llm_client.call_model(model, prompt)
            
            if not response['success']:
                return {
                    'model': model,
                    'success': False,
                    'error': response['error'],
                    'answer': None,
                    'reasoning': None
                }
            
            # 解析JSON回應
            parsed_response = self.llm_client.parse_json_response(response['response'])
            
            if 'error' in parsed_response:
                return {
                    'model': model,
                    'success': False,
                    'error': parsed_response['error'],
                    'raw_response': parsed_response.get('raw_response', ''),
                    'answer': None,
                    'reasoning': None
                }
            
            # 提取標準字段（移除信心分數）
            return {
                'model': model,
                'success': True,
                'answer': parsed_response.get('answer', ''),
                'reasoning': parsed_response.get('reasoning', ''),
                'raw_response': response['response'],
                'usage': response.get('usage')
            }
        
        except Exception as e:
            return {
                'model': model,
                'success': False,
                'error': str(e),
                'answer': None,
                'reasoning': None
            }
    
    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """格式化結果用於顯示"""
        output = []
        output.append("=== 作答層結果 ===\n")
        
        for i, result in enumerate(results, 1):
            output.append(f"模型 {i}: {result['model']}")
            if result['success']:
                output.append(f"答案: {result['answer']}")
                output.append(f"推理過程: {result['reasoning'][:200]}...")
            else:
                output.append(f"錯誤: {result['error']}")
            output.append("-" * 50)
        
        return "\n".join(output) 