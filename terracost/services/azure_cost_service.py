import requests
from .base_cost_service import BaseCostService
from typing import Dict, Any, Optional, List

class AzureCostService(BaseCostService):
    """
    Azure cost service using Azure Retail Prices API for real-time pricing
    Supports all Azure resource types through dynamic API calls
    """
    
    BASE_URL = "https://prices.azure.com/api/retail/prices"
    API_VERSION = "2021-10-01-preview"
    
    def __init__(self, region: str = "eastus"):
        super().__init__(region)
        self.region = region
        self.region_name_map = {
            "eastus": "US East",
            "westus": "US West", 
            "centralus": "US Central",
            "northeurope": "Europe North",
            "westeurope": "Europe West",
            "eastasia": "Asia Pacific East",
            "southeastasia": "Asia Pacific Southeast",
            "australiaeast": "Australia East",
            "australiasoutheast": "Australia Southeast",
            "brazilsouth": "Brazil South",
            "canadacentral": "Canada Central",
            "canadaeast": "Canada East",
            "japaneast": "Japan East",
            "japanwest": "Japan West",
            "koreacentral": "Korea Central",
            "koreasouth": "Korea South",
            "southafricanorth": "South Africa North",
            "southafricawest": "South Africa West",
            "uksouth": "UK South",
            "ukwest": "UK West"
        }
        
        # Azure service mappings for resource types
        self.service_mappings = {
            # Compute
            'azurerm_virtual_machine': 'Virtual Machines',
            'azurerm_vmss': 'Virtual Machine Scale Sets',
            'azurerm_container_group': 'Container Instances',
            'azurerm_kubernetes_cluster': 'Azure Kubernetes Service',
            'azurerm_app_service': 'App Service',
            'azurerm_function_app': 'Azure Functions',
            'azurerm_batch_account': 'Azure Batch',
            'azurerm_service_fabric_cluster': 'Service Fabric',
            
            # Storage
            'azurerm_storage_account': 'Storage',
            'azurerm_storage_container': 'Storage',
            'azurerm_storage_blob': 'Storage',
            'azurerm_storage_file_share': 'Storage',
            'azurerm_storage_queue': 'Storage',
            'azurerm_storage_table': 'Storage',
            'azurerm_managed_disk': 'Storage',
            'azurerm_snapshot': 'Storage',
            
            # Database
            'azurerm_sql_server': 'Azure SQL Database',
            'azurerm_sql_database': 'Azure SQL Database',
            'azurerm_mysql_server': 'Azure Database for MySQL',
            'azurerm_postgresql_server': 'Azure Database for PostgreSQL',
            'azurerm_cosmosdb_account': 'Azure Cosmos DB',
            'azurerm_redis_cache': 'Azure Cache for Redis',
            'azurerm_data_factory': 'Azure Data Factory',
            'azurerm_data_lake_store': 'Azure Data Lake Storage',
            
            # Networking
            'azurerm_virtual_network': 'Virtual Network',
            'azurerm_subnet': 'Virtual Network',
            'azurerm_network_security_group': 'Virtual Network',
            'azurerm_network_interface': 'Virtual Network',
            'azurerm_public_ip': 'Virtual Network',
            'azurerm_load_balancer': 'Load Balancer',
            'azurerm_application_gateway': 'Application Gateway',
            'azurerm_vpn_gateway': 'VPN Gateway',
            'azurerm_express_route_circuit': 'ExpressRoute',
            'azurerm_cdn_profile': 'Content Delivery Network',
            
            # Security & Identity
            'azurerm_key_vault': 'Key Vault',
            'azurerm_active_directory_domain_service': 'Azure Active Directory',
            'azurerm_role_assignment': 'Azure Active Directory',
            'azurerm_role_definition': 'Azure Active Directory',
            
            # AI & ML
            'azurerm_machine_learning_workspace': 'Machine Learning',
            'azurerm_cognitive_account': 'Cognitive Services',
            'azurerm_search_service': 'Azure Cognitive Search',
            
            # Analytics
            'azurerm_hdinsight_hadoop_cluster': 'HDInsight',
            'azurerm_stream_analytics_job': 'Stream Analytics',
            'azurerm_data_lake_analytics_account': 'Data Lake Analytics',
            'azurerm_event_hub_namespace': 'Event Hubs',
            'azurerm_service_bus_namespace': 'Service Bus',
            
            # Monitoring
            'azurerm_monitor_action_group': 'Azure Monitor',
            'azurerm_log_analytics_workspace': 'Log Analytics',
            'azurerm_application_insights': 'Application Insights',
            
            # Integration
            'azurerm_logic_app_workflow': 'Logic Apps',
            'azurerm_api_management': 'API Management',
            'azurerm_event_grid_topic': 'Event Grid',
            
            # Developer Tools
            'azurerm_dev_test_lab': 'DevTest Labs',
            'azurerm_spring_cloud_service': 'Azure Spring Cloud',
            'azurerm_static_site': 'Static Web Apps'
        }

    def get_resource_price(self, resource_type: str, **kwargs) -> float:
        """
        Get price for any Azure resource type using real-time API calls
        """
        # Map resource type to Azure service
        azure_service = self._get_azure_service_from_resource_type(resource_type)
        
        # Get pricing based on service type
        if azure_service == "Virtual Machines":
            return self._get_vm_price(kwargs.get("size"), kwargs.get("os_type", "Linux"))
        elif azure_service == "Storage":
            return self._get_storage_price(kwargs.get("storage_gb", 50), kwargs.get("tier", "Standard"))
        elif azure_service == "Azure SQL Database":
            return self._get_sql_database_price(kwargs.get("edition", "Basic"), kwargs.get("dtu", 5))
        elif azure_service == "App Service":
            return self._get_app_service_price(kwargs.get("sku", "Basic"), kwargs.get("size", "B1"))
        else:
            # Generic pricing for other services
            return self._get_generic_azure_price(azure_service, kwargs)

    def _get_azure_service_from_resource_type(self, resource_type: str) -> str:
        """Map Terraform resource type to Azure service name"""
        return self.service_mappings.get(resource_type, resource_type.replace('azurerm_', ''))

    def _get_vm_price(self, size: str, os_type: str = "Linux") -> float:
        """Get VM pricing from Azure Retail Prices API"""
        try:
            # Build API query for VM pricing - use simpler filter
            params = {
                'api-version': self.API_VERSION,
                '$filter': f"serviceName eq 'Virtual Machines' and armRegionName eq '{self.region}' and type eq 'Consumption'"
            }
            
            response = self._make_api_request(self.BASE_URL, params)
            
            if response and 'Items' in response:
                # Find the best matching VM size
                for item in response['Items']:
                    if (item.get('unitPrice') and 
                        item.get('currencyCode') == 'USD' and
                        item.get('skuName', '').startswith(size.split('_')[0])):  # Match size prefix
                        # Convert hourly price to monthly (730 hours per month)
                        hourly_price = float(item['unitPrice'])
                        return hourly_price * 730
            
            return 0.0
        except Exception as e:
            print(f"Warning: Could not get VM pricing for {size}: {e}")
            return 0.0

    def _get_storage_price(self, storage_gb: float, tier: str = "Standard") -> float:
        """Get storage pricing from Azure Retail Prices API"""
        try:
            params = {
                'api-version': self.API_VERSION,
                '$filter': f"serviceName eq 'Storage' and armRegionName eq '{self.region}' and type eq 'Consumption'"
            }
            
            response = self._make_api_request(self.BASE_URL, params)
            
            if response and 'Items' in response:
                # Find storage pricing for the tier
                for item in response['Items']:
                    if (item.get('unitPrice') and 
                        item.get('currencyCode') == 'USD' and
                        'blob' in item.get('productName', '').lower()):  # Look for blob storage
                        # Get price per GB per month
                        price_per_gb = float(item['unitPrice'])
                        return price_per_gb * storage_gb
            
            return 0.0
        except Exception as e:
            print(f"Warning: Could not get storage pricing: {e}")
            return 0.0

    def _get_sql_database_price(self, edition: str, dtu: int) -> float:
        """Get SQL Database pricing from Azure Retail Prices API"""
        try:
            params = {
                'api-version': self.API_VERSION,
                '$filter': f"serviceName eq 'Azure SQL Database' and armRegionName eq '{self.region}' and type eq 'Consumption'"
            }
            
            response = self._make_api_request(self.BASE_URL, params)
            
            if response and 'Items' in response:
                # Find SQL Database pricing
                for item in response['Items']:
                    if (item.get('unitPrice') and 
                        item.get('currencyCode') == 'USD' and
                        'dtu' in item.get('productName', '').lower()):  # Look for DTU-based pricing
                        # Convert hourly price to monthly
                        hourly_price = float(item['unitPrice'])
                        return hourly_price * 730
            
            return 0.0
        except Exception as e:
            print(f"Warning: Could not get SQL Database pricing: {e}")
            return 0.0

    def _get_app_service_price(self, sku: str, size: str) -> float:
        """Get App Service pricing from Azure Retail Prices API"""
        try:
            params = {
                'api-version': self.API_VERSION,
                '$filter': f"serviceName eq 'App Service' and armRegionName eq '{self.region}' and type eq 'Consumption'"
            }
            
            response = self._make_api_request(self.BASE_URL, params)
            
            if response and 'Items' in response:
                # Find App Service pricing
                for item in response['Items']:
                    if (item.get('unitPrice') and 
                        item.get('currencyCode') == 'USD' and
                        'plan' in item.get('productName', '').lower()):  # Look for plan-based pricing
                        # Convert hourly price to monthly
                        hourly_price = float(item['unitPrice'])
                        return hourly_price * 730
            
            return 0.0
        except Exception as e:
            print(f"Warning: Could not get App Service pricing: {e}")
            return 0.0

    def _get_generic_azure_price(self, service: str, config: dict) -> float:
        """Get generic pricing for any Azure service"""
        try:
            # Try to get pricing from Azure Retail Prices API with a simpler filter
            params = {
                'api-version': self.API_VERSION,
                '$filter': f"serviceName eq '{service}' and armRegionName eq '{self.region}'"
            }
            
            response = self._make_api_request(self.BASE_URL, params)
            
            if response and 'Items' in response:
                # Get the first available price
                for item in response['Items']:
                    if item.get('unitPrice') and item.get('currencyCode') == 'USD':
                        hourly_price = float(item['unitPrice'])
                        return hourly_price * 730  # Monthly estimate
            
            # Fallback: return a reasonable default based on service type
            return self._get_fallback_price(service)
            
        except Exception as e:
            print(f"Warning: Could not get pricing for {service}: {e}")
            return self._get_fallback_price(service)

    def _get_fallback_price(self, service: str) -> float:
        """Provide reasonable fallback prices when API calls fail"""
        fallback_prices = {
            'Virtual Machines': 50.0,      # $50/month for basic VM
            'Storage': 0.02,               # $0.02/GB/month
            'Azure SQL Database': 5.0,     # $5/month for basic DB
            'App Service': 13.0,           # $13/month for basic plan
            'Virtual Network': 0.0,        # Free
            'Load Balancer': 18.0,         # $18/month
            'Key Vault': 0.03,             # $0.03 per 10K operations
            'Machine Learning': 100.0,     # $100/month for basic workspace
            'HDInsight': 200.0,            # $200/month for basic cluster
            'Event Hubs': 10.0,            # $10/month for basic namespace
            'Service Bus': 10.0,           # $10/month for basic namespace
            'Logic Apps': 0.0,             # Free for basic
            'API Management': 50.0,        # $50/month for developer tier
            'Content Delivery Network': 0.0,  # Free for basic
            'VPN Gateway': 27.0,           # $27/month
            'ExpressRoute': 500.0,         # $500/month for basic circuit
        }
        
        return fallback_prices.get(service, 10.0)  # Default $10/month

    def build_costs(self, config: dict) -> Dict[str, float]:
        """
        Build cost breakdown for Azure infrastructure configuration
        Uses real-time API calls to get accurate pricing
        """
        costs = {}
        
        for resource_type, resource_list in config.items():
            if not isinstance(resource_list, list):
                continue
                
            for resource in resource_list:
                resource_name = resource.get('name', 'unknown')
                resource_config = resource.get('config', {})
                
                # Generate unique key
                key = f"{resource_type}.{resource_name}"
                
                # Calculate cost using real-time API
                cost = self._calculate_resource_cost(resource_type, resource_config)
                
                if cost > 0:
                    costs[key] = cost
        
        return costs

    def _calculate_resource_cost(self, resource_type: str, config: dict) -> float:
        """Calculate cost for a specific Azure resource"""
        try:
            # Extract relevant configuration parameters
            size = config.get('size', config.get('sku', 'Standard'))
            os_type = config.get('os_type', 'Linux')
            storage_gb = config.get('storage_gb', 50)
            tier = config.get('tier', 'Standard')
            edition = config.get('edition', 'Basic')
            dtu = config.get('dtu', 5)
            
            # Get real-time pricing
            return self.get_resource_price(
                resource_type,
                size=size,
                os_type=os_type,
                storage_gb=storage_gb,
                tier=tier,
                edition=edition,
                dtu=dtu
            )
            
        except Exception as e:
            print(f"Warning: Error calculating cost for {resource_type}: {e}")
            return 0.0

    def get_region_name(self) -> str:
        """Get human-readable region name"""
        return self.region_name_map.get(self.region, self.region)

    def estimate_uncertainty(self, base_cost: float, timeframe_months: float) -> Dict[str, float]:
        """
        Estimate cost uncertainty for Azure resources
        Azure pricing tends to be more stable than AWS
        """
        # Azure pricing is generally more predictable
        volatility_factors = {
            'low': 0.03,     # 3% monthly variation (lower than AWS)
            'medium': 0.06,  # 6% monthly variation
            'high': 0.12     # 12% monthly variation
        }
        
        # Use the same uncertainty calculation as base class
        return super().estimate_uncertainty(base_cost, timeframe_months)
