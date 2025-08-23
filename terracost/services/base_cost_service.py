from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import requests
import time

class BaseCostService(ABC):
    """Base class for cloud provider cost services"""
    
    def __init__(self, region: str = "us-east-1"):
        self.region = region
        self._pricing_cache = {}
        self._cache_ttl = 3600  # 1 hour cache
    
    @abstractmethod
    def get_resource_price(self, resource_type: str, **kwargs) -> float:
        """Get price for a specific resource type"""
        pass
    
    @abstractmethod
    def build_costs(self, config: Dict[str, Any]) -> Dict[str, float]:
        """Build cost breakdown from infrastructure configuration"""
        pass
    
    def _get_cached_price(self, cache_key: str) -> Optional[float]:
        """Get cached price if still valid"""
        if cache_key in self._pricing_cache:
            timestamp, price = self._pricing_cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return price
        return None
    
    def _cache_price(self, cache_key: str, price: float):
        """Cache a price with timestamp"""
        self._pricing_cache[cache_key] = (time.time(), price)
    
    def _make_api_request(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make API request with retry logic and error handling"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(f"API request failed after {max_retries} attempts: {str(e)}")
                time.sleep(retry_delay)
                retry_delay *= 2
        
        raise Exception("Unexpected error in API request")
    
    def estimate_uncertainty(self, base_cost: float, timeframe_months: float) -> Dict[str, float]:
        """
        Estimate cost uncertainty using Monte Carlo simulation
        Returns confidence intervals for cost estimation
        """
        import random
        import numpy as np
        
        # Simulate cost variations based on historical patterns
        # This is a simplified model - in production you'd use more sophisticated data
        
        # Cost volatility factors (monthly variations)
        volatility_factors = {
            'low': 0.05,    # 5% monthly variation
            'medium': 0.10,  # 10% monthly variation  
            'high': 0.20     # 20% monthly variation
        }
        
        # Determine volatility based on timeframe and cost
        if timeframe_months <= 1:
            volatility = volatility_factors['low']
        elif timeframe_months <= 6:
            volatility = volatility_factors['medium']
        else:
            volatility = volatility_factors['high']
        
        # Monte Carlo simulation
        n_simulations = 1000
        monthly_costs = []
        
        for _ in range(n_simulations):
            monthly_cost = base_cost
            for month in range(int(timeframe_months)):
                # Add random variation each month
                variation = random.gauss(0, volatility)
                monthly_cost *= (1 + variation)
            monthly_costs.append(monthly_cost)
        
        monthly_costs = np.array(monthly_costs)
        
        # Calculate confidence intervals
        confidence_68 = np.percentile(monthly_costs, [16, 84])  # 68% confidence
        confidence_95 = np.percentile(monthly_costs, [2.5, 97.5])  # 95% confidence
        
        return {
            'base_cost': base_cost,
            'timeframe_months': timeframe_months,
            'confidence_68_lower': confidence_68[0],
            'confidence_68_upper': confidence_68[1],
            'confidence_95_lower': confidence_95[0],
            'confidence_95_upper': confidence_95[1],
            'volatility': volatility,
            'std_deviation': np.std(monthly_costs)
        }
