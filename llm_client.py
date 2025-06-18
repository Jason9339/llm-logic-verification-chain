"""
多層次LLM邏輯題驗證系統 - LLM客戶端 (aisuite版本)
使用aisuite統一接口，支持多個AI提供商
"""

import os
import asyncio
import json
from typing import Dict, Any
import aisuite as ai
from config import Config


class LLMClient:
    """使用aisuite的統一LLM客戶端"""
    
    def __init__(self):
        self.config = Config()
        self.client = ai.Client()
        self._setup_environment()
    
    def _setup_environment(self):
        """設置環境變量"""
        # OpenAI
        if self.config.OPENAI_API_KEY:
            os.environ['OPENAI_API_KEY'] = self.config.OPENAI_API_KEY
        
        # Anthropic
        if self.config.ANTHROPIC_API_KEY:
            os.environ['ANTHROPIC_API_KEY'] = self.config.ANTHROPIC_API_KEY
        
        # Google
        if self.config.GOOGLE_API_KEY:
            os.environ['GOOGLE_API_KEY'] = self.config.GOOGLE_API_KEY
        
        # Groq
        if self.config.GROQ_API_KEY:
            os.environ['GROQ_API_KEY'] = self.config.GROQ_API_KEY
        
        # OpenRouter (備用)
        if self.config.OPENROUTER_API_KEY:
            os.environ['OPENROUTER_API_KEY'] = self.config.OPENROUTER_API_KEY
    
    async def call_model(self, model_key: str, prompt: str, max_retries: int = None) -> Dict[str, Any]:
        """
        調用指定的LLM模型 (使用aisuite)
        
        Args:
            model_key: 模型標識符 (如 'openai/gpt-4o')
            prompt: 輸入提示
            max_retries: 最大重試次數
        
        Returns:
            包含回應內容和元數據的字典
        """
        if max_retries is None:
            max_retries = self.config.MAX_RETRIES
        
        if not self.config.is_model_available(model_key):
            return {
                'success': False,
                'error': f"Model {model_key} is not available",
                'response': None,
                'model': model_key
            }
        
        model_config = self.config.get_model_config(model_key)
        provider = model_config['provider']
        model_name = model_config['model_name']
        
        # aisuite 格式: "provider:model"
        aisuite_model = f"{provider}:{model_name}"
        
        for attempt in range(max_retries + 1):
            try:
                # 使用aisuite統一接口
                messages = [
                    {"role": "system", "content": "請用台灣習慣的中文回覆。"},
                    {"role": "user", "content": prompt}
                ]
                
                response = self.client.chat.completions.create(
                    model=aisuite_model,
                    messages=messages,
                    max_tokens=2000,
                    temperature=0.3
                )
                
                return {
                    'success': True,
                    'response': response.choices[0].message.content,
                    'model': model_key,
                    'provider': provider,
                    'usage': getattr(response, 'usage', None)
                }
            
            except Exception as e:
                error_str = str(e)
                
                # 檢查是否為速率限制錯誤
                if "429" in error_str or "Rate limit" in error_str:
                    if attempt == max_retries:
                        return {
                            'success': False,
                            'error': f"Rate limit exceeded after {max_retries} retries: {error_str}",
                            'response': None,
                            'model': model_key,
                            'provider': provider
                        }
                    # 速率限制時等待
                    wait_time = 10 + (attempt * 5)  # 減少等待時間，因為付費API限制較少
                    print(f"遇到速率限制，等待 {wait_time} 秒後重試... (嘗試 {attempt + 1}/{max_retries + 1})")
                    await asyncio.sleep(wait_time)
                else:
                    if attempt == max_retries:
                        return {
                            'success': False,
                            'error': str(e),
                            'response': None,
                            'model': model_key,
                            'provider': provider
                        }
                    # 其他錯誤使用短暫延遲
                    await asyncio.sleep(2)
        
        return {
            'success': False,
            'error': 'Max retries exceeded',
            'response': None,
            'model': model_key,
            'provider': provider
        }
    
    def parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """解析JSON回應"""
        try:
            # 嘗試直接解析
            return json.loads(response_text)
        except json.JSONDecodeError:
            # 嘗試提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # 如果無法解析，返回錯誤信息
            return {
                'error': 'Failed to parse JSON response',
                'raw_response': response_text
            }
    
    def get_available_models(self) -> Dict[str, Dict]:
        """獲取所有可用模型"""
        return self.config.AVAILABLE_MODELS
    
    def test_connection(self, model_key: str = None) -> bool:
        """測試連接"""
        if model_key is None:
            model_key = 'openai/gpt-4o-mini'  # 使用便宜的模型測試
        
        try:
            response = asyncio.run(self.call_model(model_key, "Hello"))
            return response['success']
        except Exception:
            return False 