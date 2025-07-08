#!/usr/bin/env python3
"""
Gemini Models Extraction Script for LlamaIndex
LlamaIndexで使用可能なGeminiモデルを抽出・分析するスクリプト
"""

import os
import sys
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

# 環境変数の読み込み
load_dotenv()

class GeminiModelExtractor:
    """Geminiモデルの抽出・分析クラス"""
    
    def __init__(self):
        """初期化"""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEYが設定されていません。.envファイルを確認してください。")
        
        # Google GenAI APIの設定
        genai.configure(api_key=self.api_key)
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """利用可能なGeminiモデルを取得"""
        try:
            models = []
            for model in genai.list_models():
                model_info = {
                    "name": model.name,
                    "display_name": model.display_name,
                    "description": model.description,
                    "version": getattr(model, 'version', 'N/A'),
                    "input_token_limit": getattr(model, 'input_token_limit', 'N/A'),
                    "output_token_limit": getattr(model, 'output_token_limit', 'N/A'),
                    "supported_generation_methods": getattr(model, 'supported_generation_methods', [])
                }
                models.append(model_info)
            return models
        except Exception as e:
            print(f"モデル取得エラー: {e}")
            return []
    
    def categorize_models(self, models: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """モデルをジャンル別に分類"""
        categories = {
            "text_generation": [],    # テキスト生成・チャット用
            "multimodal": [],         # マルチモーダル（画像・動画対応）
            "embedding": [],          # 埋め込み用
            "image_generation": [],   # 画像生成
            "experimental": [],       # 実験的モデル
            "other": []              # その他
        }
        
        for model in models:
            model_name = model["name"].lower()
            description = model["description"].lower()
            display_name = model["display_name"].lower()
            
            # 分類ロジック
            if "embedding" in model_name:
                categories["embedding"].append(model)
            elif "imagen" in model_name or "image" in description:
                categories["image_generation"].append(model)
            elif "vision" in description or "image" in description or "multimodal" in description:
                categories["multimodal"].append(model)
            elif "exp" in model_name or "experimental" in description or "preview" in model_name:
                categories["experimental"].append(model)
            elif "generatecontent" in str(model.get("supported_generation_methods", [])).lower():
                categories["text_generation"].append(model)
            else:
                categories["other"].append(model)
        
        return categories
    
    def get_llamaindex_compatible_models(self, categorized: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[str]]:
        """LlamaIndexで使用可能なモデル名を抽出"""
        compatible = {
            "llm_models": [],
            "embedding_models": [],
            "multimodal_models": []
        }
        
        # LLM用モデル（テキスト生成 + マルチモーダル）
        for model in categorized["text_generation"] + categorized["multimodal"]:
            model_name = model["name"]
            if any(pattern in model_name for pattern in ["gemini", "models/gemini"]):
                compatible["llm_models"].append(model_name)
        
        # 埋め込みモデル
        for model in categorized["embedding"]:
            model_name = model["name"]
            if "gemini" in model_name:
                compatible["embedding_models"].append(model_name)
        
        # マルチモーダルモデル
        for model in categorized["multimodal"]:
            model_name = model["name"]
            if "gemini" in model_name:
                compatible["multimodal_models"].append(model_name)
        
        return compatible
    
    def generate_usage_examples(self, compatible_models: Dict[str, List[str]]) -> str:
        """使用例を生成"""
        examples = []
        
        # LLM使用例
        if compatible_models["llm_models"]:
            model_name = compatible_models["llm_models"][0]
            examples.append(f"""
# LLMモデルの使用例
from llama_index.llms.gemini import Gemini

llm = Gemini(model_name="{model_name}", api_key="YOUR_API_KEY")
response = llm.complete("こんにちは")
print(response.text)
""")
        
        # 埋め込みモデル使用例
        if compatible_models["embedding_models"]:
            model_name = compatible_models["embedding_models"][0]
            examples.append(f"""
# 埋め込みモデルの使用例
from llama_index.embeddings.gemini import GeminiEmbedding

embedding = GeminiEmbedding(model_name="{model_name}", api_key="YOUR_API_KEY")
embed_result = embedding.get_text_embedding("テストテキスト")
print(f"埋め込み次元数: {{len(embed_result)}}")
""")
        
        # マルチモーダルモデル使用例
        if compatible_models["multimodal_models"]:
            model_name = compatible_models["multimodal_models"][0]
            examples.append(f"""
# マルチモーダルモデルの使用例
from llama_index.llms.gemini import Gemini
from llama_index.core.schema import ImageDocument

llm = Gemini(model_name="{model_name}", api_key="YOUR_API_KEY")
# 画像付きクエリの例
response = llm.complete("この画像について説明してください")
""")
        
        return "\n".join(examples)
    
    def save_results(self, results: Dict[str, Any], filename: str = "gemini_models_analysis.json"):
        """結果をJSONファイルに保存"""
        try:
            # modelsディレクトリに保存
            models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
            os.makedirs(models_dir, exist_ok=True)
            
            filepath = os.path.join(models_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"結果を {filepath} に保存しました")
        except Exception as e:
            print(f"ファイル保存エラー: {e}")
    
    def run_analysis(self, save_to_file: bool = True):
        """メインの分析処理"""
        print("=== Gemini Models Analysis for LlamaIndex ===")
        print("利用可能なGeminiモデルを取得中...")
        
        # 利用可能なモデルを取得
        all_models = self.get_available_models()
        if not all_models:
            print("モデルの取得に失敗しました")
            return
        
        print(f"取得したモデル数: {len(all_models)}")
        
        # ジャンル別に分類
        categorized = self.categorize_models(all_models)
        
        # LlamaIndex互換モデルを抽出
        compatible_models = self.get_llamaindex_compatible_models(categorized)
        
        # 結果の表示
        print("\n=== ジャンル別分類 ===")
        for category, models in categorized.items():
            print(f"\n{category.upper()} ({len(models)}個):")
            for model in models[:5]:  # 最初の5個を表示
                print(f"  - {model['name']}")
                print(f"    説明: {model['description'][:80]}...")
            if len(models) > 5:
                print(f"    ... 他{len(models)-5}個")
        
        print("\n=== LlamaIndex互換モデル ===")
        for model_type, models in compatible_models.items():
            print(f"\n{model_type.upper()} ({len(models)}個):")
            for model in models[:3]:  # 最初の3個を表示
                print(f"  - {model}")
            if len(models) > 3:
                print(f"    ... 他{len(models)-3}個")
        
        # 使用例を生成
        print("\n=== 使用例 ===")
        examples = self.generate_usage_examples(compatible_models)
        print(examples)
        
        # 結果をまとめる
        analysis_results = {
            "timestamp": "2025-07-08",
            "total_models": len(all_models),
            "genre_categorized": {
                category: [{"name": model["name"], "display_name": model["display_name"]} 
                          for model in models]
                for category, models in categorized.items()
            },
            "llamaindex_compatible": compatible_models,
            "usage_examples": examples
        }
        
        # ファイルに保存
        if save_to_file:
            self.save_results(analysis_results)
        
        return analysis_results


def main():
    """メイン関数"""
    try:
        extractor = GeminiModelExtractor()
        
        # 引数の処理
        save_to_file = "--no-save" not in sys.argv
        
        # 分析実行
        results = extractor.run_analysis(save_to_file=save_to_file)
        
        print("\n=== 分析完了 ===")
        if save_to_file:
            print("詳細な結果はmodels/gemini_models_analysis.jsonファイルに保存されました")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()