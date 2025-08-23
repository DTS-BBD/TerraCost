import requests
from .base_cost_service import BaseCostService

class AzureCostService(BaseCostService):
    def __init__(self, region="eastus"):
        super().__init__(region)
        self.base_url = "https://prices.azure.com/api/retail/prices"
    
    def get_resource_price(self, resource_type: str, **kwargs) -> float:
        """Get price for a specific Azure resource type"""
        if resource_type == "vm":
            return self.get_vm_price(kwargs.get("vm_size"))
        elif resource_type == "sql":
            return self.get_sql_price(kwargs.get("tier"))
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")
    
    def get_vm_price(self, vm_size: str):
        cache_key = f"azure_vm_{vm_size}_{self.region}"
        cached_price = self._get_cached_price(cache_key)
        if cached_price is not None:
            return cached_price
            
        params = {
            '$filter': f"serviceName eq 'Virtual Machines' and armSkuName eq '{vm_size}' and priceType eq 'Consumption'"
        }
        data = self._make_api_request(self.base_url, params)
        if data.get('Items'):
            price = data['Items'][0]['unitPrice']
            monthly_price = price * 730
            self._cache_price(cache_key, monthly_price)
            return monthly_price
        raise Exception(f"No pricing found for VM size: {vm_size}")
    
    def get_sql_price(self, tier: str):
        cache_key = f"azure_sql_{tier}_{self.region}"
        cached_price = self._get_cached_price(cache_key)
        if cached_price is not None:
            return cached_price
            
        tier_mapping = {
            'Basic': '10 DTU',
            'Standard': '50 DTU', 
            'Premium': '125 DTU'
        }
        
        sku_name = tier_mapping.get(tier, '10 DTU')
        params = {
            '$filter': f"serviceName eq 'SQL Database' and skuName eq '{sku_name}'"
        }
        data = self._make_api_request(self.base_url, params)
        if data.get('Items'):
            monthly_price = data['Items'][0]['unitPrice']
            self._cache_price(cache_key, monthly_price)
            return monthly_price
        raise Exception(f"No pricing found for SQL tier: {tier}")
    
    def build_costs(self, config: dict):
        costs = {}
        
        if "vm" in config:
            for idx, vm in enumerate(config["vm"], start=1):
                vm_size = vm.get("vm_size", "Standard_B1s")
                costs[f"azurerm_virtual_machine.vm_{idx}"] = self.get_vm_price(vm_size)
        
        if "sql" in config:
            for idx, sql in enumerate(config["sql"], start=1):
                tier = sql.get("tier", "Basic")
                costs[f"azurerm_virtual_machine.db_{idx}"] = self.get_sql_price(tier)
        
        return costs