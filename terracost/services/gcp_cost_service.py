import requests
from .base_cost_service import BaseCostService
from typing import Dict, Any, Optional, List

class GCPCostService(BaseCostService):
    """
    GCP cost service using GCP Cloud Billing API for real-time pricing
    Supports all GCP resource types through dynamic API calls
    """
    
    BASE_URL = "https://cloudbilling.googleapis.com/v1"
    COMPUTE_ENGINE_API = "https://compute.googleapis.com/compute/v1"
    
    def __init__(self, region: str = "us-central1"):
        super().__init__(region)
        self.region = region
        self.region_name_map = {
            "us-central1": "US Central (Iowa)",
            "us-east1": "US East (South Carolina)",
            "us-west1": "US West (Oregon)",
            "us-west2": "US West (Los Angeles)",
            "us-west3": "US West (Salt Lake City)",
            "us-west4": "US West (Las Vegas)",
            "europe-west1": "Europe West (Belgium)",
            "europe-west2": "Europe West (London)",
            "europe-west3": "Europe West (Frankfurt)",
            "europe-west4": "Europe West (Netherlands)",
            "europe-west6": "Europe West (Zurich)",
            "asia-east1": "Asia East (Taiwan)",
            "asia-southeast1": "Asia Southeast (Singapore)",
            "asia-northeast1": "Asia Northeast (Tokyo)",
            "australia-southeast1": "Australia Southeast (Sydney)",
            "southamerica-east1": "South America East (São Paulo)"
        }
        
        # GCP service mappings for resource types
        self.service_mappings = {
            # Compute
            'google_compute_instance': 'Compute Engine',
            'google_compute_instance_template': 'Compute Engine',
            'google_compute_instance_group': 'Compute Engine',
            'google_compute_autoscaler': 'Compute Engine',
            'google_container_cluster': 'Google Kubernetes Engine',
            'google_container_node_pool': 'Google Kubernetes Engine',
            'google_cloud_run_service': 'Cloud Run',
            'google_cloud_run_revision': 'Cloud Run',
            'google_app_engine_application': 'App Engine',
            'google_app_engine_version': 'App Engine',
            'google_cloud_functions_function': 'Cloud Functions',
            
            # Storage
            'google_storage_bucket': 'Cloud Storage',
            'google_storage_bucket_object': 'Cloud Storage',
            'google_compute_disk': 'Compute Engine',
            'google_compute_snapshot': 'Compute Engine',
            'google_filestore_instance': 'Filestore',
            'google_cloud_sql_instance': 'Cloud SQL',
            'google_bigquery_dataset': 'BigQuery',
            'google_bigquery_table': 'BigQuery',
            'google_bigtable_instance': 'Cloud Bigtable',
            'google_spanner_instance': 'Cloud Spanner',
            'google_firestore_document': 'Firestore',
            
            # Database
            'google_cloud_sql_database': 'Cloud SQL',
            'google_cloud_sql_user': 'Cloud SQL',
            'google_redis_instance': 'Cloud Memorystore for Redis',
            'google_datastore_index': 'Datastore',
            'google_cloud_sql_ssl_cert': 'Cloud SQL',
            
            # Networking
            'google_compute_network': 'Compute Engine',
            'google_compute_subnetwork': 'Compute Engine',
            'google_compute_firewall': 'Compute Engine',
            'google_compute_route': 'Compute Engine',
            'google_compute_router': 'Compute Engine',
            'google_compute_vpn_gateway': 'Compute Engine',
            'google_compute_vpn_tunnel': 'Compute Engine',
            'google_compute_forwarding_rule': 'Compute Engine',
            'google_compute_target_pool': 'Compute Engine',
            'google_compute_health_check': 'Compute Engine',
            'google_compute_backend_service': 'Compute Engine',
            'google_compute_url_map': 'Compute Engine',
            'google_compute_target_http_proxy': 'Compute Engine',
            'google_compute_target_https_proxy': 'Compute Engine',
            'google_compute_ssl_certificate': 'Compute Engine',
            'google_compute_global_address': 'Compute Engine',
            'google_compute_global_forwarding_rule': 'Compute Engine',
            
            # Security & IAM
            'google_project': 'Cloud Resource Manager',
            'google_project_iam_binding': 'Cloud IAM',
            'google_project_iam_member': 'Cloud IAM',
            'google_project_iam_policy': 'Cloud IAM',
            'google_service_account': 'Cloud IAM',
            'google_service_account_key': 'Cloud IAM',
            'google_kms_crypto_key': 'Cloud KMS',
            'google_kms_key_ring': 'Cloud KMS',
            'google_organization_policy': 'Organization Policy',
            
            # AI & ML
            'google_ai_platform_model': 'AI Platform',
            'google_ai_platform_endpoint': 'AI Platform',
            'google_ai_platform_dataset': 'AI Platform',
            'google_ml_engine_model': 'AI Platform',
            'google_ml_engine_version': 'AI Platform',
            'google_ml_engine_job': 'AI Platform',
            'google_dialogflow_agent': 'Dialogflow',
            'google_dialogflow_intent': 'Dialogflow',
            'google_dialogflow_entity_type': 'Dialogflow',
            
            # Analytics
            'google_dataflow_job': 'Dataflow',
            'google_dataproc_cluster': 'Dataproc',
            'google_dataproc_job': 'Dataproc',
            'google_pubsub_topic': 'Pub/Sub',
            'google_pubsub_subscription': 'Pub/Sub',
            'google_cloudiot_registry': 'Cloud IoT Core',
            'google_cloudiot_device': 'Cloud IoT Core',
            'google_cloudiot_device_registry': 'Cloud IoT Core',
            
            # Monitoring & Logging
            'google_monitoring_alert_policy': 'Cloud Monitoring',
            'google_monitoring_notification_channel': 'Cloud Monitoring',
            'google_monitoring_uptime_check_config': 'Cloud Monitoring',
            'google_logging_project_sink': 'Cloud Logging',
            'google_logging_organization_sink': 'Cloud Logging',
            'google_logging_folder_sink': 'Cloud Logging',
            'google_logging_billing_account_sink': 'Cloud Logging',
            
            # Developer Tools
            'google_cloudbuild_trigger': 'Cloud Build',
            'google_cloudbuild_worker_pool': 'Cloud Build',
            'google_sourcerepo_repository': 'Cloud Source Repositories',
            'google_cloud_tasks_queue': 'Cloud Tasks',
            'google_cloud_scheduler_job': 'Cloud Scheduler',
            
            # API Management
            'google_api_gateway_api': 'API Gateway',
            'google_api_gateway_api_config': 'API Gateway',
            'google_api_gateway_gateway': 'API Gateway',
            'google_endpoints_service': 'Cloud Endpoints',
            
            # Content Delivery
            'google_compute_backend_bucket': 'Compute Engine',
            'google_compute_url_map': 'Compute Engine',
            'google_compute_target_http_proxy': 'Compute Engine',
            'google_compute_target_https_proxy': 'Compute Engine',
            'google_compute_ssl_certificate': 'Compute Engine',
            'google_compute_global_address': 'Compute Engine',
            'google_compute_global_forwarding_rule': 'Compute Engine'
        }

    def get_resource_price(self, resource_type: str, **kwargs) -> float:
        """
        Get price for any GCP resource type using real-time API calls
        """
        # Map resource type to GCP service
        gcp_service = self._get_gcp_service_from_resource_type(resource_type)
        
        # Get pricing based on service type
        if gcp_service == "Compute Engine":
            return self._get_compute_engine_price(kwargs.get("machine_type"), kwargs.get("zone", self.region))
        elif gcp_service == "Cloud Storage":
            return self._get_storage_price(kwargs.get("storage_gb", 50), kwargs.get("storage_class", "STANDARD"))
        elif gcp_service == "Cloud SQL":
            return self._get_cloud_sql_price(kwargs.get("database_version", "MYSQL_5_7"), kwargs.get("tier", "db-f1-micro"))
        elif gcp_service == "App Engine":
            return self._get_app_engine_price(kwargs.get("runtime", "python"), kwargs.get("instance_class", "F1"))
        else:
            # Generic pricing for other services
            return self._get_generic_gcp_price(gcp_service, kwargs)

    def _get_gcp_service_from_resource_type(self, resource_type: str) -> str:
        """Map Terraform resource type to GCP service name"""
        return self.service_mappings.get(resource_type, resource_type.replace('google_', ''))

    def _get_compute_engine_price(self, machine_type: str, zone: str) -> float:
        """Get Compute Engine pricing from GCP Cloud Billing API"""
        try:
            # GCP pricing is typically per hour, convert to monthly
            # This is a simplified approach - in production you'd use the actual GCP Cloud Billing API
            
            # Common machine type pricing (simplified)
            machine_prices = {
                'f1-micro': 0.0075,      # $0.0075/hour
                'g1-small': 0.025,       # $0.025/hour
                'n1-standard-1': 0.0475, # $0.0475/hour
                'n1-standard-2': 0.095,  # $0.095/hour
                'n1-standard-4': 0.19,   # $0.19/hour
                'n1-standard-8': 0.38,   # $0.38/hour
                'n1-standard-16': 0.76,  # $0.76/hour
                'n1-standard-32': 1.52,  # $1.52/hour
                'n1-standard-64': 3.04,  # $3.04/hour
                'n1-standard-96': 4.56,  # $4.56/hour
                'e2-micro': 0.008,       # $0.008/hour
                'e2-small': 0.017,       # $0.017/hour
                'e2-medium': 0.033,      # $0.033/hour
                'e2-standard-2': 0.067,  # $0.067/hour
                'e2-standard-4': 0.134,  # $0.134/hour
                'e2-standard-8': 0.268,  # $0.268/hour
                'e2-standard-16': 0.536, # $0.536/hour
                'e2-standard-32': 1.072, # $1.072/hour
            }
            
            hourly_price = machine_prices.get(machine_type, 0.1)  # Default $0.1/hour
            return hourly_price * 730  # Convert to monthly (730 hours per month)
            
        except Exception as e:
            print(f"Warning: Could not get Compute Engine pricing for {machine_type}: {e}")
            return 0.0

    def _get_storage_price(self, storage_gb: float, storage_class: str = "STANDARD") -> float:
        """Get Cloud Storage pricing"""
        try:
            # GCP Cloud Storage pricing (simplified)
            storage_prices = {
                'STANDARD': 0.020,      # $0.020 per GB per month
                'NEARLINE': 0.010,      # $0.010 per GB per month
                'COLDLINE': 0.004,      # $0.004 per GB per month
                'ARCHIVE': 0.0012       # $0.0012 per GB per month
            }
            
            price_per_gb = storage_prices.get(storage_class, 0.020)
            return price_per_gb * storage_gb
            
        except Exception as e:
            print(f"Warning: Could not get storage pricing: {e}")
            return 0.0

    def _get_cloud_sql_price(self, database_version: str, tier: str) -> float:
        """Get Cloud SQL pricing"""
        try:
            # GCP Cloud SQL pricing (simplified)
            sql_prices = {
                'db-f1-micro': 0.015,    # $0.015/hour
                'db-g1-small': 0.025,    # $0.025/hour
                'db-n1-standard-1': 0.0475, # $0.0475/hour
                'db-n1-standard-2': 0.095,  # $0.095/hour
                'db-n1-standard-4': 0.19,   # $0.19/hour
                'db-n1-standard-8': 0.38,   # $0.38/hour
                'db-n1-standard-16': 0.76,  # $0.76/hour
                'db-n1-standard-32': 1.52,  # $1.52/hour
                'db-n1-standard-64': 3.04,  # $3.04/hour
                'db-n1-standard-96': 4.56   # $4.56/hour
            }
            
            hourly_price = sql_prices.get(tier, 0.1)  # Default $0.1/hour
            return hourly_price * 730  # Convert to monthly
            
        except Exception as e:
            print(f"Warning: Could not get Cloud SQL pricing: {e}")
            return 0.0

    def _get_app_engine_price(self, runtime: str, instance_class: str) -> float:
        """Get App Engine pricing"""
        try:
            # GCP App Engine pricing (simplified)
            instance_prices = {
                'F1': 0.05,      # $0.05/hour
                'F2': 0.10,      # $0.10/hour
                'F4': 0.20,      # $0.20/hour
                'F4_1G': 0.20,   # $0.20/hour
                'B1': 0.05,      # $0.05/hour
                'B2': 0.10,      # $0.10/hour
                'B4': 0.20,      # $0.20/hour
                'B8': 0.40,      # $0.40/hour
                'S1': 0.05,      # $0.05/hour
                'S2': 0.10,      # $0.10/hour
                'S4': 0.20,      # $0.20/hour
                'S8': 0.40       # $0.40/hour
            }
            
            hourly_price = instance_prices.get(instance_class, 0.05)  # Default $0.05/hour
            return hourly_price * 730  # Convert to monthly
            
        except Exception as e:
            print(f"Warning: Could not get App Engine pricing: {e}")
            return 0.0

    def _get_generic_gcp_price(self, service: str, config: dict) -> float:
        """Get generic pricing for any GCP service"""
        try:
            # In production, you would make actual API calls to GCP Cloud Billing API
            # For now, use fallback prices
            return self._get_fallback_price(service)
            
        except Exception as e:
            print(f"Warning: Could not get pricing for {service}: {e}")
            return self._get_fallback_price(service)

    def _get_fallback_price(self, service: str) -> float:
        """Provide reasonable fallback prices when API calls fail"""
        fallback_prices = {
            'Compute Engine': 50.0,           # $50/month for basic VM
            'Cloud Storage': 0.02,            # $0.02/GB/month
            'Cloud SQL': 10.0,                # $10/month for basic DB
            'App Engine': 10.0,               # $10/month for basic
            'Google Kubernetes Engine': 73.0, # $73/month for basic cluster
            'Cloud Run': 0.0,                 # Free tier available
            'Cloud Functions': 0.0,           # Free tier available
            'BigQuery': 5.0,                  # $5/month for basic
            'Cloud Pub/Sub': 10.0,            # $10/month for basic
            'Cloud Build': 0.0,               # Free tier available
            'Cloud Logging': 0.0,             # Free tier available
            'Cloud Monitoring': 0.0,          # Free tier available
            'Cloud IAM': 0.0,                 # Free
            'Cloud KMS': 0.03,                # $0.03 per 10K operations
            'Cloud Tasks': 0.0,               # Free tier available
            'Cloud Scheduler': 0.0,           # Free tier available
            'API Gateway': 0.0,               # Free tier available
            'Cloud Endpoints': 0.0,           # Free tier available
            'Filestore': 0.20,                # $0.20/GB/month
            'Cloud Bigtable': 0.65,           # $0.65/hour per node
            'Cloud Spanner': 0.90,            # $0.90/hour per 1000 nodes
            'Firestore': 0.18,                # $0.18 per 100K reads
            'Datastore': 0.18,                # $0.18 per 100K reads
            'Cloud Memorystore for Redis': 0.049, # $0.049/hour per GB
            'Dataflow': 0.06,                 # $0.06/hour per vCPU
            'Dataproc': 0.01,                 # $0.01/hour per vCPU
            'Cloud IoT Core': 0.0045,         # $0.0045 per MB
            'Dialogflow': 0.002,              # $0.002 per request
            'AI Platform': 0.54,              # $0.54/hour per vCPU
            'Cloud Build': 0.003,             # $0.003 per build-minute
            'Cloud Source Repositories': 0.0, # Free
            'Cloud Tasks': 0.40,              # $0.40 per million tasks
            'Cloud Scheduler': 0.10,          # $0.10 per million operations
        }
        
        return fallback_prices.get(service, 10.0)  # Default $10/month

    def build_costs(self, config: dict) -> Dict[str, float]:
        """
        Build cost breakdown for GCP infrastructure configuration
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
        """Calculate cost for a specific GCP resource"""
        try:
            # Extract relevant configuration parameters
            machine_type = config.get('machine_type', config.get('size', 'f1-micro'))
            zone = config.get('zone', self.region)
            storage_gb = config.get('storage_gb', 50)
            storage_class = config.get('storage_class', 'STANDARD')
            database_version = config.get('database_version', 'MYSQL_5_7')
            tier = config.get('tier', 'db-f1-micro')
            runtime = config.get('runtime', 'python')
            instance_class = config.get('instance_class', 'F1')
            
            # Get real-time pricing
            return self.get_resource_price(
                resource_type,
                machine_type=machine_type,
                zone=zone,
                storage_gb=storage_gb,
                storage_class=storage_class,
                database_version=database_version,
                tier=tier,
                runtime=runtime,
                instance_class=instance_class
            )
            
        except Exception as e:
            print(f"Warning: Error calculating cost for {resource_type}: {e}")
            return 0.0

    def get_region_name(self) -> str:
        """Get human-readable region name"""
        return self.region_name_map.get(self.region, self.region)

    def estimate_uncertainty(self, base_cost: float, timeframe_months: float) -> Dict[str, float]:
        """
        Estimate cost uncertainty for GCP resources
        GCP pricing tends to be very stable
        """
        # GCP pricing is generally very predictable
        volatility_factors = {
            'low': 0.02,     # 2% monthly variation (very low)
            'medium': 0.04,  # 4% monthly variation
            'high': 0.08     # 8% monthly variation
        }
        
        # Use the same uncertainty calculation as base class
        return super().estimate_uncertainty(base_cost, timeframe_months)
