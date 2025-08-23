import requests

class AzureCostService:
    def __init__(self, region="eastus"):
        self.region = region
        self.base_url = "https://prices.azure.com/api/retail/prices"
    
    def get_vm_price(self, vm_size: str):
        params = {
            '$filter': f"serviceName eq 'Virtual Machines' and armSkuName eq '{vm_size}' and priceType eq 'Consumption'"
        }
        resp = requests.get(self.base_url, params=params)
        resp.raise_for_status()
        data = resp.json()
        if data.get('Items'):
            price = data['Items'][0]['unitPrice']
            return price * 730
        raise Exception(f"No pricing found for VM size: {vm_size}")
    
    def get_sql_price(self, tier: str):
        tier_mapping = {
            'Basic': '10 DTU',
            'Standard': '50 DTU', 
            'Premium': '125 DTU'
        }
        
        sku_name = tier_mapping.get(tier, '10 DTU')
        params = {
            '$filter': f"serviceName eq 'SQL Database' and skuName eq '{sku_name}'"
        }
        resp = requests.get(self.base_url, params=params)
        resp.raise_for_status()
        data = resp.json()
        if data.get('Items'):
            return data['Items'][0]['unitPrice']
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
                costs[f"azurerm_sql_database.db_{idx}"] = self.get_sql_price(tier)
        
        return costs