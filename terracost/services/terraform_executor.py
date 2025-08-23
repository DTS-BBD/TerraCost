import subprocess
import json
import os
import tempfile
from typing import Dict, Any, Optional
import time

class TerraformExecutor:
    """Handles Terraform plan execution and JSON output parsing"""
    
    def __init__(self, working_dir: str):
        self.working_dir = working_dir
        self.plan_file = None
    
    def run_terraform_plan(self, show_progress: bool = True) -> Dict[str, Any]:
        """
        Execute 'terraform plan' and capture JSON output
        Returns parsed plan data
        """
        # Check if we're in a terraform directory
        main_tf = os.path.join(self.working_dir, "main.tf")
        if not os.path.exists(main_tf):
            raise Exception(f"No main.tf found in {self.working_dir}. Please run this command from a directory containing Terraform files.")
        
        if show_progress:
            print("🔄 Running terraform plan...")
        
        # Create temporary file for plan output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tfplan', delete=False) as f:
            self.plan_file = f.name
        
        try:
            # Run terraform plan with JSON output
            cmd = ["terraform", "plan", "-out", self.plan_file]
            
            if show_progress:
                print("   📁 Working directory:", self.working_dir)
                print("   ⚡ Executing: terraform plan -out", os.path.basename(self.plan_file))
            
            # Change to working directory and run terraform
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"Terraform plan failed: {result.stderr}")
            
            if show_progress:
                print("   ✅ Terraform plan completed successfully")
                print("   📊 Parsing plan output...")
            
            # Parse the plan file
            plan_data = self._parse_plan_file()
            
            if show_progress:
                print("   📈 Extracting resource information...")
            
            # Extract resource information from plan
            resources = self._extract_resources(plan_data)
            
            return {
                'plan_data': plan_data,
                'resources': resources,
                'summary': self._extract_summary(plan_data)
            }
            
        except subprocess.TimeoutExpired:
            raise Exception("Terraform plan timed out after 5 minutes")
        except Exception as e:
            raise Exception(f"Failed to execute terraform plan: {str(e)}")
        finally:
            # Clean up temporary file
            if self.plan_file and os.path.exists(self.plan_file):
                os.unlink(self.plan_file)
    
    def _parse_plan_file(self) -> Dict[str, Any]:
        """Parse the terraform plan file"""
        try:
            # Use terraform show to convert plan to JSON
            cmd = ["terraform", "show", "-json", self.plan_file]
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                raise Exception(f"Failed to parse plan file: {result.stderr}")
            
            return json.loads(result.stdout)
            
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse JSON output: {str(e)}")
    
    def _extract_resources(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract resource information from plan data"""
        resources = {
            'aws': {},
            'azure': {},
            'gcp': {},
            'other': {}
        }
        
        # Extract planned changes
        planned_changes = plan_data.get('resource_changes', [])
        
        for change in planned_changes:
            resource_type = change.get('type', '')
            change_action = change.get('change', {}).get('actions', [])
            
            # Only process resources that are being created or modified
            if 'create' in change_action or 'update' in change_action:
                provider = self._detect_provider(resource_type)
                
                if provider == 'aws':
                    self._extract_aws_resource(resources['aws'], change)
                elif provider == 'azure':
                    self._extract_azure_resource(resources['azure'], change)
                elif provider == 'gcp':
                    self._extract_gcp_resource(resources['gcp'], change)
                else:
                    self._extract_other_resource(resources['other'], change)
        
        return resources
    
    def _detect_provider(self, resource_type: str) -> str:
        """Detect cloud provider from resource type"""
        if resource_type.startswith('aws_'):
            return 'aws'
        elif resource_type.startswith('azurerm_'):
            return 'azure'
        elif resource_type.startswith('google_'):
            return 'gcp'
        else:
            return 'other'
    
    def _extract_aws_resource(self, aws_resources: Dict, change: Dict):
        """Extract AWS resource information"""
        resource_type = change.get('type', '')
        resource_name = change.get('name', '')
        after = change.get('change', {}).get('after', {})
        
        if resource_type == 'aws_instance':
            if 'ec2' not in aws_resources:
                aws_resources['ec2'] = []
            aws_resources['ec2'].append({
                'name': resource_name,
                'instance_type': after.get('instance_type', 't3.micro'),
                'count': 1
            })
        
        elif resource_type == 'aws_db_instance':
            if 'rds' not in aws_resources:
                aws_resources['rds'] = []
            aws_resources['rds'].append({
                'name': resource_name,
                'instance_class': after.get('instance_class', 'db.t3.micro'),
                'engine': after.get('engine', 'mysql')
            })
        
        elif resource_type == 'aws_s3_bucket':
            if 's3' not in aws_resources:
                aws_resources['s3'] = []
            aws_resources['s3'].append({
                'name': resource_name,
                'bucket': after.get('bucket', resource_name)
            })
    
    def _extract_azure_resource(self, azure_resources: Dict, change: Dict):
        """Extract Azure resource information"""
        resource_type = change.get('type', '')
        resource_name = change.get('name', '')
        after = change.get('change', {}).get('after', {})
        
        if resource_type == 'azurerm_virtual_machine':
            if 'vm' not in azure_resources:
                azure_resources['vm'] = []
            azure_resources['vm'].append({
                'name': resource_name,
                'vm_size': after.get('vm_size', 'Standard_B1s')
            })
        
        elif resource_type == 'azurerm_sql_database':
            if 'sql' not in azure_resources:
                azure_resources['sql'] = []
            azure_resources['sql'].append({
                'name': resource_name,
                'tier': after.get('requested_service_objective_name', 'Basic')
            })
    
    def _extract_gcp_resource(self, gcp_resources: Dict, change: Dict):
        """Extract GCP resource information"""
        # Placeholder for GCP resource extraction
        pass
    
    def _extract_other_resource(self, other_resources: Dict, change: Dict):
        """Extract other resource information"""
        resource_type = change.get('type', '')
        if resource_type not in other_resources:
            other_resources[resource_type] = []
        other_resources[resource_type].append(change)
    
    def _extract_summary(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract summary information from plan"""
        return {
            'add': plan_data.get('resource_changes', []).count(lambda x: 'create' in x.get('change', {}).get('actions', [])),
            'change': plan_data.get('resource_changes', []).count(lambda x: 'update' in x.get('change', {}).get('actions', [])),
            'destroy': plan_data.get('resource_changes', []).count(lambda x: 'delete' in x.get('change', {}).get('actions', [])),
            'total': len(plan_data.get('resource_changes', []))
        }
