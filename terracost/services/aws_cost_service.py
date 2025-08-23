import requests
from .base_cost_service import BaseCostService

class AwsCostService(BaseCostService):
    BASE_URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws"

    def __init__(self, region_code="us-east-1"):
        super().__init__(region_code)
        self.region = region_code  # Use the same attribute name as base class
        self.region_code = region_code  # Keep for backward compatibility
        self.region_name_map = {
            "us-east-1": "US East (N. Virginia)",
            "us-west-2": "US West (Oregon)",
            "eu-west-1": "EU (Ireland)",
        }

    def get_resource_price(self, resource_type: str, **kwargs) -> float:
        """Get price for a specific AWS resource type"""
        if resource_type == "ec2":
            return self.get_ec2_instance_price(kwargs.get("instance_type"), kwargs.get("os", "Linux"))
        elif resource_type == "rds":
            return self.get_rds_price(kwargs.get("instance_type"), kwargs.get("engine", "MySQL"))
        elif resource_type == "s3":
            return self.get_s3_bucket_price(kwargs.get("storage_gb", 50))
        else:
            raise ValueError(f"Unsupported resource type: {resource_type}")

    def _load_offer_index(self, service_code: str):
        """
        Load the current price list index for a given service (AmazonEC2, AmazonS3, AmazonRDS, etc.)
        """
        cache_key = f"aws_offer_index_{service_code}_{self.region}"
        cached_data = self._get_cached_price(cache_key)
        if cached_data is not None:
            return cached_data
        
        url = f"{self.BASE_URL}/{service_code}/current/{self.region}/index.json"
        data = self._make_api_request(url)
        self._cache_price(cache_key, data)
        return data

    def get_ec2_instance_price(self, instance_type: str, os="Linux"):
        """
        Get On-Demand monthly EC2 cost for given instance_type (e.g., 't2.large').
        """
        data = self._load_offer_index("AmazonEC2")

        region_name = self.region_name_map.get(self.region, "US East (N. Virginia)")
        for sku, product in data.get("products", {}).items():
            attrs = product.get("attributes", {})
            if (
                attrs.get("instanceType") == instance_type
                and attrs.get("location") == region_name
                and attrs.get("operatingSystem") == os
                and attrs.get("tenancy") == "Shared"
                and attrs.get("preInstalledSw") == "NA"
                and attrs.get("capacitystatus") == "Used"
            ):
                # Get price from terms
                terms = data["terms"]["OnDemand"].get(sku, {})
                for _, term in terms.items():
                    for _, pd in term["priceDimensions"].items():
                        price_per_hour = float(pd["pricePerUnit"]["USD"])
                        return price_per_hour * 720  # approx monthly
        return None

    def get_s3_bucket_price(self, storage_gb=50):
        """
        Get monthly cost for S3 Standard storage for given GB.
        """
        data = self._load_offer_index("AmazonS3")

        region_name = self.region_name_map.get(self.region, "US East (N. Virginia)")
        for sku, product in data.get("products", {}).items():
            attrs = product.get("attributes", {})
            if (
                attrs.get("location") == region_name
                and attrs.get("storageClass") == "Standard"
            ):
                terms = data["terms"]["OnDemand"].get(sku, {})
                for _, term in terms.items():
                    for _, pd in term["priceDimensions"].items():
                        price_per_gb = float(pd["pricePerUnit"]["USD"])
                        return price_per_gb * storage_gb
        return None

    def get_rds_price(self, instance_type: str, engine="MySQL"):
        """
        Get On-Demand monthly RDS cost for given instance type + engine.
        """
        data = self._load_offer_index("AmazonRDS")

        region_name = self.region_name_map.get(self.region, "US East (N. Virginia)")
        for sku, product in data.get("products", {}).items():
            attrs = product.get("attributes", {})
            if (
                attrs.get("instanceType") == instance_type
                and attrs.get("databaseEngine") == engine
                and attrs.get("deploymentOption") == "Single-AZ"
                and attrs.get("location") == region_name
            ):
                terms = data["terms"]["OnDemand"].get(sku, {})
                for _, term in terms.items():
                    for _, pd in term["priceDimensions"].items():
                        price_per_hour = float(pd["pricePerUnit"]["USD"])
                        return price_per_hour * 720
        return None

    def build_costs(self, config: dict):
        """
        Dynamically calculate costs for any AWS resource type by parsing Terraform configuration
        and fetching real-time pricing from AWS Pricing API
        """
        costs = {}
        
        # Process all resource types dynamically
        for resource_type, resource_list in config.items():
            if not isinstance(resource_list, list):
                continue
                
            for resource in resource_list:
                resource_name = resource.get('name', 'unknown')
                resource_config = resource.get('config', {})
                
                # Generate a unique key for this resource
                key = f"{resource_type}.{resource_name}"
                
                # Calculate cost based on resource type and configuration
                cost = self._calculate_resource_cost(resource_type, resource_config)
                costs[key] = cost
                
        return costs
    
    def _calculate_resource_cost(self, resource_type: str, config: dict) -> float:
        """
        Calculate cost for any AWS resource type by analyzing its configuration
        and fetching appropriate pricing from AWS API
        """
        try:
            # Extract the actual AWS service from the resource type (e.g., aws_instance -> ec2)
            aws_service = self._get_aws_service_from_resource_type(resource_type)
            
            if aws_service == "ec2":
                return self._calculate_ec2_cost(config)
            elif aws_service == "rds":
                return self._calculate_rds_cost(config)
            elif aws_service == "s3":
                return self._calculate_s3_cost(config)
            elif aws_service == "lambda":
                return self._calculate_lambda_cost(config)
            elif aws_service == "elasticache":
                return self._calculate_elasticache_cost(config)
            elif aws_service == "redshift":
                return self._calculate_redshift_cost(config)
            elif aws_service == "dynamodb":
                return self._calculate_dynamodb_cost(config)
            elif aws_service == "apigateway":
                return self._calculate_apigateway_cost(config)
            elif aws_service == "cloudfront":
                return self._calculate_cloudfront_cost(config)
            elif aws_service == "elb" or aws_service == "alb" or aws_service == "nlb":
                return self._calculate_loadbalancer_cost(config)
            elif aws_service == "vpc" or aws_service == "subnet" or aws_service == "security_group":
                return 0.0  # VPC components are free
            elif aws_service == "iam" or aws_service == "route_table" or aws_service == "internet_gateway":
                return 0.0  # IAM and basic networking are free
            else:
                # For unknown services, try to get a generic price
                return self._get_generic_aws_price(aws_service, config)
                
        except Exception as e:
            print(f"   ⚠️  Warning: Could not calculate cost for {resource_type}: {e}")
            return 0.0
    
    def _get_aws_service_from_resource_type(self, resource_type: str) -> str:
        """Extract AWS service name from Terraform resource type"""
        # Remove 'aws_' prefix and map to service names
        service_map = {
            'aws_instance': 'ec2',
            'aws_db_instance': 'rds',
            'aws_s3_bucket': 's3',
            'aws_lambda_function': 'lambda',
            'aws_elasticache_cluster': 'elasticache',
            'aws_redshift_cluster': 'redshift',
            'aws_dynamodb_table': 'dynamodb',
            'aws_api_gateway_rest_api': 'apigateway',
            'aws_cloudfront_distribution': 'cloudfront',
            'aws_lb': 'alb',  # Application Load Balancer
            'aws_elb': 'elb',  # Classic Load Balancer
            'aws_lb_listener': 'alb',
            'aws_vpc': 'vpc',
            'aws_subnet': 'subnet',
            'aws_security_group': 'security_group',
            'aws_iam_role': 'iam',
            'aws_route_table': 'route_table',
            'aws_internet_gateway': 'internet_gateway',
            'aws_key_pair': 'ec2',
            'aws_eip': 'ec2',
            'aws_db_subnet_group': 'rds',
            'aws_db_parameter_group': 'rds',
            'aws_iam_role_policy_attachment': 'iam',
            'aws_iam_instance_profile': 'iam',
            'aws_route': 'route_table',
            'aws_route_table_association': 'route_table',
            'aws_budgets_budget': 'budgets'
        }
        
        return service_map.get(resource_type, resource_type.replace('aws_', ''))
    
    def _calculate_ec2_cost(self, config: dict) -> float:
        """Calculate EC2 instance cost based on configuration"""
        instance_type = config.get('instance_type', 't3.micro')
        count = self._parse_count(config.get('count', '1'))
        
        # Get base instance cost
        base_cost = self.get_ec2_instance_price(instance_type) or 0.0
        
        # Calculate total cost for all instances
        return base_cost * count
    
    def _calculate_rds_cost(self, config: dict) -> float:
        """Calculate RDS instance cost based on configuration"""
        instance_class = config.get('instance_class', 'db.t3.micro')
        engine = config.get('engine', 'postgres')
        allocated_storage = self._parse_storage(config.get('allocated_storage', '20'))
        count = self._parse_count(config.get('count', '1'))
        
        # Get base instance cost
        base_cost = self.get_rds_price(instance_class, engine) or 0.0
        
        # Add storage cost (simplified - in reality this varies by engine and storage type)
        storage_cost = self._calculate_rds_storage_cost(allocated_storage, engine)
        
        return (base_cost + storage_cost) * count
    
    def _calculate_s3_cost(self, config: dict) -> float:
        """Calculate S3 cost based on configuration"""
        # Default storage estimate - in reality this would come from actual usage
        storage_gb = 50  # Default estimate
        
        # Try to extract storage information from tags or other config
        if 'tags' in config:
            # Look for storage hints in tags
            pass
        
        return self.get_s3_bucket_price(storage_gb) or 0.0
    
    def _calculate_lambda_cost(self, config: dict) -> float:
        """Calculate Lambda function cost based on configuration"""
        # Lambda pricing: $0.20 per 1M requests + $0.0000166667 per GB-second
        # Default estimates for monthly usage
        monthly_requests = 1000000  # 1M requests per month
        memory_mb = int(config.get('memory_size', '128'))
        execution_time_seconds = 1  # Default 1 second execution
        
        request_cost = (monthly_requests / 1000000) * 0.20
        compute_cost = (monthly_requests * memory_mb * execution_time_seconds / 1024) * 0.0000166667 * 720  # Convert to monthly
        
        return request_cost + compute_cost
    
    def _calculate_elasticache_cost(self, config: dict) -> float:
        """Calculate ElastiCache cost based on configuration"""
        node_type = config.get('node_type', 'cache.t3.micro')
        num_cache_nodes = self._parse_count(config.get('num_cache_nodes', '1'))
        
        # ElastiCache uses similar pricing to EC2 for compute
        base_cost = self.get_ec2_instance_price(node_type) or 0.0
        
        return base_cost * num_cache_nodes
    
    def _calculate_redshift_cost(self, config: dict) -> float:
        """Calculate Redshift cost based on configuration"""
        node_type = config.get('node_type', 'dc2.large')
        number_of_nodes = self._parse_count(config.get('number_of_nodes', '1'))
        
        # Redshift pricing is similar to RDS but different service code
        # For now, use a simplified calculation
        return 0.0  # TODO: Implement Redshift pricing
    
    def _calculate_dynamodb_cost(self, config: dict) -> float:
        """Calculate DynamoDB cost based on configuration"""
        # DynamoDB pricing: $1.25 per million write request units, $0.25 per million read request units
        # Plus $0.25 per GB-month for storage
        
        # Default estimates
        monthly_writes = 1000000  # 1M write requests per month
        monthly_reads = 2000000   # 2M read requests per month
        storage_gb = 10           # 10 GB storage
        
        write_cost = (monthly_writes / 1000000) * 1.25
        read_cost = (monthly_reads / 1000000) * 0.25
        storage_cost = storage_gb * 0.25
        
        return write_cost + read_cost + storage_cost
    
    def _calculate_apigateway_cost(self, config: dict) -> float:
        """Calculate API Gateway cost based on configuration"""
        # API Gateway pricing: $3.50 per million API calls + data transfer
        
        # Default estimate
        monthly_requests = 1000000  # 1M API calls per month
        
        return (monthly_requests / 1000000) * 3.50
    
    def _calculate_cloudfront_cost(self, config: dict) -> float:
        """Calculate CloudFront cost based on configuration"""
        # CloudFront pricing: $0.085 per GB for first 10TB of data transfer out
        
        # Default estimate
        monthly_data_transfer_gb = 100  # 100 GB per month
        
        return monthly_data_transfer_gb * 0.085
    
    def _calculate_loadbalancer_cost(self, config: dict) -> float:
        """Calculate Load Balancer cost based on configuration"""
        # ALB/NLB: $16.20 per month + $0.006 per LCU-hour
        # Classic LB: $18.00 per month + $0.008 per GB
        
        # Default estimate
        return 16.20  # Base ALB cost per month
    
    def _get_generic_aws_price(self, service: str, config: dict) -> float:
        """Try to get pricing for any AWS service using the pricing API"""
        try:
            # Map service names to AWS service codes
            service_codes = {
                'ec2': 'AmazonEC2',
                'rds': 'AmazonRDS',
                's3': 'AmazonS3',
                'lambda': 'AWSLambda',
                'elasticache': 'AmazonElastiCache',
                'redshift': 'AmazonRedshift',
                'dynamodb': 'AmazonDynamoDB',
                'apigateway': 'AmazonAPIGateway',
                'cloudfront': 'AmazonCloudFront',
                'alb': 'AWSElasticLoadBalancing',
                'elb': 'AWSElasticLoadBalancing',
                'nlb': 'AWSElasticLoadBalancing'
            }
            
            service_code = service_codes.get(service)
            if not service_code:
                return 0.0
            
            # Try to get pricing data for this service
            data = self._load_offer_index(service_code)
            
            # For now, return 0.0 as we need more sophisticated parsing
            # In the future, this could analyze the config and find matching SKUs
            return 0.0
            
        except Exception as e:
            print(f"   ⚠️  Warning: Could not get generic pricing for {service}: {e}")
            return 0.0
    
    def _parse_count(self, count_value: str) -> int:
        """Parse count value from Terraform config (handles variables, expressions, etc.)"""
        if isinstance(count_value, int):
            return count_value
        if isinstance(count_value, str):
            # Handle Terraform expressions like "var.instance_count"
            if count_value.startswith('var.'):
                return 1  # Default to 1 for variables
            try:
                return int(count_value)
            except ValueError:
                return 1  # Default to 1 if we can't parse
        return 1
    
    def _parse_storage(self, storage_value: str) -> int:
        """Parse storage value from Terraform config"""
        if isinstance(storage_value, int):
            return storage_value
        if isinstance(storage_value, str):
            try:
                return int(storage_value)
            except ValueError:
                return 20  # Default to 20 GB
        return 20
    
    def _calculate_rds_storage_cost(self, storage_gb: int, engine: str) -> float:
        """Calculate RDS storage cost based on engine and storage size"""
        # Simplified storage pricing - in reality this varies by engine and storage type
        # General purpose SSD: $0.115 per GB-month
        return storage_gb * 0.115