"""
多層次LLM邏輯題驗證系統 - 配置文件
"""
import os
from dotenv import load_dotenv
from typing import Dict, List

# 載入環境變量
load_dotenv()

class Config:
    """系統配置類"""
    
    # API 密鑰
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    COHERE_API_KEY = os.getenv('COHERE_API_KEY')
    
    # 系統配置
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 5))
    TIMEOUT_SECONDS = int(os.getenv('TIMEOUT_SECONDS', 60))
    RATE_LIMIT_DELAY = int(os.getenv('RATE_LIMIT_DELAY', 30))  # 速率限制延遲秒數
    
    # 可用的LLM模型配置 (aisuite格式)
    AVAILABLE_MODELS = {
        # OpenAI模型 (推薦用於大規模實驗)
        'openai': {
            'gpt-4o': {'provider': 'openai', 'model_name': 'gpt-4o'},
            'gpt-4o-mini': {'provider': 'openai', 'model_name': 'gpt-4o-mini'},
            'gpt-4-turbo': {'provider': 'openai', 'model_name': 'gpt-4-turbo'},
            'gpt-3.5-turbo': {'provider': 'openai', 'model_name': 'gpt-3.5-turbo'}
        },
        # Anthropic模型
        'anthropic': {
            'claude-3-5-sonnet': {'provider': 'anthropic', 'model_name': 'claude-3-5-sonnet-20241022'},
            'claude-3-haiku': {'provider': 'anthropic', 'model_name': 'claude-3-haiku-20240307'},
            'claude-3-opus': {'provider': 'anthropic', 'model_name': 'claude-3-opus-20240229'}
        },
        # Google模型
        'google': {
            'gemini-pro': {'provider': 'google', 'model_name': 'gemini-1.5-pro'},
            'gemini-flash': {'provider': 'google', 'model_name': 'gemini-1.5-flash'}
        },
        # Groq模型 (免費且快速) - 僅保留可用模型
        'groq': {
            'llama-3-70b-8192': {'provider': 'groq', 'model_name': 'llama3-70b-8192'},
            'llama-3.3-70b': {'provider': 'groq', 'model_name': 'llama-3.3-70b-versatile'}
        },
        # OpenRouter模型 (備用選項)
        'openrouter': {
            'deepseek-r1': {'provider': 'openrouter', 'model_name': 'deepseek/deepseek-r1-0528-qwen3-8b:free'},
            'gemini-2-flash': {'provider': 'openrouter', 'model_name': 'google/gemini-2.0-flash-exp:free'},
            'mistral-7b': {'provider': 'openrouter', 'model_name': 'mistralai/mistral-7b-instruct:free'}
        }
    }
    
    # 默認使用的模型組合（Groq模型 - 免費且快速）
    DEFAULT_ANSWERING_MODELS = [
        'groq/llama-3-70b-8192',
        'groq/llama-3.3-70b'
    ]
    
    DEFAULT_VERIFICATION_MODELS = [
        'groq/llama-3-70b-8192',
        'groq/llama-3.3-70b'
    ]
    
    # 限制模式配置（單模型測試）
    LIMITED_MODE_ANSWERING_MODELS = ['groq/llama-3-70b-8192']
    LIMITED_MODE_VERIFICATION_MODELS = ['groq/llama-3-70b-8192']
    
    DEFAULT_CORRECTION_MODEL = 'groq/llama-3-70b-8192'
    DEFAULT_DECISION_MODEL = 'groq/llama-3.3-70b'
    
    # 高性能配置（用於大規模實驗）
    HIGH_PERFORMANCE_ANSWERING_MODELS = [
        'openai/gpt-4o',
        'anthropic/claude-3-5-sonnet',
        'google/gemini-pro'
    ]
    
    HIGH_PERFORMANCE_VERIFICATION_MODELS = [
        'openai/gpt-4o',
        'anthropic/claude-3-5-sonnet'
    ]
    
    # 文件路徑
    PROMPTS_DIR = 'prompts'
    QUESTIONS_DIR = '2星題目'
    RESULTS_DIR = 'results'
    
    @classmethod
    def get_model_config(cls, model_key: str) -> Dict:
        """獲取模型配置"""
        provider, model = model_key.split('/')
        return cls.AVAILABLE_MODELS[provider][model]
    
    @classmethod
    def is_model_available(cls, model_key: str) -> bool:
        """檢查模型是否可用"""
        try:
            provider, model = model_key.split('/')
            return (provider in cls.AVAILABLE_MODELS and 
                   model in cls.AVAILABLE_MODELS[provider])
        except:
            return False 