#!/usr/bin/env python3
"""
多層次LLM邏輯題驗證系統 - 演示模式
不需要真實API，用模擬數據展示系統工作流程
"""

import asyncio
import json
import time
import random
from colorama import init, Fore, Style
from typing import Dict, Any, List

# 初始化colorama
init()

class DemoLLMClient:
    """演示模式的模擬LLM客戶端"""
    
    def __init__(self):
        self.demo_responses = {
            "logic_question": {
                "openai/gpt-4o": {
                    "reasoning": "根據邏輯推理，小明說'如果下雨就不去公園'，但他今天去了公園，所以今天沒有下雨。這是一個否定後件(modus tollens)的邏輯推理。",
                    "answer": "今天沒有下雨"
                },
                "openai/gpt-4o-mini": {
                    "reasoning": "使用反向推理：如果今天下雨→小明不去公園。但小明去了公園，所以今天沒下雨。",
                    "answer": "沒有下雨"
                },
                "anthropic/claude-3-5-sonnet": {
                    "reasoning": "這是經典的邏輯三段論。前提：下雨→不去公園；事實：去了公園；結論：沒下雨。",
                    "answer": "今天沒有下雨"
                }
            },
            "verification": {
                "correct": {
                    "verdict": "Correct",
                    "error_reason": "答案正確，邏輯推理嚴謹，符合否定後件的推理規則"
                },
                "incorrect": {
                    "verdict": "Incorrect", 
                    "error_reason": "推理過程有誤，未正確應用邏輯規則"
                }
            },
            "correction": {
                "original_error_acknowledgment": "我理解了原先的邏輯推理錯誤",
                "revised_reasoning": "重新分析：這是否定後件的邏輯推理，如果下雨則不去公園，去了公園說明沒下雨",
                "revised_answer": "今天沒有下雨"
            },
            "decision": {
                "final_answer": "今天沒有下雨",
                "reasoning": "綜合分析三個模型的回答，都指向同一結論。這是標準的否定後件邏輯推理，結論可靠。",
                "evidence_analysis": "所有模型都正確識別了這是否定後件推理，答案一致性高，邏輯嚴謹。"
            }
        }
    
    async def call_model(self, model_key: str, prompt: str) -> Dict[str, Any]:
        """模擬API調用"""
        # 模擬API延遲
        await asyncio.sleep(random.uniform(1, 3))
        
        # 模擬不同的回應
        if "邏輯" in prompt or "下雨" in prompt or "公園" in prompt:
            if model_key in self.demo_responses["logic_question"]:
                response_data = self.demo_responses["logic_question"][model_key]
                response_text = json.dumps(response_data, ensure_ascii=False)
            else:
                response_text = json.dumps({
                    "reasoning": f"[{model_key}模擬回應] 這是一個邏輯推理問題...",
                    "answer": "今天沒有下雨"
                }, ensure_ascii=False)
        else:
            response_text = json.dumps({
                "reasoning": f"[{model_key}模擬回應] 根據分析...",
                "answer": "示例答案"
            }, ensure_ascii=False)
        
        return {
            'success': True,
            'response': response_text,
            'model': model_key,
            'provider': model_key.split('/')[0],
            'usage': {'input_tokens': 100, 'output_tokens': 50}
        }

class DemoAnsweringLayer:
    """演示版回答層"""
    
    def __init__(self):
        self.demo_client = DemoLLMClient()
    
    async def process_question(self, question: str, models: List[str] = None) -> List[Dict[str, Any]]:
        if models is None:
            models = ['openai/gpt-4o', 'openai/gpt-4o-mini']
        
        print(f"{Fore.CYAN}📝 回答層處理中...{Style.RESET_ALL}")
        
        results = []
        for model in models:
            print(f"  正在處理模型: {model}")
            
            response = await self.demo_client.call_model(model, question)
            if response['success']:
                parsed = json.loads(response['response'])
                results.append({
                    'model': model,
                    'success': True,
                    'answer': parsed['answer'],
                    'reasoning': parsed['reasoning'],
                    'raw_response': response['response']
                })
            
            await asyncio.sleep(0.5)
        
        return results

class DemoVerificationLayer:
    """演示版驗證層"""
    
    def __init__(self):
        self.demo_client = DemoLLMClient()
    
    async def verify_answers(self, question: str, answers: List[Dict[str, Any]], 
                           verification_models: List[str] = None) -> List[Dict[str, Any]]:
        if verification_models is None:
            verification_models = ['openai/gpt-4o', 'openai/gpt-4o-mini']
        
        print(f"{Fore.CYAN}🔍 驗證層處理中...{Style.RESET_ALL}")
        
        verification_results = []
        for answer in answers:
            if answer['success']:
                for verification_model in verification_models:
                    # 交叉驗證：不讓模型驗證自己
                    if verification_model != answer['model']:
                        print(f"  正在使用 {verification_model} 驗證 {answer['model']} 的答案")
                        
                        # 模擬驗證結果
                        await asyncio.sleep(1)
                        verification_data = self.demo_client.demo_responses["verification"]["correct"]
                        
                        verification_results.append({
                            'verification_model': verification_model,
                            'target_model': answer['model'],
                            'success': True,
                            'verdict': verification_data['verdict'],
                            'error_reason': verification_data['error_reason']
                        })
        
        return verification_results

class DemoCorrectionLayer:
    """演示版訂正層"""
    
    def __init__(self):
        self.demo_client = DemoLLMClient()
    
    async def correct_answers(self, question: str, original_answers: List[Dict[str, Any]], 
                            verification_results: List[Dict[str, Any]], 
                            correction_model: str = None) -> List[Dict[str, Any]]:
        
        print(f"{Fore.CYAN}🔧 訂正層處理中...{Style.RESET_ALL}")
        
        correction_results = []
        
        for answer in original_answers:
            if answer['success']:
                # 檢查是否需要訂正
                needs_correction = False
                for verification in verification_results:
                    if (verification['target_model'] == answer['model'] and 
                        verification.get('verdict') == 'Incorrect'):
                        needs_correction = True
                        break
                
                if needs_correction:
                    print(f"  正在訂正 {answer['model']} 的答案")
                    await asyncio.sleep(1)
                    
                    correction_data = self.demo_client.demo_responses["correction"]
                    correction_results.append({
                        'model': answer['model'],
                        'needs_correction': True,
                        'success': True,
                        'original_answer': answer['answer'],
                        'revised_answer': correction_data['revised_answer'],
                        'original_reasoning': answer['reasoning'],
                        'revised_reasoning': correction_data['revised_reasoning'],
                        'original_error_acknowledgment': correction_data['original_error_acknowledgment'],
                        'correction_applied': True
                    })
                else:
                    correction_results.append({
                        'model': answer['model'],
                        'needs_correction': False,
                        'original_answer': answer['answer'],
                        'revised_answer': answer['answer'],
                        'original_reasoning': answer['reasoning'],
                        'revised_reasoning': answer['reasoning'],
                        'correction_applied': False
                    })
        
        return correction_results

class DemoDecisionLayer:
    """演示版決策層"""
    
    def __init__(self):
        self.demo_client = DemoLLMClient()
    
    async def make_final_decision(self, question: str, 
                                original_answers: List[Dict[str, Any]],
                                verification_results: List[Dict[str, Any]],
                                correction_results: List[Dict[str, Any]],
                                decision_model: str = None) -> Dict[str, Any]:
        
        print(f"{Fore.CYAN}⚖️ 決策層處理中...{Style.RESET_ALL}")
        await asyncio.sleep(2)
        
        decision_data = self.demo_client.demo_responses["decision"]
        
        # 計算信心度和共識度
        correct_count = sum(1 for v in verification_results if v.get('verdict') == 'Correct')
        total_verifications = len(verification_results)
        confidence = correct_count / total_verifications if total_verifications > 0 else 1.0
        
        return {
            'success': True,
            'decision_model': decision_model or 'openai/gpt-4o',
            'final_answer': decision_data['final_answer'],
            'reasoning': decision_data['reasoning'],
            'evidence_analysis': decision_data['evidence_analysis'],
            'answer_confidence': confidence,
            'verification_consensus': {
                'consensus_rate': confidence,
                'agreement_level': 'High Consensus' if confidence >= 0.8 else 'Moderate Consensus',
                'verdict_distribution': {'Correct': correct_count, 'Incorrect': total_verifications - correct_count}
            }
        }

class DemoSystemCoordinator:
    """演示版系統協調器"""
    
    def __init__(self):
        self.answering_layer = DemoAnsweringLayer()
        self.verification_layer = DemoVerificationLayer()
        self.correction_layer = DemoCorrectionLayer()
        self.decision_layer = DemoDecisionLayer()
    
    async def process_question(self, question: str, verbose: bool = True) -> Dict[str, Any]:
        """處理問題的完整流程"""
        
        if verbose:
            print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}🚀 開始處理問題{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}📋 問題：{question}{Style.RESET_ALL}\n")
        
        try:
            # 第一層：回答層
            if verbose:
                print(f"{Fore.YELLOW}🔄 第一層：多模型回答{Style.RESET_ALL}")
            answering_results = await self.answering_layer.process_question(question)
            
            # 第二層：驗證層
            if verbose:
                print(f"\n{Fore.YELLOW}🔄 第二層：交叉驗證{Style.RESET_ALL}")
            verification_results = await self.verification_layer.verify_answers(question, answering_results)
            
            # 第三層：訂正層
            if verbose:
                print(f"\n{Fore.YELLOW}🔄 第三層：錯誤訂正{Style.RESET_ALL}")
            correction_results = await self.correction_layer.correct_answers(question, answering_results, verification_results)
            
            # 第四層：決策層
            if verbose:
                print(f"\n{Fore.YELLOW}🔄 第四層：最終決策{Style.RESET_ALL}")
            decision_result = await self.decision_layer.make_final_decision(question, answering_results, verification_results, correction_results)
            
            # 整理結果
            result = {
                'layer_results': {
                    'answering': answering_results,
                    'verification': verification_results,
                    'correction': correction_results,
                    'decision': decision_result
                },
                'summary': {
                    'overall_success': decision_result['success'],
                    'total_models_used': len(answering_results),
                    'verification_count': len(verification_results),
                    'corrections_applied': sum(1 for c in correction_results if c.get('correction_applied', False))
                }
            }
            
            if verbose:
                self.print_results(result)
            
            return result
        
        except Exception as e:
            if verbose:
                print(f"{Fore.RED}❌ 處理過程中發生錯誤: {str(e)}{Style.RESET_ALL}")
            
            return {
                'layer_results': {'decision': {'success': False, 'error': str(e)}},
                'summary': {'overall_success': False}
            }
    
    def print_results(self, result: Dict[str, Any]):
        """打印結果"""
        print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}📊 處理結果{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        
        decision = result['layer_results']['decision']
        if decision['success']:
            print(f"{Fore.GREEN}✅ 處理成功{Style.RESET_ALL}")
            print(f"{Fore.BLUE}📋 最終答案: {decision['final_answer']}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}📊 信心程度: {decision['answer_confidence']:.2%}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}🤝 驗證共識度: {decision['verification_consensus']['consensus_rate']:.2%}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}📈 共識程度: {decision['verification_consensus']['agreement_level']}{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}🧠 決策推理:{Style.RESET_ALL}")
            print(f"{decision['reasoning']}")
            
            print(f"\n{Fore.CYAN}📋 證據分析:{Style.RESET_ALL}")
            print(f"{decision['evidence_analysis']}")
        else:
            print(f"{Fore.RED}❌ 處理失敗: {decision.get('error', '未知錯誤')}{Style.RESET_ALL}")

async def run_demo():
    """運行演示"""
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}🎭 多層次LLM邏輯驗證系統 - 演示模式{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}📋 演示說明:{Style.RESET_ALL}")
    print(f"• 這是模擬模式，不需要真實API密鑰")
    print(f"• 展示完整的四層處理流程")
    print(f"• 使用預設的示例回應")
    print(f"• 幫助您理解系統工作原理")
    
    demo_questions = [
        '小明說："如果今天下雨，我就不去公園。"今天小明去了公園。請問今天是否下雨？',
        '所有鳥都會飛。企鵝是鳥。企鵝會飛嗎？',
        '如果A大於B，B大於C，那麼A和C的關係是什麼？'
    ]
    
    system = DemoSystemCoordinator()
    
    for i, question in enumerate(demo_questions, 1):
        print(f"\n{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🧪 演示 {i}: 邏輯推理測試{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}{'='*60}{Style.RESET_ALL}")
        
        result = await system.process_question(question, verbose=True)
        
        if i < len(demo_questions):
            print(f"\n{Fore.BLUE}按Enter鍵繼續下一個演示...{Style.RESET_ALL}")
            input()

def print_api_guide():
    """打印API申請指南"""
    print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}🔑 API密鑰申請指南{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    
    guides = [
        {
            'name': 'OpenAI (推薦)',
            'url': 'https://platform.openai.com/api-keys',
            'features': '穩定可靠，質量高，適合大規模實驗',
            'cost': 'gpt-4o-mini: $0.15/1M tokens (便宜)',
            'steps': [
                '1. 註冊OpenAI帳號',
                '2. 前往API密鑰頁面',
                '3. 創建新的API密鑰',
                '4. 複製密鑰到.env文件'
            ]
        },
        {
            'name': 'Google Gemini (免費額度大)',
            'url': 'https://ai.google.dev/',
            'features': '免費額度較大，速度快',
            'cost': '免費額度 + 付費選項',
            'steps': [
                '1. 使用Google帳號登入',
                '2. 前往Google AI Studio',
                '3. 獲取API密鑰',
                '4. 配置到環境變量'
            ]
        },
        {
            'name': 'Anthropic Claude',
            'url': 'https://console.anthropic.com/',
            'features': '邏輯推理能力強，安全性高',
            'cost': '$3/1M input tokens',
            'steps': [
                '1. 註冊Anthropic帳號',
                '2. 前往控制台',
                '3. 獲取API密鑰',
                '4. 配置環境變量'
            ]
        }
    ]
    
    for guide in guides:
        print(f"\n{Fore.CYAN}🔹 {guide['name']}{Style.RESET_ALL}")
        print(f"   網址: {guide['url']}")
        print(f"   特點: {guide['features']}")
        print(f"   費用: {guide['cost']}")
        print(f"   步驟:")
        for step in guide['steps']:
            print(f"     {step}")

if __name__ == "__main__":
    print(f"{Fore.BLUE}選擇模式:{Style.RESET_ALL}")
    print(f"1. 運行演示 (推薦)")
    print(f"2. 查看API申請指南")
    print(f"3. 兩者都要")
    
    choice = input(f"\n請輸入選擇 (1/2/3): ").strip()
    
    if choice in ['1', '3']:
        asyncio.run(run_demo())
    
    if choice in ['2', '3']:
        print_api_guide()
    
    print(f"\n{Fore.GREEN}感謝使用演示模式！{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}準備好API密鑰後，可以運行: python test_aisuite.py{Style.RESET_ALL}") 