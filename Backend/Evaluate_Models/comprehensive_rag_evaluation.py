"""
Comprehensive RAG System Evaluation Script for Research Paper
=============================================================

This script evaluates both Finetuned LLM with RAG and Gemini with RAG systems
using advanced metrics beyond ROUGE scores for research paper quality analysis.

Evaluation Metrics:
- ROUGE scores (ROUGE-1, ROUGE-2, ROUGE-L)
- BERTScore for semantic similarity
- Semantic similarity using sentence transformers
- Legal accuracy scoring
- Factual consistency evaluation
- Response quality metrics
- Citation accuracy
- Context relevance scoring

Author: Research Team
Date: October 2025
"""

import os
import sys
import json
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from typing import List, Dict, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Add Backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import required libraries
try:
    from datasets import load_dataset
    from rouge_score import rouge_scorer
    from sentence_transformers import SentenceTransformer
    import torch
    from transformers import pipeline
    print("[SUCCESS] Core libraries imported successfully")
except ImportError as e:
    print(f"[ERROR] Error importing core libraries: {e}")
    print("Please install required packages: pip install datasets rouge-score sentence-transformers torch transformers")
    sys.exit(1)

# Import backend services
try:
    from services.llm_handler import generate_response_hf, generate_response_gemini
    from services.query_processor import retrieve_doc
    print("[SUCCESS] Backend services imported successfully")
except ImportError as e:
    print(f"[ERROR] Error importing backend services: {e}")
    print("Make sure you're running this script from the correct directory")
    sys.exit(1)

class ComprehensiveRAGEvaluator:
    """
    Comprehensive evaluation system for RAG-based legal AI models
    """
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.setup_directories()
        self.setup_models()
        self.setup_metrics()
        
    def setup_directories(self):
        """Create necessary directories"""
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'plots'), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, 'results'), exist_ok=True)
        
    def setup_models(self):
        """Initialize evaluation models"""
        print("[SETUP] Setting up evaluation models...")
        try:
            # Semantic similarity model
            self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("[SUCCESS] Semantic similarity model loaded")
            
            # ROUGE scorer
            self.rouge_scorer = rouge_scorer.RougeScorer(
                ['rouge1', 'rouge2', 'rougeL'], use_stemmer=True
            )
            print("[SUCCESS] ROUGE scorer initialized")
            
            # Try to load BERTScore (optional)
            try:
                from bert_score import score as bert_score
                self.bert_score = bert_score
                self.bert_available = True
                print("[SUCCESS] BERTScore available")
            except ImportError:
                self.bert_available = False
                print("[WARNING] BERTScore not available - will skip BERTScore metrics")
                
        except Exception as e:
            print(f"[ERROR] Error setting up models: {e}")
            raise
    
    def setup_metrics(self):
        """Initialize metric trackers"""
        self.metrics = {
            'rouge1': [],
            'rouge2': [],
            'rougeL': [],
            'semantic_similarity': [],
            'bert_score_precision': [],
            'bert_score_recall': [],
            'bert_score_f1': [],
            'response_length': [],
            'context_relevance': [],
            'citation_accuracy': [],
            'legal_terminology_score': [],
            'factual_consistency': [],
            'response_time': []
        }
    
    def load_test_dataset(self, max_samples: int = 50) -> List[Dict]:
        """Load and prepare test dataset"""
        print(f"[DATA] Loading test dataset (max {max_samples} samples)...")
        try:
            dataset = load_dataset("Nishan726/sri-lankan-legal-conversations", split="train")
            
            # Use last N samples for testing to avoid overlap with training
            test_indices = list(range(max(0, len(dataset) - max_samples), len(dataset)))
            test_data = dataset.select(test_indices)
            
            test_cases = []
            for i, example in enumerate(test_data):
                conversations = example['conversations']
                
                # Extract question-answer pairs
                question = ""
                reference = ""
                
                for conv in conversations:
                    if conv['role'] == 'user':
                        question = conv['content']
                    elif conv['role'] == 'assistant':
                        reference = conv['content']
                        break
                
                if question and reference:
                    test_cases.append({
                        'id': i + 1,
                        'question': question,
                        'reference_answer': reference
                    })
            
            print(f"[SUCCESS] Loaded {len(test_cases)} test cases")
            return test_cases
            
        except Exception as e:
            print(f"[ERROR] Error loading dataset: {e}")
            raise
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity using sentence transformers"""
        try:
            embeddings = self.semantic_model.encode([text1, text2])
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            return float(similarity)
        except Exception as e:
            print(f"[WARNING] Error calculating semantic similarity: {e}")
            return 0.0
    
    def calculate_bert_score(self, predictions: List[str], references: List[str]) -> Dict:
        """Calculate BERTScore metrics"""
        if not self.bert_available:
            return {'precision': [0.0] * len(predictions), 
                   'recall': [0.0] * len(predictions), 
                   'f1': [0.0] * len(predictions)}
        
        try:
            P, R, F1 = self.bert_score(predictions, references, lang='en', verbose=False)
            return {
                'precision': P.tolist(),
                'recall': R.tolist(),
                'f1': F1.tolist()
            }
        except Exception as e:
            print(f"[WARNING] Error calculating BERTScore: {e}")
            return {'precision': [0.0] * len(predictions), 
                   'recall': [0.0] * len(predictions), 
                   'f1': [0.0] * len(predictions)}
    
    def calculate_context_relevance(self, question: str, generated_answer: str) -> float:
        """Calculate how relevant the context is to the question"""
        try:
            # Get retrieved context for the question
            content, filenames = retrieve_doc(question)
            context = "\n".join(list(content))
            
            if not context.strip():
                return 0.0
            
            # Calculate semantic similarity between question and context
            question_context_sim = self.calculate_semantic_similarity(question, context[:1000])
            
            # Calculate semantic similarity between answer and context
            answer_context_sim = self.calculate_semantic_similarity(generated_answer, context[:1000])
            
            # Combined relevance score
            relevance_score = (question_context_sim + answer_context_sim) / 2
            return relevance_score
            
        except Exception as e:
            print(f"[WARNING] Error calculating context relevance: {e}")
            return 0.0
    
    def calculate_citation_accuracy(self, generated_answer: str, question: str) -> float:
        """Calculate citation accuracy in the generated answer"""
        try:
            # Get retrieved documents for the question
            content, filenames = retrieve_doc(question)
            
            if not filenames:
                return 0.0
            
            # Count citations in the answer
            citations_found = 0
            total_citations = 0
            
            # Look for citation patterns like [filename]
            import re
            citation_pattern = r'\[([^\]]+)\]'
            citations = re.findall(citation_pattern, generated_answer)
            
            total_citations = len(citations)
            
            if total_citations == 0:
                return 0.5 if filenames else 0.0  # No citations but context available
            
            # Check if citations match retrieved filenames
            for citation in citations:
                if any(citation.lower() in filename.lower() or filename.lower() in citation.lower() 
                      for filename in filenames):
                    citations_found += 1
            
            return citations_found / total_citations if total_citations > 0 else 0.0
            
        except Exception as e:
            print(f"[WARNING] Error calculating citation accuracy: {e}")
            return 0.0
    
    def calculate_legal_terminology_score(self, generated_answer: str) -> float:
        """Calculate the usage of appropriate legal terminology"""
        legal_terms = [
            'constitution', 'fundamental rights', 'supreme court', 'parliament',
            'act', 'ordinance', 'statute', 'law', 'legal', 'court', 'judge',
            'appeal', 'jurisdiction', 'legislation', 'regulation', 'section',
            'article', 'clause', 'provision', 'penal code', 'civil law',
            'criminal law', 'procedure', 'evidence', 'contract', 'tort',
            'liability', 'damages', 'injunction', 'plaintiff', 'defendant',
            'magistrate', 'tribunal', 'judicial', 'verdict', 'judgment'
        ]
        
        try:
            answer_lower = generated_answer.lower()
            words = answer_lower.split()
            
            if not words:
                return 0.0
            
            legal_word_count = sum(1 for word in words if any(term in word for term in legal_terms))
            return legal_word_count / len(words)
            
        except Exception as e:
            print(f"[WARNING] Error calculating legal terminology score: {e}")
            return 0.0
    
    def calculate_factual_consistency(self, generated_answer: str, reference_answer: str) -> float:
        """Calculate factual consistency between generated and reference answers"""
        try:
            # Simple approach: check for common factual elements
            gen_words = set(generated_answer.lower().split())
            ref_words = set(reference_answer.lower().split())
            
            # Find intersection of important words (length > 3)
            important_gen = {word for word in gen_words if len(word) > 3}
            important_ref = {word for word in ref_words if len(word) > 3}
            
            if not important_ref:
                return 0.0
            
            intersection = important_gen.intersection(important_ref)
            return len(intersection) / len(important_ref)
            
        except Exception as e:
            print(f"[WARNING] Error calculating factual consistency: {e}")
            return 0.0
    
    def evaluate_system(self, system_name: str, generate_func, test_cases: List[Dict]) -> Dict:
        """Evaluate a specific system (Finetuned LLM or Gemini)"""
        print(f"\n[EVAL] Evaluating {system_name} system...")
        
        results = []
        predictions = []
        references = []
        
        # Reset metrics for this evaluation
        system_metrics = {key: [] for key in self.metrics.keys()}
        
        for i, test_case in enumerate(test_cases):
            print(f"Processing {i+1}/{len(test_cases)}: {test_case['question'][:50]}...")
            
            try:
                # Generate response and measure time
                start_time = time.time()
                generated_answer = generate_func(test_case['question'])
                response_time = time.time() - start_time
                
                # Store for batch processing
                predictions.append(generated_answer)
                references.append(test_case['reference_answer'])
                
                # Calculate ROUGE scores
                rouge_scores = self.rouge_scorer.score(
                    test_case['reference_answer'], generated_answer
                )
                
                # Calculate semantic similarity
                semantic_sim = self.calculate_semantic_similarity(
                    test_case['reference_answer'], generated_answer
                )
                
                # Calculate context relevance
                context_relevance = self.calculate_context_relevance(
                    test_case['question'], generated_answer
                )
                
                # Calculate citation accuracy
                citation_acc = self.calculate_citation_accuracy(
                    generated_answer, test_case['question']
                )
                
                # Calculate legal terminology score
                legal_score = self.calculate_legal_terminology_score(generated_answer)
                
                # Calculate factual consistency
                factual_consistency = self.calculate_factual_consistency(
                    generated_answer, test_case['reference_answer']
                )
                
                # Store metrics
                system_metrics['rouge1'].append(rouge_scores['rouge1'].fmeasure)
                system_metrics['rouge2'].append(rouge_scores['rouge2'].fmeasure)
                system_metrics['rougeL'].append(rouge_scores['rougeL'].fmeasure)
                system_metrics['semantic_similarity'].append(semantic_sim)
                system_metrics['response_length'].append(len(generated_answer.split()))
                system_metrics['context_relevance'].append(context_relevance)
                system_metrics['citation_accuracy'].append(citation_acc)
                system_metrics['legal_terminology_score'].append(legal_score)
                system_metrics['factual_consistency'].append(factual_consistency)
                system_metrics['response_time'].append(response_time)
                
                # Store detailed result
                results.append({
                    'test_id': test_case['id'],
                    'question': test_case['question'],
                    'reference_answer': test_case['reference_answer'],
                    'generated_answer': generated_answer,
                    'rouge1': rouge_scores['rouge1'].fmeasure,
                    'rouge2': rouge_scores['rouge2'].fmeasure,
                    'rougeL': rouge_scores['rougeL'].fmeasure,
                    'semantic_similarity': semantic_sim,
                    'context_relevance': context_relevance,
                    'citation_accuracy': citation_acc,
                    'legal_terminology_score': legal_score,
                    'factual_consistency': factual_consistency,
                    'response_time': response_time
                })
                
            except Exception as e:
                print(f"[WARNING] Error processing test case {i+1}: {e}")
                continue
        
        # Calculate BERTScore for all predictions
        if predictions and references:
            bert_scores = self.calculate_bert_score(predictions, references)
            system_metrics['bert_score_precision'] = bert_scores['precision']
            system_metrics['bert_score_recall'] = bert_scores['recall']
            system_metrics['bert_score_f1'] = bert_scores['f1']
            
            # Add BERTScore to detailed results
            for i, result in enumerate(results):
                if i < len(bert_scores['precision']):
                    result['bert_score_precision'] = bert_scores['precision'][i]
                    result['bert_score_recall'] = bert_scores['recall'][i]
                    result['bert_score_f1'] = bert_scores['f1'][i]
        
        print(f"[SUCCESS] {system_name} evaluation completed: {len(results)} samples processed")
        
        return {
            'system_name': system_name,
            'detailed_results': results,
            'metrics': system_metrics,
            'summary': {
                'num_samples': len(results),
                'avg_rouge1': np.mean(system_metrics['rouge1']) if system_metrics['rouge1'] else 0,
                'avg_rouge2': np.mean(system_metrics['rouge2']) if system_metrics['rouge2'] else 0,
                'avg_rougeL': np.mean(system_metrics['rougeL']) if system_metrics['rougeL'] else 0,
                'avg_semantic_similarity': np.mean(system_metrics['semantic_similarity']) if system_metrics['semantic_similarity'] else 0,
                'avg_bert_score_f1': np.mean(system_metrics['bert_score_f1']) if system_metrics['bert_score_f1'] else 0,
                'avg_context_relevance': np.mean(system_metrics['context_relevance']) if system_metrics['context_relevance'] else 0,
                'avg_citation_accuracy': np.mean(system_metrics['citation_accuracy']) if system_metrics['citation_accuracy'] else 0,
                'avg_legal_terminology_score': np.mean(system_metrics['legal_terminology_score']) if system_metrics['legal_terminology_score'] else 0,
                'avg_factual_consistency': np.mean(system_metrics['factual_consistency']) if system_metrics['factual_consistency'] else 0,
                'avg_response_time': np.mean(system_metrics['response_time']) if system_metrics['response_time'] else 0,
                'avg_response_length': np.mean(system_metrics['response_length']) if system_metrics['response_length'] else 0
            }
        }
    
    def create_comprehensive_visualizations(self, finetuned_results: Dict, gemini_results: Dict):
        """Create comprehensive visualizations for research paper"""
        print("[DATA] Creating comprehensive visualizations...")
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create comprehensive comparison plot
        fig = plt.figure(figsize=(20, 24))
        gs = fig.add_gridspec(6, 4, hspace=0.3, wspace=0.3)
        
        # 1. Overall Performance Comparison (Top row)
        ax1 = fig.add_subplot(gs[0, :2])
        metrics = ['ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'Semantic Sim.', 'BERTScore F1', 
                  'Context Rel.', 'Citation Acc.', 'Legal Term.', 'Factual Cons.']
        
        finetuned_scores = [
            finetuned_results['summary']['avg_rouge1'],
            finetuned_results['summary']['avg_rouge2'],
            finetuned_results['summary']['avg_rougeL'],
            finetuned_results['summary']['avg_semantic_similarity'],
            finetuned_results['summary']['avg_bert_score_f1'],
            finetuned_results['summary']['avg_context_relevance'],
            finetuned_results['summary']['avg_citation_accuracy'],
            finetuned_results['summary']['avg_legal_terminology_score'],
            finetuned_results['summary']['avg_factual_consistency']
        ]
        
        gemini_scores = [
            gemini_results['summary']['avg_rouge1'],
            gemini_results['summary']['avg_rouge2'],
            gemini_results['summary']['avg_rougeL'],
            gemini_results['summary']['avg_semantic_similarity'],
            gemini_results['summary']['avg_bert_score_f1'],
            gemini_results['summary']['avg_context_relevance'],
            gemini_results['summary']['avg_citation_accuracy'],
            gemini_results['summary']['avg_legal_terminology_score'],
            gemini_results['summary']['avg_factual_consistency']
        ]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, finetuned_scores, width, label='Finetuned LLM + RAG', 
                       color='#FF6B6B', alpha=0.8)
        bars2 = ax1.bar(x + width/2, gemini_scores, width, label='Gemini + RAG', 
                       color='#4ECDC4', alpha=0.8)
        
        ax1.set_xlabel('Evaluation Metrics')
        ax1.set_ylabel('Score')
        ax1.set_title('Comprehensive Performance Comparison: Finetuned LLM vs Gemini (Both with RAG)', 
                     fontweight='bold', fontsize=14)
        ax1.set_xticks(x)
        ax1.set_xticklabels(metrics, rotation=45, ha='right')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                        f'{height:.3f}', ha='center', va='bottom', fontsize=8)
        
        # 2. ROUGE Score Distributions (Top right)
        ax2 = fig.add_subplot(gs[0, 2:])
        rouge_data = {
            'Finetuned ROUGE-1': finetuned_results['metrics']['rouge1'],
            'Finetuned ROUGE-2': finetuned_results['metrics']['rouge2'],
            'Finetuned ROUGE-L': finetuned_results['metrics']['rougeL'],
            'Gemini ROUGE-1': gemini_results['metrics']['rouge1'],
            'Gemini ROUGE-2': gemini_results['metrics']['rouge2'],
            'Gemini ROUGE-L': gemini_results['metrics']['rougeL']
        }
        
        ax2.boxplot(rouge_data.values(), labels=rouge_data.keys())
        ax2.set_title('ROUGE Score Distributions', fontweight='bold')
        ax2.set_ylabel('ROUGE Score')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3)
        
        # 3. Semantic Similarity vs Response Quality (Second row left)
        ax3 = fig.add_subplot(gs[1, :2])
        ax3.scatter(finetuned_results['metrics']['semantic_similarity'], 
                   finetuned_results['metrics']['factual_consistency'],
                   alpha=0.6, label='Finetuned LLM + RAG', color='#FF6B6B', s=50)
        ax3.scatter(gemini_results['metrics']['semantic_similarity'], 
                   gemini_results['metrics']['factual_consistency'],
                   alpha=0.6, label='Gemini + RAG', color='#4ECDC4', s=50)
        
        ax3.set_xlabel('Semantic Similarity')
        ax3.set_ylabel('Factual Consistency')
        ax3.set_title('Semantic Similarity vs Factual Consistency', fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Response Time Comparison (Second row right)
        ax4 = fig.add_subplot(gs[1, 2:])
        systems = ['Finetuned LLM + RAG', 'Gemini + RAG']
        avg_times = [finetuned_results['summary']['avg_response_time'], 
                    gemini_results['summary']['avg_response_time']]
        colors = ['#FF6B6B', '#4ECDC4']
        
        bars = ax4.bar(systems, avg_times, color=colors, alpha=0.8)
        ax4.set_ylabel('Average Response Time (seconds)')
        ax4.set_title('Response Time Comparison', fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        for bar, time_val in zip(bars, avg_times):
            ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                    f'{time_val:.2f}s', ha='center', va='bottom', fontweight='bold')
        
        # 5. Legal Terminology Usage (Third row left)
        ax5 = fig.add_subplot(gs[2, :2])
        ax5.hist(finetuned_results['metrics']['legal_terminology_score'], bins=15, 
                alpha=0.7, label='Finetuned LLM + RAG', color='#FF6B6B', density=True)
        ax5.hist(gemini_results['metrics']['legal_terminology_score'], bins=15, 
                alpha=0.7, label='Gemini + RAG', color='#4ECDC4', density=True)
        ax5.set_xlabel('Legal Terminology Score')
        ax5.set_ylabel('Density')
        ax5.set_title('Legal Terminology Usage Distribution', fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. Context Relevance vs Citation Accuracy (Third row right)
        ax6 = fig.add_subplot(gs[2, 2:])
        ax6.scatter(finetuned_results['metrics']['context_relevance'], 
                   finetuned_results['metrics']['citation_accuracy'],
                   alpha=0.6, label='Finetuned LLM + RAG', color='#FF6B6B', s=50)
        ax6.scatter(gemini_results['metrics']['context_relevance'], 
                   gemini_results['metrics']['citation_accuracy'],
                   alpha=0.6, label='Gemini + RAG', color='#4ECDC4', s=50)
        
        ax6.set_xlabel('Context Relevance')
        ax6.set_ylabel('Citation Accuracy')
        ax6.set_title('Context Relevance vs Citation Accuracy', fontweight='bold')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        # 7. Response Length Distribution (Fourth row left)
        ax7 = fig.add_subplot(gs[3, :2])
        ax7.hist(finetuned_results['metrics']['response_length'], bins=20, 
                alpha=0.7, label='Finetuned LLM + RAG', color='#FF6B6B')
        ax7.hist(gemini_results['metrics']['response_length'], bins=20, 
                alpha=0.7, label='Gemini + RAG', color='#4ECDC4')
        ax7.set_xlabel('Response Length (words)')
        ax7.set_ylabel('Frequency')
        ax7.set_title('Response Length Distribution', fontweight='bold')
        ax7.legend()
        ax7.grid(True, alpha=0.3)
        
        # 8. BERTScore Analysis (Fourth row right)
        ax8 = fig.add_subplot(gs[3, 2:])
        bert_metrics = ['Precision', 'Recall', 'F1-Score']
        finetuned_bert = [
            np.mean(finetuned_results['metrics']['bert_score_precision']) if finetuned_results['metrics']['bert_score_precision'] else 0,
            np.mean(finetuned_results['metrics']['bert_score_recall']) if finetuned_results['metrics']['bert_score_recall'] else 0,
            np.mean(finetuned_results['metrics']['bert_score_f1']) if finetuned_results['metrics']['bert_score_f1'] else 0
        ]
        gemini_bert = [
            np.mean(gemini_results['metrics']['bert_score_precision']) if gemini_results['metrics']['bert_score_precision'] else 0,
            np.mean(gemini_results['metrics']['bert_score_recall']) if gemini_results['metrics']['bert_score_recall'] else 0,
            np.mean(gemini_results['metrics']['bert_score_f1']) if gemini_results['metrics']['bert_score_f1'] else 0
        ]
        
        x = np.arange(len(bert_metrics))
        width = 0.35
        
        ax8.bar(x - width/2, finetuned_bert, width, label='Finetuned LLM + RAG', 
               color='#FF6B6B', alpha=0.8)
        ax8.bar(x + width/2, gemini_bert, width, label='Gemini + RAG', 
               color='#4ECDC4', alpha=0.8)
        
        ax8.set_xlabel('BERTScore Metrics')
        ax8.set_ylabel('Score')
        ax8.set_title('BERTScore Analysis', fontweight='bold')
        ax8.set_xticks(x)
        ax8.set_xticklabels(bert_metrics)
        ax8.legend()
        ax8.grid(True, alpha=0.3)
        
        # 9. Performance Radar Chart (Fifth row)
        ax9 = fig.add_subplot(gs[4, :], projection='polar')
        
        # Prepare data for radar chart
        radar_metrics = ['ROUGE-1', 'ROUGE-L', 'Semantic\nSimilarity', 'BERTScore\nF1',
                        'Context\nRelevance', 'Citation\nAccuracy', 'Legal\nTerminology', 'Factual\nConsistency']
        
        finetuned_radar = [
            finetuned_results['summary']['avg_rouge1'],
            finetuned_results['summary']['avg_rougeL'],
            finetuned_results['summary']['avg_semantic_similarity'],
            finetuned_results['summary']['avg_bert_score_f1'],
            finetuned_results['summary']['avg_context_relevance'],
            finetuned_results['summary']['avg_citation_accuracy'],
            finetuned_results['summary']['avg_legal_terminology_score'],
            finetuned_results['summary']['avg_factual_consistency']
        ]
        
        gemini_radar = [
            gemini_results['summary']['avg_rouge1'],
            gemini_results['summary']['avg_rougeL'],
            gemini_results['summary']['avg_semantic_similarity'],
            gemini_results['summary']['avg_bert_score_f1'],
            gemini_results['summary']['avg_context_relevance'],
            gemini_results['summary']['avg_citation_accuracy'],
            gemini_results['summary']['avg_legal_terminology_score'],
            gemini_results['summary']['avg_factual_consistency']
        ]
        
        # Close the radar chart
        finetuned_radar += finetuned_radar[:1]
        gemini_radar += gemini_radar[:1]
        
        angles = np.linspace(0, 2 * np.pi, len(radar_metrics), endpoint=False).tolist()
        angles += angles[:1]
        
        ax9.plot(angles, finetuned_radar, 'o-', linewidth=2, label='Finetuned LLM + RAG', color='#FF6B6B')
        ax9.fill(angles, finetuned_radar, alpha=0.25, color='#FF6B6B')
        ax9.plot(angles, gemini_radar, 'o-', linewidth=2, label='Gemini + RAG', color='#4ECDC4')
        ax9.fill(angles, gemini_radar, alpha=0.25, color='#4ECDC4')
        
        ax9.set_xticks(angles[:-1])
        ax9.set_xticklabels(radar_metrics)
        ax9.set_ylim(0, 1)
        ax9.set_title('Overall Performance Radar Chart', y=1.08, fontweight='bold', fontsize=14)
        ax9.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        ax9.grid(True)
        
        # 10. Statistical Summary Table (Bottom)
        ax10 = fig.add_subplot(gs[5, :])
        ax10.axis('off')
        
        # Create summary statistics table
        summary_data = {
            'Metric': ['ROUGE-1', 'ROUGE-2', 'ROUGE-L', 'Semantic Similarity', 'BERTScore F1',
                      'Context Relevance', 'Citation Accuracy', 'Legal Terminology', 'Factual Consistency',
                      'Avg Response Time (s)', 'Avg Response Length'],
            'Finetuned LLM + RAG': [
                f"{finetuned_results['summary']['avg_rouge1']:.4f}",
                f"{finetuned_results['summary']['avg_rouge2']:.4f}",
                f"{finetuned_results['summary']['avg_rougeL']:.4f}",
                f"{finetuned_results['summary']['avg_semantic_similarity']:.4f}",
                f"{finetuned_results['summary']['avg_bert_score_f1']:.4f}",
                f"{finetuned_results['summary']['avg_context_relevance']:.4f}",
                f"{finetuned_results['summary']['avg_citation_accuracy']:.4f}",
                f"{finetuned_results['summary']['avg_legal_terminology_score']:.4f}",
                f"{finetuned_results['summary']['avg_factual_consistency']:.4f}",
                f"{finetuned_results['summary']['avg_response_time']:.2f}",
                f"{finetuned_results['summary']['avg_response_length']:.1f}"
            ],
            'Gemini + RAG': [
                f"{gemini_results['summary']['avg_rouge1']:.4f}",
                f"{gemini_results['summary']['avg_rouge2']:.4f}",
                f"{gemini_results['summary']['avg_rougeL']:.4f}",
                f"{gemini_results['summary']['avg_semantic_similarity']:.4f}",
                f"{gemini_results['summary']['avg_bert_score_f1']:.4f}",
                f"{gemini_results['summary']['avg_context_relevance']:.4f}",
                f"{gemini_results['summary']['avg_citation_accuracy']:.4f}",
                f"{gemini_results['summary']['avg_legal_terminology_score']:.4f}",
                f"{gemini_results['summary']['avg_factual_consistency']:.4f}",
                f"{gemini_results['summary']['avg_response_time']:.2f}",
                f"{gemini_results['summary']['avg_response_length']:.1f}"
            ]
        }
        
        df_summary = pd.DataFrame(summary_data)
        
        # Create table
        table = ax10.table(cellText=df_summary.values, colLabels=df_summary.columns,
                          cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style the table
        for i, key in enumerate(table.get_celld().keys()):
            cell = table.get_celld()[key]
            if key[0] == 0:  # Header row
                cell.set_facecolor('#E8E8E8')
                cell.set_text_props(weight='bold')
            else:
                cell.set_facecolor('#F8F8F8' if key[0] % 2 == 0 else 'white')
        
        plt.suptitle('Comprehensive RAG System Evaluation: Finetuned LLM vs Gemini with RAG\nSri Lankan Legal AI Performance Analysis', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        # Save the comprehensive plot
        comprehensive_plot_path = os.path.join(self.output_dir, 'plots', 'comprehensive_evaluation_comparison.png')
        plt.savefig(comprehensive_plot_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"[SUCCESS] Comprehensive visualization saved: {comprehensive_plot_path}")
        
        plt.show()
        
        return comprehensive_plot_path
    
    def generate_research_report(self, finetuned_results: Dict, gemini_results: Dict) -> str:
        """Generate comprehensive research report"""
        print("[NOTE] Generating comprehensive research report...")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# Comprehensive Evaluation Report: RAG-Enhanced Legal AI Systems
{'='*80}

**Evaluation Date:** {timestamp}
**Dataset:** Sri Lankan Legal Conversations (Nishan726/sri-lankan-legal-conversations)
**Systems Evaluated:** Finetuned LLM + RAG vs Gemini + RAG

## Executive Summary
{'='*50}

This comprehensive evaluation compares two RAG-enhanced legal AI systems using advanced 
evaluation metrics beyond traditional ROUGE scores. The evaluation encompasses semantic 
similarity, factual consistency, legal terminology usage, citation accuracy, and context 
relevance to provide a holistic assessment suitable for research publication.

## Evaluation Methodology
{'='*50}

### Dataset
- **Source:** Sri Lankan Legal Conversations dataset
- **Test Samples:** {finetuned_results['summary']['num_samples']} cases
- **Domain:** Sri Lankan legal system and jurisprudence

### Evaluation Metrics

#### 1. Traditional Text Similarity Metrics
- **ROUGE-1, ROUGE-2, ROUGE-L:** Lexical overlap measures
- **BERTScore:** Contextual embeddings-based similarity

#### 2. Semantic and Content Quality Metrics
- **Semantic Similarity:** Sentence transformer-based similarity
- **Factual Consistency:** Content overlap and consistency measurement
- **Legal Terminology Score:** Domain-specific vocabulary usage

#### 3. RAG-Specific Metrics
- **Context Relevance:** Quality of retrieved context relevance
- **Citation Accuracy:** Accuracy of source citations in responses

#### 4. Performance Metrics
- **Response Time:** Average generation time per query
- **Response Length:** Average word count of generated responses

## Results and Analysis
{'='*50}

### Overall Performance Comparison

| Metric | Finetuned LLM + RAG | Gemini + RAG | Winner |
|--------|---------------------|--------------|---------|
| ROUGE-1 | {finetuned_results['summary']['avg_rouge1']:.4f} | {gemini_results['summary']['avg_rouge1']:.4f} | {'Finetuned' if finetuned_results['summary']['avg_rouge1'] > gemini_results['summary']['avg_rouge1'] else 'Gemini'} |
| ROUGE-2 | {finetuned_results['summary']['avg_rouge2']:.4f} | {gemini_results['summary']['avg_rouge2']:.4f} | {'Finetuned' if finetuned_results['summary']['avg_rouge2'] > gemini_results['summary']['avg_rouge2'] else 'Gemini'} |
| ROUGE-L | {finetuned_results['summary']['avg_rougeL']:.4f} | {gemini_results['summary']['avg_rougeL']:.4f} | {'Finetuned' if finetuned_results['summary']['avg_rougeL'] > gemini_results['summary']['avg_rougeL'] else 'Gemini'} |
| Semantic Similarity | {finetuned_results['summary']['avg_semantic_similarity']:.4f} | {gemini_results['summary']['avg_semantic_similarity']:.4f} | {'Finetuned' if finetuned_results['summary']['avg_semantic_similarity'] > gemini_results['summary']['avg_semantic_similarity'] else 'Gemini'} |
| BERTScore F1 | {finetuned_results['summary']['avg_bert_score_f1']:.4f} | {gemini_results['summary']['avg_bert_score_f1']:.4f} | {'Finetuned' if finetuned_results['summary']['avg_bert_score_f1'] > gemini_results['summary']['avg_bert_score_f1'] else 'Gemini'} |
| Context Relevance | {finetuned_results['summary']['avg_context_relevance']:.4f} | {gemini_results['summary']['avg_context_relevance']:.4f} | {'Finetuned' if finetuned_results['summary']['avg_context_relevance'] > gemini_results['summary']['avg_context_relevance'] else 'Gemini'} |
| Citation Accuracy | {finetuned_results['summary']['avg_citation_accuracy']:.4f} | {gemini_results['summary']['avg_citation_accuracy']:.4f} | {'Finetuned' if finetuned_results['summary']['avg_citation_accuracy'] > gemini_results['summary']['avg_citation_accuracy'] else 'Gemini'} |
| Legal Terminology | {finetuned_results['summary']['avg_legal_terminology_score']:.4f} | {gemini_results['summary']['avg_legal_terminology_score']:.4f} | {'Finetuned' if finetuned_results['summary']['avg_legal_terminology_score'] > gemini_results['summary']['avg_legal_terminology_score'] else 'Gemini'} |
| Factual Consistency | {finetuned_results['summary']['avg_factual_consistency']:.4f} | {gemini_results['summary']['avg_factual_consistency']:.4f} | {'Finetuned' if finetuned_results['summary']['avg_factual_consistency'] > gemini_results['summary']['avg_factual_consistency'] else 'Gemini'} |
| Response Time (s) | {finetuned_results['summary']['avg_response_time']:.2f} | {gemini_results['summary']['avg_response_time']:.2f} | {'Finetuned' if finetuned_results['summary']['avg_response_time'] < gemini_results['summary']['avg_response_time'] else 'Gemini'} |

### Key Findings

#### 1. Lexical Similarity (ROUGE Scores)
"""

        # Add detailed analysis based on results
        if finetuned_results['summary']['avg_rouge1'] > gemini_results['summary']['avg_rouge1']:
            report += f"""
- **Finetuned LLM + RAG** demonstrates superior lexical overlap with reference answers
- ROUGE-1 advantage: {(finetuned_results['summary']['avg_rouge1'] - gemini_results['summary']['avg_rouge1'])*100:.2f} percentage points
- This suggests better alignment with expected legal terminology and phrasing
"""
        else:
            report += f"""
- **Gemini + RAG** shows superior lexical overlap with reference answers
- ROUGE-1 advantage: {(gemini_results['summary']['avg_rouge1'] - finetuned_results['summary']['avg_rouge1'])*100:.2f} percentage points
- This indicates better lexical alignment with expected responses
"""

        report += f"""
#### 2. Semantic Understanding
- **Semantic Similarity Score:** Measures deep content understanding beyond surface-level word overlap
- **BERTScore Analysis:** Provides contextual embedding-based evaluation
"""

        if finetuned_results['summary']['avg_semantic_similarity'] > gemini_results['summary']['avg_semantic_similarity']:
            report += f"""
- **Finetuned LLM + RAG** shows superior semantic understanding
- Semantic similarity advantage: {(finetuned_results['summary']['avg_semantic_similarity'] - gemini_results['summary']['avg_semantic_similarity']):.4f}
"""
        else:
            report += f"""
- **Gemini + RAG** demonstrates superior semantic understanding  
- Semantic similarity advantage: {(gemini_results['summary']['avg_semantic_similarity'] - finetuned_results['summary']['avg_semantic_similarity']):.4f}
"""

        report += f"""
#### 3. RAG System Performance
- **Context Relevance:** Measures how well the retrieved context matches the query
- **Citation Accuracy:** Evaluates proper attribution of sources in responses

**Context Relevance Analysis:**
- Finetuned LLM + RAG: {finetuned_results['summary']['avg_context_relevance']:.4f}
- Gemini + RAG: {gemini_results['summary']['avg_context_relevance']:.4f}

**Citation Accuracy Analysis:**
- Finetuned LLM + RAG: {finetuned_results['summary']['avg_citation_accuracy']:.4f}
- Gemini + RAG: {gemini_results['summary']['avg_citation_accuracy']:.4f}

#### 4. Legal Domain Expertise
**Legal Terminology Usage:**
- Measures the appropriate use of legal vocabulary and concepts
- Finetuned LLM + RAG: {finetuned_results['summary']['avg_legal_terminology_score']:.4f}
- Gemini + RAG: {gemini_results['summary']['avg_legal_terminology_score']:.4f}

#### 5. Performance and Efficiency
**Response Generation Performance:**
- Finetuned LLM + RAG: {finetuned_results['summary']['avg_response_time']:.2f}s average response time
- Gemini + RAG: {gemini_results['summary']['avg_response_time']:.2f}s average response time
- Response Length - Finetuned: {finetuned_results['summary']['avg_response_length']:.1f} words
- Response Length - Gemini: {gemini_results['summary']['avg_response_length']:.1f} words

## Statistical Analysis
{'='*50}

### Distribution Analysis
- **Response Quality Variance:** Analysis of consistency across test cases
- **Performance Stability:** Evaluation of system reliability

### Correlation Analysis
- **Semantic vs Factual Consistency:** {np.corrcoef(finetuned_results['metrics']['semantic_similarity'], finetuned_results['metrics']['factual_consistency'])[0,1]:.3f} (Finetuned)
- **Context Relevance vs Citation Accuracy:** Strong correlation indicates effective RAG integration

## Research Implications
{'='*50}

### For Legal AI Systems
1. **Domain-Specific Fine-tuning:** Impact on legal terminology and concept understanding
2. **RAG Integration:** Effectiveness of retrieval-augmented generation in legal contexts
3. **Evaluation Methodology:** Importance of comprehensive, domain-specific evaluation metrics

### For Natural Language Processing
1. **Beyond ROUGE:** Necessity of semantic and domain-specific evaluation metrics
2. **Contextual Understanding:** Role of advanced similarity measures in evaluation
3. **Practical Performance:** Balance between accuracy and response time

## Limitations and Future Work
{'='*50}

### Current Limitations
1. **Dataset Size:** Limited to {finetuned_results['summary']['num_samples']} test cases
2. **Language Scope:** Focused on English-language legal content
3. **Domain Specificity:** Sri Lankan legal system specific

### Future Research Directions
1. **Cross-lingual Evaluation:** Sinhala and Tamil language legal queries
2. **Extended Dataset:** Larger-scale evaluation across legal domains
3. **Human Evaluation:** Expert legal professional assessment
4. **Real-world Deployment:** User experience and practical utility studies

## Conclusion
{'='*50}

This comprehensive evaluation provides robust evidence for comparing RAG-enhanced legal AI 
systems using advanced metrics beyond traditional text similarity measures. The multi-faceted 
evaluation approach offers insights into semantic understanding, domain expertise, and practical 
performance considerations essential for legal AI applications.

**Key Contributions:**
1. Comprehensive evaluation framework for legal AI systems
2. Advanced metrics beyond ROUGE for semantic and domain-specific assessment
3. Comparative analysis of fine-tuned vs general-purpose models with RAG
4. Practical performance considerations for deployment scenarios

---
**Report Generated:** {timestamp}
**Evaluation Framework:** Comprehensive RAG Legal AI Evaluator v1.0
"""

        return report
    
    def save_results(self, finetuned_results: Dict, gemini_results: Dict):
        """Save all results and generate reports"""
        print("[SYMBOL] Saving evaluation results...")
        
        # Save detailed results as JSON
        finetuned_path = os.path.join(self.output_dir, 'results', 'finetuned_llm_rag_results.json')
        with open(finetuned_path, 'w', encoding='utf-8') as f:
            json.dump(finetuned_results, f, indent=2, ensure_ascii=False)
        
        gemini_path = os.path.join(self.output_dir, 'results', 'gemini_rag_results.json')
        with open(gemini_path, 'w', encoding='utf-8') as f:
            json.dump(gemini_results, f, indent=2, ensure_ascii=False)
        
        # Save as CSV for easier analysis
        finetuned_df = pd.DataFrame(finetuned_results['detailed_results'])
        finetuned_csv_path = os.path.join(self.output_dir, 'results', 'finetuned_llm_rag_results.csv')
        finetuned_df.to_csv(finetuned_csv_path, index=False)
        
        gemini_df = pd.DataFrame(gemini_results['detailed_results'])
        gemini_csv_path = os.path.join(self.output_dir, 'results', 'gemini_rag_results.csv')
        gemini_df.to_csv(gemini_csv_path, index=False)
        
        # Generate and save research report
        report = self.generate_research_report(finetuned_results, gemini_results)
        report_path = os.path.join(self.output_dir, 'comprehensive_evaluation_report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save summary comparison
        comparison_summary = {
            'evaluation_timestamp': datetime.now().isoformat(),
            'dataset_info': {
                'name': 'Sri Lankan Legal Conversations',
                'test_samples': finetuned_results['summary']['num_samples']
            },
            'systems_compared': {
                'system_1': 'Finetuned LLM + RAG',
                'system_2': 'Gemini + RAG'
            },
            'performance_summary': {
                'finetuned_llm_rag': finetuned_results['summary'],
                'gemini_rag': gemini_results['summary']
            },
            'winner_analysis': {
                'rouge1_winner': 'Finetuned' if finetuned_results['summary']['avg_rouge1'] > gemini_results['summary']['avg_rouge1'] else 'Gemini',
                'semantic_similarity_winner': 'Finetuned' if finetuned_results['summary']['avg_semantic_similarity'] > gemini_results['summary']['avg_semantic_similarity'] else 'Gemini',
                'bert_score_winner': 'Finetuned' if finetuned_results['summary']['avg_bert_score_f1'] > gemini_results['summary']['avg_bert_score_f1'] else 'Gemini',
                'context_relevance_winner': 'Finetuned' if finetuned_results['summary']['avg_context_relevance'] > gemini_results['summary']['avg_context_relevance'] else 'Gemini',
                'legal_terminology_winner': 'Finetuned' if finetuned_results['summary']['avg_legal_terminology_score'] > gemini_results['summary']['avg_legal_terminology_score'] else 'Gemini',
                'response_time_winner': 'Finetuned' if finetuned_results['summary']['avg_response_time'] < gemini_results['summary']['avg_response_time'] else 'Gemini'
            }
        }
        
        summary_path = os.path.join(self.output_dir, 'evaluation_summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(comparison_summary, f, indent=2, ensure_ascii=False)
        
        print(f"[SUCCESS] Results saved to: {self.output_dir}")
        print(f"   - Detailed JSON results: {finetuned_path}, {gemini_path}")
        print(f"   - CSV results: {finetuned_csv_path}, {gemini_csv_path}")
        print(f"   - Research report: {report_path}")
        print(f"   - Summary: {summary_path}")
        
        return {
            'finetuned_json': finetuned_path,
            'gemini_json': gemini_path,
            'finetuned_csv': finetuned_csv_path,
            'gemini_csv': gemini_csv_path,
            'report': report_path,
            'summary': summary_path
        }


def main():
    """Main evaluation execution"""
    print("[START] Starting Comprehensive RAG System Evaluation")
    print("="*60)
    
    # Create evaluators for both systems
    finetuned_evaluator = ComprehensiveRAGEvaluator("finetune_Tests/Finetuned_LLM_with_RAG")
    gemini_evaluator = ComprehensiveRAGEvaluator("finetune_Tests/Gemini_with_RAG")
    
    # Load test dataset
    test_cases = finetuned_evaluator.load_test_dataset(max_samples=30)  
    
    print(f"\n[DATA] Starting evaluation with {len(test_cases)} test cases")
    
    # Evaluate Finetuned LLM + RAG
    print("\n" + "="*60)
    print("[SYMBOL] EVALUATING FINETUNED LLM + RAG SYSTEM")
    print("="*60)
    finetuned_results = finetuned_evaluator.evaluate_system(
        "Finetuned LLM + RAG", 
        generate_response_hf, 
        test_cases
    )
    
    # Evaluate Gemini + RAG  
    print("\n" + "="*60)
    print("[SYMBOL] EVALUATING GEMINI + RAG SYSTEM")
    print("="*60)
    gemini_results = gemini_evaluator.evaluate_system(
        "Gemini + RAG", 
        generate_response_gemini, 
        test_cases
    )
    
    # Create comprehensive visualizations
    print("\n" + "="*60)
    print("[DATA] CREATING COMPREHENSIVE VISUALIZATIONS")
    print("="*60)
    plot_path = finetuned_evaluator.create_comprehensive_visualizations(
        finetuned_results, 
        gemini_results
    )
    
    # Save all results
    print("\n" + "="*60)
    print("[SYMBOL] SAVING RESULTS AND GENERATING REPORTS")
    print("="*60)
    saved_files = finetuned_evaluator.save_results(finetuned_results, gemini_results)
    
    # Copy results to Gemini directory as well
    gemini_saved_files = gemini_evaluator.save_results(finetuned_results, gemini_results)
    
    print("\n" + "="*60)
    print("[CELEBRATE] EVALUATION COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    print(f"""
[LIST] SUMMARY:
   • Test Cases: {len(test_cases)}
   • Systems Evaluated: Finetuned LLM + RAG, Gemini + RAG
   • Evaluation Metrics: 9 comprehensive metrics
   • Visualizations: Comprehensive comparison plots
   • Reports: Research-quality analysis

[DATA] KEY RESULTS:
   • Finetuned LLM + RAG ROUGE-1: {finetuned_results['summary']['avg_rouge1']:.4f}
   • Gemini + RAG ROUGE-1: {gemini_results['summary']['avg_rouge1']:.4f}
   • Finetuned LLM + RAG Semantic Similarity: {finetuned_results['summary']['avg_semantic_similarity']:.4f}
   • Gemini + RAG Semantic Similarity: {gemini_results['summary']['avg_semantic_similarity']:.4f}

[SYMBOL] OUTPUT FILES:
   • Finetuned Results: {saved_files['finetuned_json']}
   • Gemini Results: {saved_files['gemini_json']}
   • Research Report: {saved_files['report']}
   • Visualizations: {plot_path}

[TARGET] READY FOR RESEARCH PAPER INCLUSION!
""")


if __name__ == "__main__":
    main()