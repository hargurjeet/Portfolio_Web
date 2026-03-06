from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
import requests
import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

class FireworksLLM(LLM):
    """Fireworks AI LLM implementation"""
    
    model: str = "accounts/fireworks/models/qwen3-8b"
    temperature: float = 0.6
    max_tokens: int = 1024
    top_p: float = 1
    top_k: int = 40
    presence_penalty: float = 0
    frequency_penalty: float = 0
    api_key: str = ""
    streaming: bool = False
    callbacks: list = []
    # Add option to hide think blocks
    hide_think_blocks: bool = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set API key from env if not provided in kwargs
        if not self.api_key:
            self.api_key = os.getenv('FIREWORKS_API_KEY', '')
    
    def _clean_response(self, text: str) -> str:
        """Remove think blocks from the response"""
        if self.hide_think_blocks:
            # Remove everything between <think> and </think> tags including the tags themselves
            cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
            # Also remove any leftover whitespace from the removal
            cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
            return cleaned.strip()
        return text
    
    @property
    def _llm_type(self) -> str:
        return "fireworks"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager = None,
        **kwargs: Any,
    ) -> str:
        """Call the Fireworks API and return the response."""
        
        try:
            # Handle both string prompts and message lists
            if isinstance(prompt, str):
                messages = [{"role": "user", "content": prompt}]
            else:
                # Assume it's already a list of messages
                messages = prompt
            
            url = "https://api.fireworks.ai/inference/v1/chat/completions"
            
            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "presence_penalty": self.presence_penalty,
                "frequency_penalty": self.frequency_penalty,
            }
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Make the API call
            response = requests.post(url, headers=headers, json=payload)
            
            # Check for errors
            if response.status_code != 200:
                error_msg = f"Fireworks API error: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
            
            # Parse response
            result = response.json()
            
            # Extract the message content
            if 'choices' in result and len(result['choices']) > 0:
                raw_response = result['choices'][0]['message']['content']
                # Clean the response by removing think blocks
                return self._clean_response(raw_response)
            else:
                raise Exception("Unexpected API response format: no choices found")
                
        except Exception as e:
            raise Exception(f"Error calling Fireworks API: {str(e)}")
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "hide_think_blocks": self.hide_think_blocks,
        }