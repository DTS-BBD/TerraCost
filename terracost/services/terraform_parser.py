import os
import json
import hcl2

def parse_tf_file(tf_file):
    """Parse a .tf file into a Python dict using hcl2."""
    with open(tf_file, "r") as f:
        return hcl2.load(f)
    
def detect_provider(folder_path):
    """Detect if infrastructure uses AWS or Azure"""
    main_tf = os.path.join(folder_path, "main.tf")
    if os.path.exists(main_tf):
        with open(main_tf, 'r') as f:
            content = f.read()
            if 'provider "azurerm"' in content:
                return "azure"
    return "aws"

def parse_infrastructure(folder_path):
    result = {"ec2": [], "rds": [], "s3": []}

    root_main = os.path.join(folder_path, "main.tf")
    if not os.path.exists(root_main):
        raise FileNotFoundError(f"No main.tf found in {folder_path}")
    root_config = parse_tf_file(root_main)

    if "module" in root_config:
        for module in root_config["module"]:
            for module_name, module_def in module.items():
                if module_name in ["ec2", "rds", "s3"]:
                    module_path = os.path.join(folder_path, module_def["source"].replace("./", ""))
                    module_main = os.path.join(module_path, "main.tf")

                    if os.path.exists(module_main):
                        module_config = parse_tf_file(module_main)
                        
                        if module_name == "ec2":
                            for res in module_config.get("resource", []):
                                if "aws_instance" in res:
                                    instance = list(res["aws_instance"].values())[0]
                                    result["ec2"].append({
                                        "instance_type": instance.get("instance_type", "t3.micro"),
                                        "count": instance.get("count", 1)
                                    })

                        elif module_name == "rds":
                            for res in module_config.get("resource", []):
                                if "aws_db_instance" in res:
                                    db = list(res["aws_db_instance"].values())[0]
                                    result["rds"].append({
                                        "instance_class": db.get("instance_class", "db.t3.micro"),
                                        "engine": db.get("engine", "mysql")
                                    })

                        elif module_name == "s3":
                            for res in module_config.get("resource", []):
                                if "aws_s3_bucket" in res:
                                    bucket = list(res["aws_s3_bucket"].values())[0]
                                    result["s3"].append({
                                        "bucket": bucket.get("bucket", "default-bucket")
                                    })

    return result

def parse_azure_infrastructure(folder_path):
    result = {"vm": [], "sql": [], "storage": []}
    
    root_main = os.path.join(folder_path, "main.tf")
    if not os.path.exists(root_main):
        raise FileNotFoundError(f"No main.tf found in {folder_path}")
    
    root_config = parse_tf_file(root_main)
    
    for res in root_config.get("resource", []):
        if "azurerm_virtual_machine" in res:
            vm = list(res["azurerm_virtual_machine"].values())[0]
            vm_size = vm.get("vm_size", "Standard_B1s")
            # Handle Terraform variables by using default values
            if "${var." in str(vm_size):
                vm_size = "Standard_B1s"  # default
            result["vm"].append({
                "vm_size": vm_size
            })
        
        if "azurerm_sql_database" in res:
            db = list(res["azurerm_sql_database"].values())[0]
            tier = db.get("requested_service_objective_name", "Basic")
            # Handle Terraform variables by using default values
            if "${var." in str(tier):
                tier = "Basic"  # default
            result["sql"].append({
                "tier": tier
            })
    
    return result