import os
import httpx
import json
from openai import OpenAI
from typing import List, Dict

class AIEngine:
    def __init__(self, llama_key: str, nemotron_key: str, whisper_key: str):
        self.llama_key = llama_key
        self.nemotron_key = nemotron_key
        self.whisper_key = whisper_key
        self.base_url = "https://integrate.api.nvidia.com/v1"
        
        self.intent_model = "meta/llama-3.1-70b-instruct"
        self.insight_model = "nvidia/nemotron-nano-9b-v2"
        self.embed_model = "snowflake/arctic-embed-l"

    def _get_client(self, api_key: str):
        return OpenAI(base_url=self.base_url, api_key=api_key)

    def classify_intent(self, search_terms: List[str]) -> List[str]:
        """Classifies each search term as HIGH, MEDIUM, or LOW intent with batching for high speed."""
        if not search_terms:
            return []
            
        client = self._get_client(self.llama_key)
        all_intents = []
        
        # Batching: Process 50 terms at a time for maximum speed and reliability
        batch_size = 50
        for i in range(0, len(search_terms), batch_size):
            batch = search_terms[i:i + batch_size]
            prompt = (
                "You are a Google Ads Specialist for a jewelry brand. "
                "Classify the following search terms based on purchase intent (HIGH, MEDIUM, LOW):\n\n"
                "- HIGH: Terms like 'buy', 'price', 'engagement ring store near me', 'diamond ring 1 carat'.\n"
                "- MEDIUM: Comparison terms, 'best engagement rings', 'diamond vs moissanite'.\n"
                "- LOW: Informational, 'what is 14k gold', 'how to clean jewelry', 'free ring sizer'.\n\n"
                "Return ONLY a JSON list of strings representing the classifications for these items.\n"
                f"Batch: {json.dumps(batch)}"
            )
            
            try:
                response = client.chat.completions.create(
                    model=self.intent_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=1024,
                )
                content = response.choices[0].message.content.strip()
                
                # Extract JSON list
                start_idx = content.find('[')
                end_idx = content.rfind(']')
                if start_idx != -1 and end_idx != -1:
                    batch_intents = json.loads(content[start_idx:end_idx+1])
                    # Ensure the batch results match the batch size
                    if len(batch_intents) == len(batch):
                        all_intents.extend(batch_intents)
                    else:
                        # Padded fallback if length mismatch
                        all_intents.extend(["UNKNOWN"] * (len(batch) - len(batch_intents)) + batch_intents[:len(batch)])
                else:
                    all_intents.extend(["UNKNOWN"] * len(batch))
                    
            except Exception as e:
                print(f"Error in batch {i}: {e}")
                all_intents.extend(["UNKNOWN"] * len(batch))
                
        return all_intents

    def generate_insights(self, report_summary: Dict) -> str:
        """Generates an executive summary and recommendations."""
        client = self._get_client(self.nemotron_key)
        prompt = (
            "Based on the following Google Ads Search Term Audit summary, "
            "generate an executive summary with specific insights and an action plan. "
            "Focus on efficiency and spend optimization for a jewelry retailer.\n\n"
            f"Summary Data: {json.dumps(report_summary)}\n\n"
            "Expected format:\n"
            "1. Executive Summary\n"
            "2. Critical Issues\n"
            "3. Recommendations\n"
            "4. Action Plan"
        )
        
        try:
            response = client.chat.completions.create(
                model=self.insight_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=4096,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating insights: {e}")
            return "Unable to generate insights at this time."

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for search terms for clustering."""
        client = self._get_client(self.llama_key) # Using Llama key for embeddings for now
        try:
            response = client.embeddings.create(
                input=texts,
                model=self.embed_model
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            return []
