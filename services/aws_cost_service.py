import requests

class AwsCostService:
    BASE_URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws"

    def __init__(self, region_code="us-east-1"):
        self.region_code = region_code
        self.region_name_map = {
            "us-east-1": "US East (N. Virginia)",
            "us-west-2": "US West (Oregon)",
            "eu-west-1": "EU (Ireland)",
        }

    def _load_offer_index(self, service_code: str):
        """
        Load the current price list index for a given service (AmazonEC2, AmazonS3, AmazonRDS, etc.)
        """
        url = f"{self.BASE_URL}/{service_code}/current/{self.region_code}/index.json"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_ec2_instance_price(self, instance_type: str, os="Linux"):
        """
        Get On-Demand monthly EC2 cost for given instance_type (e.g., 't2.large').
        """
        data = self._load_offer_index("AmazonEC2")

        region_name = self.region_name_map.get(self.region_code, "US East (N. Virginia)")
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

        region_name = self.region_name_map.get(self.region_code, "US East (N. Virginia)")
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

        region_name = self.region_name_map.get(self.region_code, "US East (N. Virginia)")
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
        costs = {}

        if "ec2" in config:
            for idx, ec2 in enumerate(config["ec2"], start=1):
                instance_type = ec2.get("instance_type")
                if instance_type:
                    key = f"aws_instance.web_server_{idx}"
                    costs[key] = self.get_ec2_instance_price(instance_type) or 0

        if "rds" in config:
            for idx, rds in enumerate(config["rds"], start=1):
                instance_class = rds.get("instance_class")
                if instance_class:
                    key = f"aws_rds_instance.db_{idx}"
                    costs[key] = self.get_rds_price(instance_class) or 0

        if "s3" in config:
            for idx, s3 in enumerate(config["s3"], start=1):
                # You’ll need to decide how to estimate storage — hardcode for now (e.g. 50GB)
                key = f"aws_s3_bucket.bucket_{idx}"
                costs[key] = self.get_s3_bucket_price(storage_gb=50) or 0

        return costs