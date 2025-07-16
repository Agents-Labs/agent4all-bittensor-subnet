#!/usr/bin/env python3
"""
Agent4All Research Miner
Specialized miner for research tasks with comprehensive capabilities
"""

import os
import sys
import time
import logging
import asyncio
import hashlib
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import aiohttp
import requests
from bs4 import BeautifulSoup
import wikipedia
from duckduckgo_search import ddg
import numpy as np
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import bittensor as bt
from neurons.miner import Miner
from category_registry import get_category_info

class ResearchMiner(Miner):
    """Enhanced research miner with comprehensive capabilities"""
    
    def __init__(self, config=None):
        super().__init__(config=config)
        self.category = "research"
        self.category_info = get_category_info(self.category)
        
        # Research-specific configuration
        self.research_config = {
            'max_search_results': 10,
            'max_document_length': 50000,
            'search_timeout': 30,
            'synthesis_max_length': 2000,
            'supported_sources': ['web', 'wikipedia', 'academic', 'news'],
            'citation_required': True,
            'plagiarism_check': True,
            'fact_verification': True
        }
        
        # Initialize research tools
        self.research_tools = {
            'web_search': self.web_search,
            'wikipedia_search': self.wikipedia_search,
            'document_analysis': self.analyze_document,
            'synthesis': self.synthesize_information,
            'citation_generator': self.generate_citations,
            'fact_checker': self.fact_check
        }
        
        # Performance tracking
        self.performance_metrics = {
            'response_times': defaultdict(list),
            'success_rate': defaultdict(float),
            'search_accuracy': defaultdict(float),
            'synthesis_quality': defaultdict(float),
            'citation_accuracy': defaultdict(float),
            'fact_check_accuracy': defaultdict(float),
            'resource_usage': {
                'cpu': [],
                'memory': [],
                'api_calls': defaultdict(int)
            }
        }
        
        # Initialize Prometheus metrics
        self.metrics = {
            'research_requests': Counter('research_requests_total', 'Total research requests'),
            'search_requests': Counter('search_requests_total', 'Total search requests'),
            'synthesis_requests': Counter('synthesis_requests_total', 'Total synthesis requests'),
            'response_time': Histogram('research_response_time_seconds', 'Research response time'),
            'search_accuracy': Gauge('search_accuracy', 'Search accuracy score'),
            'synthesis_quality': Gauge('synthesis_quality', 'Synthesis quality score'),
            'active_research_tasks': Gauge('active_research_tasks', 'Number of active research tasks')
        }
        
        # Start Prometheus metrics server
        start_http_server(8001)
        
        # Research cache for improved performance
        self.research_cache = {}
        self.cache_ttl = 3600  # 1 hour
        
        logging.info(f"Initialized enhanced research miner with comprehensive capabilities")

    async def process_research_request(self, synapse):
        """Process research requests with comprehensive capabilities"""
        start_time = time.time()
        self.metrics['research_requests'].inc()
        self.metrics['active_research_tasks'].inc()
        
        try:
            # Parse request parameters
            request_data = self.parse_research_request(synapse)
            
            # Validate request
            if not self.validate_research_request(request_data):
                raise ValueError("Invalid research request parameters")
            
            # Execute research task
            result = await self.execute_research_task(request_data)
            
            # Calculate response time
            response_time = time.time() - start_time
            self.metrics['response_time'].observe(response_time)
            
            # Update performance metrics
            self.update_performance_metrics(request_data['task_type'], response_time, True)
            
            # Prepare response
            synapse.dummy_output = result
            synapse.category = self.category
            synapse.response_time = response_time
            synapse.success = True
            synapse.metadata = {
                'sources_used': result.get('sources', []),
                'citations': result.get('citations', []),
                'fact_check_score': result.get('fact_check_score', 0.0),
                'synthesis_quality': result.get('synthesis_quality', 0.0)
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            self.metrics['response_time'].observe(response_time)
            self.update_performance_metrics('error', response_time, False)
            
            synapse.dummy_output = f"Research error: {str(e)}"
            synapse.success = False
            synapse.response_time = response_time
            
        finally:
            self.metrics['active_research_tasks'].dec()
            
        return synapse

    def parse_research_request(self, synapse) -> Dict:
        """Parse and validate research request parameters"""
        return {
            "input": synapse.dummy_input,
            "category": self.category,
            "task_type": getattr(synapse, 'task_type', 'comprehensive_research'),
            "parameters": getattr(synapse, 'parameters', {}),
            "sources": getattr(synapse, 'sources', ['web', 'wikipedia']),
            "depth": getattr(synapse, 'depth', 'medium'),
            "citation_style": getattr(synapse, 'citation_style', 'apa'),
            "max_length": getattr(synapse, 'max_length', 2000)
        }

    def validate_research_request(self, request_data: Dict) -> bool:
        """Validate research request parameters"""
        required_fields = ['input', 'task_type']
        for field in required_fields:
            if field not in request_data or not request_data[field]:
                return False
        
        # Validate task type
        valid_task_types = [
            'comprehensive_research',
            'web_search',
            'wikipedia_research',
            'document_analysis',
            'fact_checking',
            'synthesis',
            'citation_generation'
        ]
        
        if request_data['task_type'] not in valid_task_types:
            return False
        
        # Validate sources
        if 'sources' in request_data:
            for source in request_data['sources']:
                if source not in self.research_config['supported_sources']:
                    return False
        
        return True

    async def execute_research_task(self, request_data: Dict) -> Dict:
        """Execute research task based on type"""
        task_type = request_data['task_type']
        
        if task_type == 'comprehensive_research':
            return await self.comprehensive_research(request_data)
        elif task_type == 'web_search':
            return await self.web_search_research(request_data)
        elif task_type == 'wikipedia_research':
            return await self.wikipedia_research(request_data)
        elif task_type == 'document_analysis':
            return await self.document_analysis_research(request_data)
        elif task_type == 'fact_checking':
            return await self.fact_checking_research(request_data)
        elif task_type == 'synthesis':
            return await self.synthesis_research(request_data)
        else:
            raise ValueError(f"Unsupported research task type: {task_type}")

    async def comprehensive_research(self, request_data: Dict) -> Dict:
        """Perform comprehensive research with multiple sources"""
        query = request_data['input']
        sources = request_data.get('sources', ['web', 'wikipedia'])
        
        # Check cache first
        cache_key = self.generate_cache_key(query, sources)
        if cache_key in self.research_cache:
            cached_result = self.research_cache[cache_key]
            if time.time() - cached_result['timestamp'] < self.cache_ttl:
                return cached_result['data']
        
        # Collect information from multiple sources
        research_data = {}
        
        if 'web' in sources:
            research_data['web_results'] = await self.web_search(query)
        
        if 'wikipedia' in sources:
            research_data['wikipedia_results'] = await self.wikipedia_search(query)
        
        # Analyze and synthesize information
        synthesis = await self.synthesize_information(research_data, request_data)
        
        # Generate citations
        citations = await self.generate_citations(research_data, request_data.get('citation_style', 'apa'))
        
        # Fact check the synthesis
        fact_check_score = await self.fact_check(synthesis['content'], research_data)
        
        result = {
            'content': synthesis['content'],
            'summary': synthesis['summary'],
            'sources': research_data,
            'citations': citations,
            'fact_check_score': fact_check_score,
            'synthesis_quality': synthesis['quality_score'],
            'metadata': {
                'query': query,
                'sources_used': sources,
                'timestamp': datetime.now().isoformat(),
                'word_count': len(synthesis['content'].split())
            }
        }
        
        # Cache the result
        self.research_cache[cache_key] = {
            'data': result,
            'timestamp': time.time()
        }
        
        return result

    async def web_search_research(self, request_data: Dict) -> Dict:
        """Perform web search research"""
        query = request_data['input']
        max_results = request_data.get('max_results', self.research_config['max_search_results'])
        
        self.metrics['search_requests'].inc()
        
        try:
            # Use DuckDuckGo for web search
            search_results = ddg(query, max_results=max_results)
            
            # Process and clean results
            processed_results = []
            for result in search_results:
                processed_result = {
                    'title': result.get('title', ''),
                    'link': result.get('link', ''),
                    'snippet': result.get('body', ''),
                    'source': 'web_search'
                }
                processed_results.append(processed_result)
            
            # Calculate search accuracy
            accuracy = self.calculate_search_accuracy(query, processed_results)
            self.metrics['search_accuracy'].set(accuracy)
            
            return {
                'query': query,
                'results': processed_results,
                'accuracy_score': accuracy,
                'source': 'web_search'
            }
            
        except Exception as e:
            logging.error(f"Web search failed: {str(e)}")
            return {
                'query': query,
                'results': [],
                'accuracy_score': 0.0,
                'error': str(e)
            }

    async def wikipedia_research(self, request_data: Dict) -> Dict:
        """Perform Wikipedia research"""
        query = request_data['input']
        
        try:
            # Search Wikipedia
            search_results = wikipedia.search(query, results=5)
            
            if not search_results:
                return {
                    'query': query,
                    'results': [],
                    'accuracy_score': 0.0,
                    'error': 'No Wikipedia articles found'
                }
            
            # Get detailed information for the first result
            try:
                page = wikipedia.page(search_results[0])
                summary = wikipedia.summary(search_results[0], sentences=5)
                
                result = {
                    'query': query,
                    'title': page.title,
                    'url': page.url,
                    'summary': summary,
                    'content_length': len(page.content),
                    'accuracy_score': 0.9,  # Wikipedia is generally reliable
                    'source': 'wikipedia'
                }
                
                return result
                
            except wikipedia.exceptions.DisambiguationError as e:
                # Handle disambiguation
                return {
                    'query': query,
                    'results': e.options[:5],
                    'accuracy_score': 0.7,
                    'error': 'Disambiguation required',
                    'source': 'wikipedia'
                }
                
        except Exception as e:
            logging.error(f"Wikipedia search failed: {str(e)}")
            return {
                'query': query,
                'results': [],
                'accuracy_score': 0.0,
                'error': str(e)
            }

    async def synthesize_information(self, research_data: Dict, request_data: Dict) -> Dict:
        """Synthesize information from multiple sources"""
        self.metrics['synthesis_requests'].inc()
        
        try:
            # Extract key information from research data
            key_points = []
            
            if 'web_results' in research_data:
                for result in research_data['web_results'].get('results', []):
                    key_points.append({
                        'source': 'web',
                        'content': result.get('snippet', ''),
                        'title': result.get('title', ''),
                        'reliability': 0.7
                    })
            
            if 'wikipedia_results' in research_data:
                wiki_result = research_data['wikipedia_results']
                if 'summary' in wiki_result:
                    key_points.append({
                        'source': 'wikipedia',
                        'content': wiki_result['summary'],
                        'title': wiki_result.get('title', ''),
                        'reliability': 0.9
                    })
            
            # Synthesize content
            synthesis = self.create_synthesis(key_points, request_data)
            
            # Calculate quality score
            quality_score = self.calculate_synthesis_quality(synthesis, key_points)
            self.metrics['synthesis_quality'].set(quality_score)
            
            return {
                'content': synthesis['content'],
                'summary': synthesis['summary'],
                'quality_score': quality_score,
                'key_points': len(key_points)
            }
            
        except Exception as e:
            logging.error(f"Synthesis failed: {str(e)}")
            return {
                'content': f"Error in synthesis: {str(e)}",
                'summary': "Synthesis failed",
                'quality_score': 0.0,
                'key_points': 0
            }

    def create_synthesis(self, key_points: List[Dict], request_data: Dict) -> Dict:
        """Create synthesis from key points"""
        max_length = request_data.get('max_length', self.research_config['synthesis_max_length'])
        
        # Sort by reliability
        sorted_points = sorted(key_points, key=lambda x: x['reliability'], reverse=True)
        
        # Create content
        content_parts = []
        summary_parts = []
        
        for point in sorted_points:
            if len(' '.join(content_parts)) < max_length:
                content_parts.append(point['content'])
                if len(' '.join(summary_parts)) < 200:  # Keep summary short
                    summary_parts.append(point['content'][:100] + "...")
        
        content = ' '.join(content_parts)
        summary = ' '.join(summary_parts)
        
        # Truncate if necessary
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return {
            'content': content,
            'summary': summary
        }

    async def generate_citations(self, research_data: Dict, citation_style: str = 'apa') -> List[Dict]:
        """Generate citations for research data"""
        citations = []
        
        if 'web_results' in research_data:
            for i, result in enumerate(research_data['web_results'].get('results', [])):
                citation = self.format_citation(result, citation_style, i + 1)
                citations.append(citation)
        
        if 'wikipedia_results' in research_data:
            wiki_result = research_data['wikipedia_results']
            if 'title' in wiki_result and 'url' in wiki_result:
                citation = self.format_citation(wiki_result, citation_style, len(citations) + 1)
                citations.append(citation)
        
        return citations

    def format_citation(self, source: Dict, style: str, number: int) -> Dict:
        """Format citation according to specified style"""
        if style == 'apa':
            return {
                'number': number,
                'text': f"{source.get('title', 'Unknown')}. Retrieved from {source.get('link', source.get('url', 'Unknown'))}",
                'style': 'apa'
            }
        elif style == 'mla':
            return {
                'number': number,
                'text': f'"{source.get("title", "Unknown")}." {source.get("link", source.get("url", "Unknown"))}',
                'style': 'mla'
            }
        else:
            return {
                'number': number,
                'text': f"[{number}] {source.get('title', 'Unknown')} - {source.get('link', source.get('url', 'Unknown'))}",
                'style': 'numbered'
            }

    async def fact_check(self, content: str, sources: Dict) -> float:
        """Perform fact checking on content"""
        try:
            # Simple fact checking based on source consistency
            fact_check_score = 0.0
            
            # Check if content is consistent with sources
            if 'wikipedia_results' in sources:
                wiki_content = sources['wikipedia_results'].get('summary', '')
                if wiki_content and self.check_content_consistency(content, wiki_content):
                    fact_check_score += 0.4
            
            if 'web_results' in sources:
                web_results = sources['web_results'].get('results', [])
                consistency_count = 0
                for result in web_results:
                    if self.check_content_consistency(content, result.get('snippet', '')):
                        consistency_count += 1
                
                if web_results:
                    fact_check_score += 0.6 * (consistency_count / len(web_results))
            
            return min(fact_check_score, 1.0)
            
        except Exception as e:
            logging.error(f"Fact checking failed: {str(e)}")
            return 0.0

    def check_content_consistency(self, content: str, source_content: str) -> bool:
        """Check if content is consistent with source"""
        # Simple keyword-based consistency check
        content_words = set(content.lower().split())
        source_words = set(source_content.lower().split())
        
        # Calculate overlap
        overlap = len(content_words.intersection(source_words))
        total_unique = len(content_words.union(source_words))
        
        if total_unique == 0:
            return False
        
        consistency_ratio = overlap / total_unique
        return consistency_ratio > 0.1  # 10% overlap threshold

    def calculate_search_accuracy(self, query: str, results: List[Dict]) -> float:
        """Calculate search accuracy based on query relevance"""
        if not results:
            return 0.0
        
        # Simple relevance scoring based on query terms
        query_terms = set(query.lower().split())
        total_relevance = 0.0
        
        for result in results:
            title_terms = set(result.get('title', '').lower().split())
            snippet_terms = set(result.get('snippet', '').lower().split())
            
            title_overlap = len(query_terms.intersection(title_terms)) / len(query_terms) if query_terms else 0
            snippet_overlap = len(query_terms.intersection(snippet_terms)) / len(query_terms) if query_terms else 0
            
            relevance = (title_overlap * 0.7) + (snippet_overlap * 0.3)
            total_relevance += relevance
        
        return total_relevance / len(results)

    def calculate_synthesis_quality(self, synthesis: Dict, key_points: List[Dict]) -> float:
        """Calculate synthesis quality score"""
        if not key_points:
            return 0.0
        
        # Quality factors
        content_length = len(synthesis['content'])
        source_diversity = len(set(point['source'] for point in key_points))
        avg_reliability = sum(point['reliability'] for point in key_points) / len(key_points)
        
        # Normalize factors
        length_score = min(content_length / 1000, 1.0)  # Prefer longer content up to 1000 chars
        diversity_score = min(source_diversity / 3, 1.0)  # Prefer multiple sources
        
        # Calculate overall quality
        quality = (length_score * 0.3) + (diversity_score * 0.3) + (avg_reliability * 0.4)
        
        return quality

    def generate_cache_key(self, query: str, sources: List[str]) -> str:
        """Generate cache key for research query"""
        cache_string = f"{query}:{':'.join(sorted(sources))}"
        return hashlib.md5(cache_string.encode()).hexdigest()

    def update_performance_metrics(self, task_type: str, response_time: float, success: bool):
        """Update performance metrics"""
        self.performance_metrics['response_times'][task_type].append(response_time)
        
        # Keep only last 100 measurements
        if len(self.performance_metrics['response_times'][task_type]) > 100:
            self.performance_metrics['response_times'][task_type] = \
                self.performance_metrics['response_times'][task_type][-100:]
        
        # Update success rate
        if task_type not in self.performance_metrics['success_rate']:
            self.performance_metrics['success_rate'][task_type] = 0.0
        
        current_success_rate = self.performance_metrics['success_rate'][task_type]
        if success:
            self.performance_metrics['success_rate'][task_type] = \
                (current_success_rate * 0.9) + 0.1
        else:
            self.performance_metrics['success_rate'][task_type] = \
                current_success_rate * 0.9

    async def forward(self, synapse):
        """Main forward function for research requests"""
        return await self.process_research_request(synapse)

    async def blacklist(self, synapse):
        """Blacklist function for research requests"""
        # Basic blacklisting - can be enhanced with more sophisticated logic
        return False, "Research request accepted"

    async def priority(self, synapse):
        """Priority function for research requests"""
        # Research tasks get medium priority
        return 0.7

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Agent4All Enhanced Research Miner")
    parser.add_argument("--wallet.name", default="agent4all_coldkey", help="Wallet name")
    parser.add_argument("--wallet.hotkey", default="research_hotkey", help="Wallet hotkey")
    parser.add_argument("--subtensor.network", default="test", help="Bittensor network")
    parser.add_argument("--neuron.device", default="cpu", help="Device to use")
    parser.add_argument("--logging.level", default="INFO", help="Logging level")
    parser.add_argument("--research.max_results", default=10, type=int, help="Max search results")
    parser.add_argument("--research.timeout", default=30, type=int, help="Search timeout")
    args = parser.parse_args()
    
    logging.basicConfig(
        level=getattr(logging, args.logging.level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    miner = ResearchMiner()
    try:
        miner.run()
    except KeyboardInterrupt:
        logging.info("Research miner stopped by user")
    except Exception as e:
        logging.error(f"Research miner error: {e}")

if __name__ == "__main__":
    main()
