#!/usr/bin/env python3
"""
Agent4All Research Validator
Enhanced validator for research tasks with comprehensive evaluation
"""

import os
import sys
import time
import logging
import numpy as np
import asyncio
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import aiohttp
import requests
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import bittensor as bt
from neurons.validator import Validator
from category_registry import get_category_info

class ResearchValidator(Validator):
    """Enhanced research validator with comprehensive evaluation capabilities"""
    
    def __init__(self, config=None):
        super().__init__(config=config)
        self.category = "research"
        self.category_info = get_category_info(self.category)
        
        # Research-specific evaluation configuration
        self.evaluation_config = {
            'content_quality_weight': 0.3,
            'fact_accuracy_weight': 0.25,
            'citation_quality_weight': 0.2,
            'synthesis_quality_weight': 0.15,
            'response_time_weight': 0.1,
            'min_content_length': 100,
            'max_content_length': 5000,
            'min_fact_check_score': 0.7,
            'min_citation_count': 2,
            'plagiarism_threshold': 0.3
        }
        
        # Initialize evaluation tools
        self.evaluation_tools = {
            'content_analyzer': self.analyze_content_quality,
            'fact_checker': self.evaluate_fact_accuracy,
            'citation_validator': self.validate_citations,
            'synthesis_evaluator': self.evaluate_synthesis,
            'plagiarism_detector': self.detect_plagiarism,
            'source_verifier': self.verify_sources
        }
        
        # Enhanced performance tracking
        self.research_performance_metrics = {
            'evaluation_times': defaultdict(list),
            'score_distributions': defaultdict(list),
            'category_scores': defaultdict(lambda: {
                'content_quality': [],
                'fact_accuracy': [],
                'citation_quality': [],
                'synthesis_quality': [],
                'overall_score': []
            }),
            'error_analysis': defaultdict(int),
            'quality_trends': defaultdict(list)
        }
        
        # Initialize Prometheus metrics for research validation
        self.research_metrics = {
            'research_evaluations': Counter('research_evaluations_total', 'Total research evaluations'),
            'content_quality_scores': Histogram('content_quality_scores', 'Content quality scores'),
            'fact_accuracy_scores': Histogram('fact_accuracy_scores', 'Fact accuracy scores'),
            'citation_quality_scores': Histogram('citation_quality_scores', 'Citation quality scores'),
            'synthesis_quality_scores': Histogram('synthesis_quality_scores', 'Synthesis quality scores'),
            'overall_research_scores': Histogram('overall_research_scores', 'Overall research scores'),
            'evaluation_time': Histogram('research_evaluation_time_seconds', 'Research evaluation time'),
            'active_evaluations': Gauge('active_research_evaluations', 'Number of active research evaluations')
        }
        
        # Start Prometheus metrics server
        start_http_server(8002)
        
        # Research evaluation cache
        self.evaluation_cache = {}
        self.cache_ttl = 1800  # 30 minutes
        
        logging.info(f"Initialized enhanced research validator with comprehensive evaluation capabilities")

    async def evaluate_research_response(self, response, expected_output=None):
        """Comprehensive evaluation of research responses"""
        start_time = time.time()
        self.research_metrics['research_evaluations'].inc()
        self.research_metrics['active_evaluations'].inc()
        
        try:
            # Parse response data
            response_data = self.parse_research_response(response)
            
            # Validate response structure
            if not self.validate_research_response(response_data):
                return 0.0
            
            # Perform comprehensive evaluation
            evaluation_results = await self.comprehensive_evaluation(response_data)
            
            # Calculate weighted score
            overall_score = self.calculate_weighted_score(evaluation_results)
            
            # Update metrics
            evaluation_time = time.time() - start_time
            self.research_metrics['evaluation_time'].observe(evaluation_time)
            self.research_metrics['overall_research_scores'].observe(overall_score)
            
            # Update performance tracking
            self.update_research_performance_metrics(evaluation_results, evaluation_time)
            
            return overall_score
            
        except Exception as e:
            evaluation_time = time.time() - start_time
            self.research_metrics['evaluation_time'].observe(evaluation_time)
            logging.error(f"Research evaluation failed: {str(e)}")
            return 0.0
            
        finally:
            self.research_metrics['active_evaluations'].dec()

    def parse_research_response(self, response) -> Dict:
        """Parse research response data"""
        try:
            # Extract main content
            content = response.dummy_output
            
            # Parse metadata if available
            metadata = getattr(response, 'metadata', {})
            
            # Parse JSON if content is JSON string
            if isinstance(content, str) and content.strip().startswith('{'):
                try:
                    parsed_content = json.loads(content)
                    return {
                        'content': parsed_content.get('content', content),
                        'summary': parsed_content.get('summary', ''),
                        'sources': parsed_content.get('sources', []),
                        'citations': parsed_content.get('citations', []),
                        'fact_check_score': parsed_content.get('fact_check_score', 0.0),
                        'synthesis_quality': parsed_content.get('synthesis_quality', 0.0),
                        'metadata': parsed_content.get('metadata', metadata)
                    }
                except json.JSONDecodeError:
                    pass
            
            # Fallback to simple content parsing
            return {
                'content': content,
                'summary': '',
                'sources': [],
                'citations': [],
                'fact_check_score': 0.0,
                'synthesis_quality': 0.0,
                'metadata': metadata
            }
            
        except Exception as e:
            logging.error(f"Failed to parse research response: {str(e)}")
            return {
                'content': str(response.dummy_output),
                'summary': '',
                'sources': [],
                'citations': [],
                'fact_check_score': 0.0,
                'synthesis_quality': 0.0,
                'metadata': {}
            }

    def validate_research_response(self, response_data: Dict) -> bool:
        """Validate research response structure and content"""
        # Check required fields
        if 'content' not in response_data or not response_data['content']:
            return False
        
        content = response_data['content']
        
        # Check content length
        if len(content) < self.evaluation_config['min_content_length']:
            return False
        
        if len(content) > self.evaluation_config['max_content_length']:
            return False
        
        # Check for error indicators
        error_indicators = ['error:', 'failed:', 'exception:', 'traceback:']
        content_lower = content.lower()
        for indicator in error_indicators:
            if indicator in content_lower:
                return False
        
        return True

    async def comprehensive_evaluation(self, response_data: Dict) -> Dict:
        """Perform comprehensive evaluation of research response"""
        evaluation_results = {}
        
        # Content quality analysis
        evaluation_results['content_quality'] = await self.analyze_content_quality(response_data['content'])
        self.research_metrics['content_quality_scores'].observe(evaluation_results['content_quality'])
        
        # Fact accuracy evaluation
        evaluation_results['fact_accuracy'] = await self.evaluate_fact_accuracy(
            response_data['content'], 
            response_data.get('sources', [])
        )
        self.research_metrics['fact_accuracy_scores'].observe(evaluation_results['fact_accuracy'])
        
        # Citation quality validation
        evaluation_results['citation_quality'] = await self.validate_citations(
            response_data.get('citations', [])
        )
        self.research_metrics['citation_quality_scores'].observe(evaluation_results['citation_quality'])
        
        # Synthesis quality evaluation
        evaluation_results['synthesis_quality'] = await self.evaluate_synthesis(
            response_data['content'],
            response_data.get('sources', [])
        )
        self.research_metrics['synthesis_quality_scores'].observe(evaluation_results['synthesis_quality'])
        
        # Plagiarism detection
        evaluation_results['plagiarism_score'] = await self.detect_plagiarism(
            response_data['content'],
            response_data.get('sources', [])
        )
        
        # Source verification
        evaluation_results['source_verification'] = await self.verify_sources(
            response_data.get('sources', [])
        )
        
        return evaluation_results

    async def analyze_content_quality(self, content: str) -> float:
        """Analyze content quality based on multiple factors"""
        try:
            # Check cache first
            cache_key = f"content_quality:{hash(content)}"
            if cache_key in self.evaluation_cache:
                cached_result = self.evaluation_cache[cache_key]
                if time.time() - cached_result['timestamp'] < self.cache_ttl:
                    return cached_result['score']
            
            quality_score = 0.0
            
            # Length score (prefer longer content up to a point)
            length_score = min(len(content) / 1000, 1.0)
            quality_score += length_score * 0.2
            
            # Readability score
            readability_score = self.calculate_readability(content)
            quality_score += readability_score * 0.3
            
            # Structure score
            structure_score = self.evaluate_content_structure(content)
            quality_score += structure_score * 0.3
            
            # Completeness score
            completeness_score = self.evaluate_content_completeness(content)
            quality_score += completeness_score * 0.2
            
            # Cache result
            self.evaluation_cache[cache_key] = {
                'score': quality_score,
                'timestamp': time.time()
            }
            
            return quality_score
            
        except Exception as e:
            logging.error(f"Content quality analysis failed: {str(e)}")
            return 0.0

    def calculate_readability(self, content: str) -> float:
        """Calculate readability score using Flesch Reading Ease"""
        try:
            sentences = len(re.split(r'[.!?]+', content))
            words = len(content.split())
            syllables = self.count_syllables(content)
            
            if sentences == 0 or words == 0:
                return 0.0
            
            # Flesch Reading Ease formula
            flesch_score = 206.835 - (1.015 * (words / sentences)) - (84.6 * (syllables / words))
            
            # Normalize to 0-1 range
            normalized_score = max(0, min(1, flesch_score / 100))
            
            return normalized_score
            
        except Exception:
            return 0.5  # Default score

    def count_syllables(self, text: str) -> int:
        """Count syllables in text (simplified version)"""
        text = text.lower()
        count = 0
        vowels = "aeiouy"
        on_vowel = False
        
        for char in text:
            is_vowel = char in vowels
            if is_vowel and not on_vowel:
                count += 1
            on_vowel = is_vowel
        
        return max(count, 1)

    def evaluate_content_structure(self, content: str) -> float:
        """Evaluate content structure and organization"""
        structure_score = 0.0
        
        # Check for paragraphs
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            structure_score += 0.3
        
        # Check for headings
        headings = re.findall(r'^#+\s+', content, re.MULTILINE)
        if headings:
            structure_score += 0.2
        
        # Check for lists
        lists = re.findall(r'^\s*[-*+]\s+', content, re.MULTILINE)
        if lists:
            structure_score += 0.2
        
        # Check for logical flow indicators
        flow_indicators = ['first', 'second', 'third', 'finally', 'however', 'therefore', 'consequently']
        indicator_count = sum(1 for indicator in flow_indicators if indicator.lower() in content.lower())
        structure_score += min(indicator_count * 0.1, 0.3)
        
        return min(structure_score, 1.0)

    def evaluate_content_completeness(self, content: str) -> float:
        """Evaluate content completeness"""
        completeness_score = 0.0
        
        # Check for introduction
        if any(word in content.lower() for word in ['introduction', 'overview', 'summary']):
            completeness_score += 0.2
        
        # Check for conclusion
        if any(word in content.lower() for word in ['conclusion', 'summary', 'in conclusion']):
            completeness_score += 0.2
        
        # Check for evidence/sources
        if any(word in content.lower() for word in ['according to', 'research shows', 'studies indicate', 'source']):
            completeness_score += 0.3
        
        # Check for balanced perspective
        if any(word in content.lower() for word in ['however', 'on the other hand', 'alternatively', 'nevertheless']):
            completeness_score += 0.2
        
        # Check for specific details
        detail_indicators = ['specifically', 'in particular', 'for example', 'such as']
        detail_count = sum(1 for indicator in detail_indicators if indicator.lower() in content.lower())
        completeness_score += min(detail_count * 0.1, 0.1)
        
        return min(completeness_score, 1.0)

    async def evaluate_fact_accuracy(self, content: str, sources: List[Dict]) -> float:
        """Evaluate fact accuracy based on sources"""
        try:
            if not sources:
                return 0.5  # Neutral score when no sources provided
            
            # Simple fact checking based on source consistency
            consistency_scores = []
            
            for source in sources:
                source_content = source.get('snippet', source.get('summary', ''))
                if source_content:
                    consistency = self.check_fact_consistency(content, source_content)
                    consistency_scores.append(consistency)
            
            if consistency_scores:
                return sum(consistency_scores) / len(consistency_scores)
            else:
                return 0.5
                
        except Exception as e:
            logging.error(f"Fact accuracy evaluation failed: {str(e)}")
            return 0.5

    def check_fact_consistency(self, content: str, source_content: str) -> float:
        """Check consistency between content and source"""
        # Extract key facts (numbers, dates, names)
        content_facts = self.extract_facts(content)
        source_facts = self.extract_facts(source_content)
        
        if not content_facts or not source_facts:
            return 0.5
        
        # Calculate overlap
        matching_facts = content_facts.intersection(source_facts)
        total_facts = content_facts.union(source_facts)
        
        if not total_facts:
            return 0.5
        
        consistency = len(matching_facts) / len(total_facts)
        return consistency

    def extract_facts(self, text: str) -> set:
        """Extract key facts from text"""
        facts = set()
        
        # Extract numbers
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', text)
        facts.update(numbers)
        
        # Extract dates
        dates = re.findall(r'\b\d{1,4}[-/]\d{1,2}[-/]\d{1,4}\b', text)
        facts.update(dates)
        
        # Extract years
        years = re.findall(r'\b(?:19|20)\d{2}\b', text)
        facts.update(years)
        
        # Extract proper nouns (simplified)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        facts.update(proper_nouns[:10])  # Limit to first 10
        
        return facts

    async def validate_citations(self, citations: List[Dict]) -> float:
        """Validate citation quality and format"""
        try:
            if not citations:
                return 0.0
            
            citation_scores = []
            
            for citation in citations:
                score = self.evaluate_single_citation(citation)
                citation_scores.append(score)
            
            if citation_scores:
                return sum(citation_scores) / len(citation_scores)
            else:
                return 0.0
                
        except Exception as e:
            logging.error(f"Citation validation failed: {str(e)}")
            return 0.0

    def evaluate_single_citation(self, citation: Dict) -> float:
        """Evaluate a single citation"""
        score = 0.0
        
        # Check for required fields
        if 'text' in citation and citation['text']:
            score += 0.4
        
        if 'style' in citation and citation['style']:
            score += 0.2
        
        if 'number' in citation:
            score += 0.2
        
        # Check citation format
        text = citation.get('text', '')
        if self.is_valid_citation_format(text):
            score += 0.2
        
        return score

    def is_valid_citation_format(self, citation_text: str) -> bool:
        """Check if citation follows valid format"""
        # Check for common citation patterns
        patterns = [
            r'.*Retrieved from.*',  # APA style
            r'.*http[s]?://.*',     # Contains URL
            r'.*\([0-9]{4}\).*',    # Contains year in parentheses
        ]
        
        for pattern in patterns:
            if re.search(pattern, citation_text, re.IGNORECASE):
                return True
        
        return False

    async def evaluate_synthesis(self, content: str, sources: List[Dict]) -> float:
        """Evaluate synthesis quality"""
        try:
            synthesis_score = 0.0
            
            # Check for source integration
            if sources and len(sources) > 1:
                synthesis_score += 0.3
            
            # Check for coherent narrative
            if self.has_coherent_narrative(content):
                synthesis_score += 0.3
            
            # Check for balanced perspective
            if self.has_balanced_perspective(content):
                synthesis_score += 0.2
            
            # Check for original insights
            if self.has_original_insights(content):
                synthesis_score += 0.2
            
            return synthesis_score
            
        except Exception as e:
            logging.error(f"Synthesis evaluation failed: {str(e)}")
            return 0.0

    def has_coherent_narrative(self, content: str) -> bool:
        """Check if content has coherent narrative flow"""
        # Check for logical connectors
        connectors = ['therefore', 'consequently', 'as a result', 'thus', 'hence', 'so']
        connector_count = sum(1 for connector in connectors if connector.lower() in content.lower())
        
        # Check for paragraph structure
        paragraphs = content.split('\n\n')
        
        return connector_count > 0 or len(paragraphs) > 2

    def has_balanced_perspective(self, content: str) -> bool:
        """Check if content presents balanced perspective"""
        # Check for contrasting viewpoints
        contrast_words = ['however', 'on the other hand', 'alternatively', 'nevertheless', 'although']
        contrast_count = sum(1 for word in contrast_words if word.lower() in content.lower())
        
        return contrast_count > 0

    def has_original_insights(self, content: str) -> bool:
        """Check if content contains original insights"""
        # Check for analytical phrases
        analytical_phrases = [
            'this suggests', 'this indicates', 'this demonstrates',
            'the implications are', 'this means that', 'therefore'
        ]
        
        insight_count = sum(1 for phrase in analytical_phrases if phrase.lower() in content.lower())
        
        return insight_count > 0

    async def detect_plagiarism(self, content: str, sources: List[Dict]) -> float:
        """Detect potential plagiarism"""
        try:
            if not sources:
                return 1.0  # No sources to compare against
            
            max_similarity = 0.0
            
            for source in sources:
                source_text = source.get('snippet', source.get('summary', ''))
                if source_text:
                    similarity = self.calculate_text_similarity(content, source_text)
                    max_similarity = max(max_similarity, similarity)
            
            # Return plagiarism score (inverse of similarity)
            plagiarism_score = 1.0 - max_similarity
            return max(0.0, plagiarism_score)
            
        except Exception as e:
            logging.error(f"Plagiarism detection failed: {str(e)}")
            return 0.5

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)

    async def verify_sources(self, sources: List[Dict]) -> float:
        """Verify source credibility and accessibility"""
        try:
            if not sources:
                return 0.0
            
            verification_scores = []
            
            for source in sources:
                score = self.evaluate_source_credibility(source)
                verification_scores.append(score)
            
            if verification_scores:
                return sum(verification_scores) / len(verification_scores)
            else:
                return 0.0
                
        except Exception as e:
            logging.error(f"Source verification failed: {str(e)}")
            return 0.0

    def evaluate_source_credibility(self, source: Dict) -> float:
        """Evaluate source credibility"""
        score = 0.0
        
        # Check source type
        source_type = source.get('source', '').lower()
        if 'wikipedia' in source_type:
            score += 0.7
        elif 'academic' in source_type or 'research' in source_type:
            score += 0.9
        elif 'news' in source_type:
            score += 0.6
        else:
            score += 0.5
        
        # Check for URL
        if source.get('link') or source.get('url'):
            score += 0.2
        
        # Check for title
        if source.get('title'):
            score += 0.1
        
        return min(score, 1.0)

    def calculate_weighted_score(self, evaluation_results: Dict) -> float:
        """Calculate weighted overall score"""
        weights = self.evaluation_config
        
        weighted_score = (
            evaluation_results.get('content_quality', 0.0) * weights['content_quality_weight'] +
            evaluation_results.get('fact_accuracy', 0.0) * weights['fact_accuracy_weight'] +
            evaluation_results.get('citation_quality', 0.0) * weights['citation_quality_weight'] +
            evaluation_results.get('synthesis_quality', 0.0) * weights['synthesis_quality_weight']
        )
        
        # Apply penalties
        plagiarism_score = evaluation_results.get('plagiarism_score', 1.0)
        if plagiarism_score < (1.0 - self.evaluation_config['plagiarism_threshold']):
            weighted_score *= 0.5  # 50% penalty for high plagiarism
        
        return max(0.0, min(1.0, weighted_score))

    def update_research_performance_metrics(self, evaluation_results: Dict, evaluation_time: float):
        """Update research-specific performance metrics"""
        # Update evaluation times
        self.research_performance_metrics['evaluation_times']['overall'].append(evaluation_time)
        
        # Update score distributions
        for metric, score in evaluation_results.items():
            if isinstance(score, (int, float)):
                self.research_performance_metrics['score_distributions'][metric].append(score)
        
        # Update category scores
        category_scores = self.research_performance_metrics['category_scores']['research']
        category_scores['content_quality'].append(evaluation_results.get('content_quality', 0.0))
        category_scores['fact_accuracy'].append(evaluation_results.get('fact_accuracy', 0.0))
        category_scores['citation_quality'].append(evaluation_results.get('citation_quality', 0.0))
        category_scores['synthesis_quality'].append(evaluation_results.get('synthesis_quality', 0.0))
        
        # Keep only last 100 measurements
        for metric_list in category_scores.values():
            if len(metric_list) > 100:
                metric_list[:] = metric_list[-100:]

    async def forward(self):
        """Main forward function for research validation"""
        try:
            miner_uids = self.get_random_uids(k=self.config.neuron.sample_size)
            responses = await self.dendrite(
                axons=[self.metagraph.axons[uid] for uid in miner_uids],
                synapse=self.create_synapse(),
                deserialize=True,
            )
            
            scores = []
            for response in responses:
                if response.dendrite.status_code == 200:
                    score = await self.evaluate_research_response(response)
                    scores.append(score)
                else:
                    scores.append(0.0)
            
            self.update_scores(scores, miner_uids)
            
        except Exception as e:
            logging.error(f"Research validator error: {e}")

    def create_synapse(self):
        """Create research-specific synapse"""
        from template.protocol import Dummy
        return Dummy(
            dummy_input=f"Research task: Analyze the impact of artificial intelligence on modern society",
            category=self.category,
            task_type="comprehensive_research",
            parameters={
                "sources": ["web", "wikipedia"],
                "depth": "medium",
                "citation_style": "apa",
                "max_length": 2000
            }
        )

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agent4All Enhanced Research Validator")
    parser.add_argument("--wallet.name", default="agent4all_coldkey", help="Wallet name")
    parser.add_argument("--wallet.hotkey", default="research_validator_hotkey", help="Wallet hotkey")
    parser.add_argument("--subtensor.network", default="test", help="Bittensor network")
    parser.add_argument("--neuron.device", default="cpu", help="Device to use")
    parser.add_argument("--neuron.sample_size", default=16, type=int, help="Sample size")
    parser.add_argument("--logging.level", default="INFO", help="Logging level")
    parser.add_argument("--evaluation.timeout", default=30, type=int, help="Evaluation timeout")
    args = parser.parse_args()
    
    logging.basicConfig(
        level=getattr(logging, args.logging.level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    validator = ResearchValidator()
    try:
        validator.run()
    except KeyboardInterrupt:
        logging.info("Research validator stopped by user")
    except Exception as e:
        logging.error(f"Research validator error: {e}")

if __name__ == "__main__":
    main()
