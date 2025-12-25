import json
import os
import shutil
from dotenv import load_dotenv
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Tuple
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_huggingface import HuggingFaceEmbeddings
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

# Constants
TAXONOMY_FILE = "taxonomy.json"
SIMILARITY_THRESHOLD = 0.78 # As per spec

# --- 1. TAXONOMY & EMBEDDING MANAGER ---
class TaxonomyManager:
    def __init__(self, embedding_model_name="all-MiniLM-L6-v2"):
        self.taxonomy_path = TAXONOMY_FILE
        self.topics = {} # {topic_name: {examples: [], embedding: np.array, created_at: str}}
        self.embedding_model = HuggingFaceEmbeddings(model_name=embedding_model_name)
        self.load_taxonomy()

    def load_taxonomy(self):
        if os.path.exists(self.taxonomy_path):
            with open(self.taxonomy_path, "r") as f:
                data = json.load(f)
                # Restore numpy arrays from lists
                for topic, details in data.items():
                    details["embedding"] = np.array(details["embedding"])
                self.topics = data
            print(f"[TAXONOMY] Loaded {len(self.topics)} topics.")
        else:
            print("[TAXONOMY] No existing taxonomy found. Starting fresh.")
            self.topics = {}

    def save_taxonomy(self):
        # Convert numpy arrays to lists for JSON serialization
        serializable_topics = {}
        for topic, details in self.topics.items():
            serializable_topics[topic] = {
                "examples": details["examples"],
                "embedding": details["embedding"].tolist(),
                "created_at": details["created_at"]
            }
        
        # Backup
        if os.path.exists(self.taxonomy_path):
            shutil.copy(self.taxonomy_path, self.taxonomy_path + ".bak")
            
        with open(self.taxonomy_path, "w") as f:
            json.dump(serializable_topics, f, indent=2)

    def get_topic_embedding(self, text: str) -> np.ndarray:
        return np.array(self.embedding_model.embed_query(text))

    def map_extracted_topic(self, raw_topic: str) -> str:
        """
        Matches a raw extracted topic string to an existing taxonomy topic.
        Returns the existing topic name if match found, else returns the raw_topic (which implies it's new).
        """
        if not self.topics:
            return raw_topic
        
        raw_embedding = self.get_topic_embedding(raw_topic).reshape(1, -1)
        
        # Calculate similarity with all existing topics
        existing_topics = list(self.topics.keys())
        existing_embeddings = np.array([self.topics[t]["embedding"] for t in existing_topics])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(raw_embedding, existing_embeddings)[0]
        
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        best_topic = existing_topics[best_idx]
        
        # print(f"[DEBUG] '{raw_topic}' vs '{best_topic}' score: {best_score:.3f}")
        
        if best_score >= SIMILARITY_THRESHOLD:
            return best_topic
        else:
            return raw_topic

    def add_new_topic(self, topic_name: str):
        if topic_name not in self.topics:
            emb = self.get_topic_embedding(topic_name)
            self.topics[topic_name] = {
                "examples": [topic_name],
                "embedding": emb,
                "created_at": datetime.now().isoformat()
            }

# --- 2. AGENT (GROQ) ---
class Agent:
    def __init__(self):
        self.key = os.environ.get("GROQ_API_KEY")
        if not self.key:
            raise ValueError("GROQ_API_KEY not found in env")
            
        # Prioritized list of models to try
        self.models = [
            "llama-3.3-70b-versatile",  # Best quality
            "llama-3.1-8b-instant",     # Fast fallback
            "mixtral-8x7b-32768",       # Good alternative
            "gemma2-9b-it"              # Backup
        ]
        
        # Extraction Prompt
        self.extract_prompt = ChatPromptTemplate.from_template("""
        You are an AI that extracts user complaints and feature requests from reviews.
        Return ONLY a JSON list of normalized topics (strings).
        
        Reviews:
        {reviews_text}
        
        Output format: ["Topic 1", "Topic 2"]
        """)
        
        # Insight Prompt
        self.insight_prompt = ChatPromptTemplate.from_template("""
        You are a product analytics AI.
        
        Context:
        - Trend Data: {trend_str}
        - New Emerging Topics: {new_topics}
        - Spiking Topics (>2x growth): {spikes}
        
        Write 3–5 bullet-points summarizing trend changes, new/emerging topics, and spike events.
        Keep it concise and professional.
        """)
        
    def _get_chain(self, model_name: str, prompt, output_parser):
        """Creates a chain with the specified model."""
        llm = ChatGroq(
            temperature=0,
            model_name=model_name,
            groq_api_key=self.key
        )
        return prompt | llm | output_parser

    def _invoke_with_fallback(self, prompt, output_parser, input_data: Dict[str, Any]):
        """Tries to run the chain with fallback models if rate limit is hit."""
        errors = []
        
        for model in self.models:
            try:
                # print(f"[AGENT] Trying model: {model}")
                chain = self._get_chain(model, prompt, output_parser)
                return chain.invoke(input_data)
            except Exception as e:
                err_str = str(e).lower()
                # Check for rate limit (429) or overload errors
                if "429" in err_str or "rate limit" in err_str:
                    print(f"[WARN] Rate limit hit for {model}. Switching to backup...")
                    errors.append(f"{model}: Rate Limit")
                    continue
                else:
                    # If it's a different error (e.g. parsing), try next model just in case,
                    # but it might be prompt related.
                    print(f"[WARN] Error with {model}: {e}")
                    errors.append(f"{model}: {e}")
                    continue
                    
        raise Exception(f"All models failed: {errors}")

    def extract_topics(self, reviews_text: str) -> List[str]:
        try:
            return self._invoke_with_fallback(
                self.extract_prompt, 
                self.parser,  # Wait, parser wasn't re-initialized. It's stateless so it's fine.
                {"reviews_text": reviews_text}
            )
        except Exception as e:
            print(f"[ERROR] Extraction failed after retries: {e}")
            return []
            
    def generate_insights(self, trend_dict, new_topics, spikes) -> str:
        try:
            trend_view = ""
            for topic, counts in list(trend_dict.items())[:5]: 
                trend_view += f"{topic}: {counts}\n"
                
            return self._invoke_with_fallback(
                self.insight_prompt,
                self.str_parser,
                {
                    "trend_str": trend_view,
                    "new_topics": ", ".join(new_topics),
                    "spikes": ", ".join(spikes)
                }
            )
        except Exception as e:
            print(f"[ERROR] Insight generation failed: {e}")
            return "Could not generate insights (AI Busy)."

    @property
    def parser(self):
        return JsonOutputParser()
        
    @property
    def str_parser(self):
        return StrOutputParser()

# --- Singleton Instances ---
# These will be imported by main.py
taxonomy_mgr = TaxonomyManager()
agent = Agent()

# --- 3. PIPELINE ORCHESTRATOR ---
def process_daily_batch(date_str: str, reviews: List[Dict]) -> Dict[str, int]:
    """
    Processes a batch of reviews for a given date, extracts topics,
    maps them to the taxonomy, and returns daily topic counts.
    """
    print(f"[PROCESSING] {len(reviews)} reviews for {date_str}")
    
    daily_topics = {} # {topic: count}
    
    # Process in chunks of 20 to avoid context limits
    CHUNK_SIZE = 20
    for i in range(0, len(reviews), CHUNK_SIZE):
        batch = reviews[i:i+CHUNK_SIZE]
        
        # Format reviews for prompt
        reviews_text = ""
        for r in batch:
            # Filter extremely short reviews to save tokens and noise
            if len(r['content']) < 4: 
                continue
            reviews_text += f"ID: {r['reviewId']}\nText: {r['content']}\n---\n"
            
        if not reviews_text:
            continue

        # 1. Extract
        extracted_topics = agent.extract_topics(reviews_text)
        
        # 2. Map & Count
        for raw_topic in extracted_topics:
            if not raw_topic: continue
            
            # Map valid topics
            mapped_topic = taxonomy_mgr.map_extracted_topic(raw_topic)
            
            # Update taxonomy if new
            if mapped_topic not in taxonomy_mgr.topics:
                print(f"[NEW TOPIC] {mapped_topic}")
                taxonomy_mgr.add_new_topic(mapped_topic)
            
            # Count
            daily_topics[mapped_topic] = daily_topics.get(mapped_topic, 0) + 1
            
        print(f"   Processed batch {i//CHUNK_SIZE + 1}/{(len(reviews)//CHUNK_SIZE)+1}")

    # Persist taxonomy updates
    taxonomy_mgr.save_taxonomy()
    print(f"[DONE] Processed reviews for {date_str}")
    return daily_topics

def generate_insights_for_period(trend_data: Dict[str, Any], new_topics: List[str], spikes: List[str]) -> str:
    """
    Generates a summary of insights based on trend data, new topics, and spiking topics.
    """
    print("[INSIGHTS] Generating insights...")
    insights = agent.generate_insights(trend_data, new_topics, spikes)
    print("[INSIGHTS] Insights generated.")
    return insights
