import os
import re
import json
from typing import Dict, Any, List, Optional
from pathlib import Path

class TerraformFileParser:
    """Parses Terraform files directly to extract resource information"""
    
    def __init__(self, working_dir: str):
        self.working_dir = working_dir
        self.parsed_files = {}
        self.resources = {
            'aws': {},
            'azure': {},
            'gcp': {},
            'other': {}
        }
        self.modules = {}
        self.variables = {}
        self.data_sources = {}
    
    def parse_terraform_files(self, show_progress: bool = True) -> Dict[str, Any]:
        """
        Parse all Terraform files in the working directory and subdirectories
        Returns parsed resource information
        """
        if show_progress:
            print("📁 Scanning for Terraform files...")
        
        # Find all .tf files
        tf_files = self._find_terraform_files()
        
        if not tf_files:
            raise Exception(f"No .tf files found in {self.working_dir}")
        
        if show_progress:
            print(f"   📋 Found {len(tf_files)} Terraform files")
        
        # Parse each file
        for tf_file in tf_files:
            if show_progress:
                print(f"   📖 Parsing {os.path.relpath(tf_file, self.working_dir)}")
            self._parse_single_file(tf_file, show_progress)
        
        # Process modules recursively
        if show_progress:
            print("   🔍 Processing modules...")
            if self.modules:
                print(f"   📦 Found {len(self.modules)} modules to process")
            else:
                print("   ℹ️  No modules found")
        self._process_modules()
        
        # Extract resources from parsed data
        if show_progress:
            print("   📊 Extracting resource information...")
        self._extract_resources()
        
        if show_progress:
            print(f"   📋 Final resource counts:")
            for provider, resources in self.resources.items():
                if provider != 'other':
                    total = sum(len(resource_list) for resource_list in resources.values())
                    print(f"      {provider}: {total} resources")
        
        return {
            'resources': self.resources,
            'modules': self.modules,
            'variables': self.variables,
            'data_sources': self.data_sources,
            'summary': self._generate_summary()
        }
    
    def _find_terraform_files(self) -> List[str]:
        """Find all .tf files in the working directory and subdirectories"""
        tf_files = []
        
        for root, dirs, files in os.walk(self.working_dir):
            # Skip .terraform directory
            if '.terraform' in dirs:
                dirs.remove('.terraform')
            
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                if file.endswith('.tf'):
                    tf_files.append(os.path.join(root, file))
        
        return sorted(tf_files)
    
    def _parse_single_file(self, file_path: str, show_progress: bool = True):
        """Parse a single Terraform file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Store the parsed content
            relative_path = os.path.relpath(file_path, self.working_dir)
            self.parsed_files[relative_path] = content
            
            # Extract different components
            self._extract_resources_from_content(content, relative_path, show_progress)
            self._extract_modules_from_content(content, relative_path, show_progress)
            self._extract_variables_from_content(content, relative_path, show_progress)
            self._extract_data_sources_from_content(content, relative_path, show_progress)
            
            # Debug: Show what was extracted from this file
            if show_progress and relative_path == 'main.tf':
                print(f"      📋 After parsing {relative_path}:")
                print(f"         Resources: {len(self.resources['other'])} types")
                print(f"         Modules: {len(self.modules)}")
                print(f"         Variables: {len(self.variables)}")
            
        except Exception as e:
            print(f"   ⚠️  Warning: Could not parse {file_path}: {e}")
    
    def _extract_resources_from_content(self, content: str, file_path: str, show_progress: bool = True):
        """Extract resource blocks from Terraform content"""
        try:
            # Match resource blocks: resource "type" "name" { ... }
            # Simplified pattern to avoid complex nested brace matching
            resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{'
            
            for match in re.finditer(resource_pattern, content, re.DOTALL):
                try:
                    resource_type = match.group(1)
                    resource_name = match.group(2)
                    
                    # Find the matching closing brace by counting braces
                    start_pos = match.end()
                    brace_count = 1
                    pos = start_pos
                    
                    while pos < len(content) and brace_count > 0:
                        if content[pos] == '{':
                            brace_count += 1
                        elif content[pos] == '}':
                            brace_count -= 1
                        pos += 1
                    
                    if brace_count == 0:
                        resource_config = content[start_pos:pos-1]
                        # Parse the resource configuration
                        parsed_config = self._parse_resource_config(resource_config)
                        
                        # Store the resource
                        if resource_type not in self.resources['other']:
                            self.resources['other'][resource_type] = []
                        
                        self.resources['other'][resource_type].append({
                            'name': resource_name,
                            'config': parsed_config,
                            'file': file_path
                        })
                        
                        if show_progress and file_path == 'main.tf':
                            print(f"         ✅ Found resource: {resource_type} '{resource_name}'")
                    else:
                        if show_progress and file_path == 'main.tf':
                            print(f"         ⚠️  Brace count mismatch for {resource_type} '{resource_name}': {brace_count}")
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not parse resource in {file_path}: {e}")
                    continue
        except Exception as e:
            print(f"   ⚠️  Warning: Error extracting resources from {file_path}: {e}")
    
    def _extract_modules_from_content(self, content: str, file_path: str, show_progress: bool = True):
        """Extract module blocks from Terraform content"""
        try:
            # Match module blocks: module "name" { ... }
            # Simplified pattern to avoid complex nested brace matching
            module_pattern = r'module\s+"([^"]+)"\s*\{'
            
            for match in re.finditer(module_pattern, content, re.DOTALL):
                try:
                    module_name = match.group(1)
                    
                    # Find the matching closing brace by counting braces
                    start_pos = match.end()
                    brace_count = 1
                    pos = start_pos
                    
                    while pos < len(content) and brace_count > 0:
                        if content[pos] == '{':
                            brace_count += 1
                        elif content[pos] == '}':
                            brace_count -= 1
                        pos += 1
                    
                    if brace_count == 0:
                        module_config = content[start_pos:pos-1]
                        # Parse the module configuration
                        parsed_config = self._parse_resource_config(module_config)
                        
                        # Look for source attribute
                        source = parsed_config.get('source', '')
                        
                        self.modules[module_name] = {
                            'source': source,
                            'config': parsed_config,
                            'file': file_path
                        }
                        
                        if show_progress and file_path == 'main.tf':
                            print(f"         📦 Found module: {module_name} -> {source}")
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not parse module in {file_path}: {e}")
                    continue
        except Exception as e:
            print(f"   ⚠️  Warning: Error extracting modules from {file_path}: {e}")
    
    def _extract_variables_from_content(self, content: str, file_path: str, show_progress: bool = True):
        """Extract variable blocks from Terraform content"""
        try:
            # Match variable blocks: variable "name" { ... }
            # Simplified pattern to avoid complex nested brace matching
            variable_pattern = r'variable\s+"([^"]+)"\s*\{'
            
            for match in re.finditer(variable_pattern, content, re.DOTALL):
                try:
                    variable_name = match.group(1)
                    
                    # Find the matching closing brace by counting braces
                    start_pos = match.end()
                    brace_count = 1
                    pos = start_pos
                    
                    while pos < len(content) and brace_count > 0:
                        if content[pos] == '{':
                            brace_count += 1
                        elif content[pos] == '}':
                            brace_count -= 1
                        pos += 1
                    
                    if brace_count == 0:
                        variable_config = content[start_pos:pos-1]
                        # Parse the variable configuration
                        parsed_config = self._parse_resource_config(variable_config)
                        
                        self.variables[variable_name] = {
                            'config': parsed_config,
                            'file': file_path
                        }
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not parse variable in {file_path}: {e}")
                    continue
        except Exception as e:
            print(f"   ⚠️  Warning: Error extracting variables from {file_path}: {e}")
    
    def _extract_data_sources_from_content(self, content: str, file_path: str, show_progress: bool = True):
        """Extract data source blocks from Terraform content"""
        try:
            # Match data blocks: data "type" "name" { ... }
            # Simplified pattern to avoid complex nested brace matching
            data_pattern = r'data\s+"([^"]+)"\s+"([^"]+)"\s*\{'
            
            for match in re.finditer(data_pattern, content, re.DOTALL):
                try:
                    data_type = match.group(1)
                    data_name = match.group(2)
                    
                    # Find the matching closing brace by counting braces
                    start_pos = match.end()
                    brace_count = 1
                    pos = start_pos
                    
                    while pos < len(content) and brace_count > 0:
                        if content[pos] == '{':
                            brace_count += 1
                        elif content[pos] == '}':
                            brace_count -= 1
                        pos += 1
                    
                    if brace_count == 0:
                        data_config = content[start_pos:pos-1]
                        # Parse the data source configuration
                        parsed_config = self._parse_resource_config(data_config)
                        
                        if data_type not in self.data_sources:
                            self.data_sources[data_type] = []
                        
                        self.data_sources[data_type].append({
                            'name': data_name,
                            'config': parsed_config,
                            'file': file_path
                        })
                except Exception as e:
                    print(f"   ⚠️  Warning: Could not parse data source in {file_path}: {e}")
                    continue
        except Exception as e:
            print(f"   ⚠️  Warning: Error extracting data sources from {file_path}: {e}")
    
    def _parse_resource_config(self, config_text: str) -> Dict[str, Any]:
        """Parse resource configuration text into a structured format"""
        config = {}
        
        # Extract key-value pairs
        # Handle both simple assignments and nested blocks
        lines = config_text.split('\n')
        current_block = None
        current_block_content = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Check for nested block start
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*\{', line):
                if current_block:
                    # Process previous block
                    config[current_block] = self._parse_resource_config('\n'.join(current_block_content))
                
                current_block = line.split('{')[0].strip()
                current_block_content = []
                continue
            
            # Check for nested block end
            if line == '}':
                if current_block:
                    # Process current block
                    config[current_block] = self._parse_resource_config('\n'.join(current_block_content))
                    current_block = None
                    current_block_content = []
                continue
            
            # Add to current block if we're in one
            if current_block:
                current_block_content.append(line)
            else:
                # Simple key-value assignment
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    config[key] = value
        
        return config
    
    def _process_modules(self):
        """Process module sources and extract resources from them"""
        if not self.modules:
            return
            
        for module_name, module_info in self.modules.items():
            source = module_info['source']
            
            # Handle local module sources
            if source.startswith('./') or source.startswith('../'):
                module_path = os.path.join(self.working_dir, source)
                if os.path.exists(module_path):
                    # Recursively parse the module directory
                    module_parser = TerraformFileParser(module_path)
                    try:
                        module_result = module_parser.parse_terraform_files(show_progress=False)
                        
                        # Merge resources from the module
                        print(f"   🔍 Processing module {module_name} from {source}")
                        
                        # Count total resources found in this module
                        total_module_resources = 0
                        for provider, resources in module_result['resources'].items():
                            for resource_type, resource_list in resources.items():
                                total_module_resources += len(resource_list)
                        
                        print(f"      Found {total_module_resources} resources in {module_name}")
                        
                        for provider, resources in module_result['resources'].items():
                            if provider not in self.resources:
                                self.resources[provider] = {}
                            
                            for resource_type, resource_list in resources.items():
                                if resource_type not in self.resources[provider]:
                                    self.resources[provider][resource_type] = []
                                
                                # Create a copy of the resource list to avoid modification during iteration
                                resources_to_add = []
                                for resource in resource_list:
                                    resource_copy = resource.copy()
                                    resource_copy['name'] = f"{module_name}.{resource['name']}"
                                    resource_copy['module'] = module_name
                                    resources_to_add.append(resource_copy)
                                
                                self.resources[provider][resource_type].extend(resources_to_add)
                                print(f"      Added {len(resources_to_add)} {resource_type} resources from {module_name}")
                    
                    except Exception as e:
                        print(f"   ⚠️  Warning: Could not parse module {source}: {e}")
                else:
                    print(f"   ⚠️  Warning: Module path not found: {module_path}")
            else:
                print(f"   ℹ️  Skipping remote module: {source}")
    
    def _extract_resources(self):
        """Extract and categorize resources by provider"""
        # Create a copy of the keys to avoid "dictionary changed size during iteration"
        other_resource_types = list(self.resources['other'].keys())
        
        for resource_type in other_resource_types:
            resources = self.resources['other'][resource_type]
            provider = self._detect_provider(resource_type)
            
            if provider == 'aws':
                if 'aws' not in self.resources:
                    self.resources['aws'] = {}
                self.resources['aws'][resource_type] = resources
            elif provider == 'azure':
                if 'azure' not in self.resources:
                    self.resources['azure'] = {}
                self.resources['azure'][resource_type] = resources
            elif provider == 'gcp':
                if 'gcp' not in self.resources:
                    self.resources['gcp'] = {}
                self.resources['gcp'][resource_type] = resources
            
            # Remove from 'other' since we've categorized it
            del self.resources['other'][resource_type]
    
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
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate a summary of all resources"""
        total_resources = 0
        provider_counts = {}
        
        for provider, resources in self.resources.items():
            if provider == 'other':
                continue
            
            provider_total = 0
            for resource_type, resource_list in resources.items():
                provider_total += len(resource_list)
            
            provider_counts[provider] = provider_total
            total_resources += provider_total
        
        return {
            'total_resources': total_resources,
            'provider_counts': provider_counts,
            'modules_count': len(self.modules),
            'variables_count': len(self.variables),
            'data_sources_count': sum(len(resources) for resources in self.data_sources.values())
        }
