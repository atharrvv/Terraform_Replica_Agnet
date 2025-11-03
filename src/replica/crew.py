import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai.tools import tool
import subprocess
import json

# Custom tool for Azure resource discovery
@tool("Azure Resource Scanner")
def azure_resource_scanner(resource_group: str) -> str:
    """
    Scans Azure resources in a resource group and identifies dependencies.
    Uses Azure CLI commands to gather resource information.
    """

    
    try:
        # Get all resources in the resource group
        cmd = f"az resource list --resource-group {resource_group} --output json"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode != 0:
            return f"Error: {result.stderr}"
        
        resources = json.loads(result.stdout)
        
        resource_details = []
        for resource in resources:
            resource_id = resource['id']
            resource_type = resource['type']
            resource_name = resource['name']
            
            # Get detailed information for each resource
            detail_cmd = f"az resource show --ids {resource_id} --output json"
            detail_result = subprocess.run(detail_cmd, shell=True, capture_output=True, text=True)
            
            if detail_result.returncode == 0:
                detail = json.loads(detail_result.stdout)
                resource_details.append({
                    'name': resource_name,
                    'type': resource_type,
                    'id': resource_id,
                    'location': resource.get('location', ''),
                    'properties': detail.get('properties', {}),
                    'sku': detail.get('sku', {}),
                    'tags': detail.get('tags', {}),
                    'dependencies': detail.get('dependsOn', [])
                })
        
        return json.dumps(resource_details, indent=2)
    
    except Exception as e:
        return f"Error scanning resources: {str(e)}"


@tool("Azure Network Analyzer")
def azure_network_analyzer(resource_group: str) -> str:
    """
    Analyzes network connections and dependencies between Azure resources.
    Identifies VNets, subnets, NSGs, and their associations.
    """
    import subprocess
    import json
    
    try:
        connections = {}
        
        # Get VNets with subnets
        vnet_cmd = f"az network vnet list --resource-group {resource_group} --output json"
        vnet_result = subprocess.run(vnet_cmd, shell=True, capture_output=True, text=True)
        
        if vnet_result.returncode == 0:
            vnets = json.loads(vnet_result.stdout)
            for vnet in vnets:
                # Get subnet details for each vnet
                subnet_cmd = f"az network vnet subnet list --resource-group {resource_group} --vnet-name {vnet['name']} --output json"
                subnet_result = subprocess.run(subnet_cmd, shell=True, capture_output=True, text=True)
                if subnet_result.returncode == 0:
                    vnet['subnets_detailed'] = json.loads(subnet_result.stdout)
            connections['vnets'] = vnets
        
        # Get NSGs with rules
        nsg_cmd = f"az network nsg list --resource-group {resource_group} --output json"
        nsg_result = subprocess.run(nsg_cmd, shell=True, capture_output=True, text=True)
        
        if nsg_result.returncode == 0:
            nsgs = json.loads(nsg_result.stdout)
            for nsg in nsgs:
                # Get NSG rules
                rule_cmd = f"az network nsg rule list --resource-group {resource_group} --nsg-name {nsg['name']} --output json"
                rule_result = subprocess.run(rule_cmd, shell=True, capture_output=True, text=True)
                if rule_result.returncode == 0:
                    nsg['rules_detailed'] = json.loads(rule_result.stdout)
            connections['nsgs'] = nsgs
        
        # Get Public IPs
        pip_cmd = f"az network public-ip list --resource-group {resource_group} --output json"
        pip_result = subprocess.run(pip_cmd, shell=True, capture_output=True, text=True)
        
        if pip_result.returncode == 0:
            pips = json.loads(pip_result.stdout)
            connections['public_ips'] = pips
        
        # Get NICs (Network Interface Cards)
        nic_cmd = f"az network nic list --resource-group {resource_group} --output json"
        nic_result = subprocess.run(nic_cmd, shell=True, capture_output=True, text=True)
        
        if nic_result.returncode == 0:
            nics = json.loads(nic_result.stdout)
            connections['network_interfaces'] = nics
        
        # Get Load Balancers
        lb_cmd = f"az network lb list --resource-group {resource_group} --output json"
        lb_result = subprocess.run(lb_cmd, shell=True, capture_output=True, text=True)
        
        if lb_result.returncode == 0:
            lbs = json.loads(lb_result.stdout)
            connections['load_balancers'] = lbs
        
        # Get Application Gateways
        appgw_cmd = f"az network application-gateway list --resource-group {resource_group} --output json"
        appgw_result = subprocess.run(appgw_cmd, shell=True, capture_output=True, text=True)
        
        if appgw_result.returncode == 0:
            appgws = json.loads(appgw_result.stdout)
            connections['application_gateways'] = appgws
        
        return json.dumps(connections, indent=2)
    
    except Exception as e:
        return f"Error analyzing network: {str(e)}"


@tool("Azure Service Dependencies Mapper")
def azure_dependencies_mapper(resource_group: str) -> str:
    """
    Maps dependencies between Azure services like databases, storage accounts,
    app services, and their connections.
    """
    import subprocess
    import json
    
    try:
        dependencies = {}
        
        # Get Storage Accounts
        storage_cmd = f"az storage account list --resource-group {resource_group} --output json"
        storage_result = subprocess.run(storage_cmd, shell=True, capture_output=True, text=True)
        
        if storage_result.returncode == 0:
            storage_accounts = json.loads(storage_result.stdout)
            for sa in storage_accounts:
                # Get network rules
                network_cmd = f"az storage account show --name {sa['name']} --resource-group {resource_group} --query networkRuleSet --output json"
                network_result = subprocess.run(network_cmd, shell=True, capture_output=True, text=True)
                if network_result.returncode == 0:
                    sa['network_rules'] = json.loads(network_result.stdout)
            dependencies['storage_accounts'] = storage_accounts
        
        # Get SQL Servers and Databases
        sql_cmd = f"az sql server list --resource-group {resource_group} --output json"
        sql_result = subprocess.run(sql_cmd, shell=True, capture_output=True, text=True)
        
        if sql_result.returncode == 0:
            sql_servers = json.loads(sql_result.stdout)
            for server in sql_servers:
                # Get databases
                db_cmd = f"az sql db list --resource-group {resource_group} --server {server['name']} --output json"
                db_result = subprocess.run(db_cmd, shell=True, capture_output=True, text=True)
                if db_result.returncode == 0:
                    server['databases'] = json.loads(db_result.stdout)
                
                # Get firewall rules
                fw_cmd = f"az sql server firewall-rule list --resource-group {resource_group} --server {server['name']} --output json"
                fw_result = subprocess.run(fw_cmd, shell=True, capture_output=True, text=True)
                if fw_result.returncode == 0:
                    server['firewall_rules'] = json.loads(fw_result.stdout)
            dependencies['sql_servers'] = sql_servers
        
        # Get App Services
        webapp_cmd = f"az webapp list --resource-group {resource_group} --output json"
        webapp_result = subprocess.run(webapp_cmd, shell=True, capture_output=True, text=True)
        
        if webapp_result.returncode == 0:
            webapps = json.loads(webapp_result.stdout)
            for webapp in webapps:
                # Get app settings
                settings_cmd = f"az webapp config appsettings list --resource-group {resource_group} --name {webapp['name']} --output json"
                settings_result = subprocess.run(settings_cmd, shell=True, capture_output=True, text=True)
                if settings_result.returncode == 0:
                    webapp['app_settings'] = json.loads(settings_result.stdout)
                
                # Get connection strings
                conn_cmd = f"az webapp config connection-string list --resource-group {resource_group} --name {webapp['name']} --output json"
                conn_result = subprocess.run(conn_cmd, shell=True, capture_output=True, text=True)
                if conn_result.returncode == 0:
                    webapp['connection_strings'] = json.loads(conn_result.stdout)
            dependencies['webapps'] = webapps
        
        # Get App Service Plans
        plan_cmd = f"az appservice plan list --resource-group {resource_group} --output json"
        plan_result = subprocess.run(plan_cmd, shell=True, capture_output=True, text=True)
        
        if plan_result.returncode == 0:
            plans = json.loads(plan_result.stdout)
            dependencies['app_service_plans'] = plans
        
        # Get CosmosDB
        cosmos_cmd = f"az cosmosdb list --resource-group {resource_group} --output json"
        cosmos_result = subprocess.run(cosmos_cmd, shell=True, capture_output=True, text=True)
        
        if cosmos_result.returncode == 0:
            cosmos_accounts = json.loads(cosmos_result.stdout)
            dependencies['cosmos_accounts'] = cosmos_accounts
        
        # Get Key Vaults
        kv_cmd = f"az keyvault list --resource-group {resource_group} --output json"
        kv_result = subprocess.run(kv_cmd, shell=True, capture_output=True, text=True)
        
        if kv_result.returncode == 0:
            keyvaults = json.loads(kv_result.stdout)
            for kv in keyvaults:
                # Get access policies
                policy_cmd = f"az keyvault show --name {kv['name']} --resource-group {resource_group} --query properties.accessPolicies --output json"
                policy_result = subprocess.run(policy_cmd, shell=True, capture_output=True, text=True)
                if policy_result.returncode == 0:
                    kv['access_policies'] = json.loads(policy_result.stdout)
            dependencies['keyvaults'] = keyvaults
        
        # Get Virtual Machines
        vm_cmd = f"az vm list --resource-group {resource_group} --output json"
        vm_result = subprocess.run(vm_cmd, shell=True, capture_output=True, text=True)
        
        if vm_result.returncode == 0:
            vms = json.loads(vm_result.stdout)
            for vm in vms:
                # Get VM details including NICs
                vm_detail_cmd = f"az vm show --resource-group {resource_group} --name {vm['name']} --output json"
                vm_detail_result = subprocess.run(vm_detail_cmd, shell=True, capture_output=True, text=True)
                if vm_detail_result.returncode == 0:
                    vm['details'] = json.loads(vm_detail_result.stdout)
            dependencies['virtual_machines'] = vms
        
        # Get Function Apps
        func_cmd = f"az functionapp list --resource-group {resource_group} --output json"
        func_result = subprocess.run(func_cmd, shell=True, capture_output=True, text=True)
        
        if func_result.returncode == 0:
            functions = json.loads(func_result.stdout)
            for func in functions:
                # Get app settings
                settings_cmd = f"az functionapp config appsettings list --resource-group {resource_group} --name {func['name']} --output json"
                settings_result = subprocess.run(settings_cmd, shell=True, capture_output=True, text=True)
                if settings_result.returncode == 0:
                    func['app_settings'] = json.loads(settings_result.stdout)
            dependencies['function_apps'] = functions
        
        return json.dumps(dependencies, indent=2)
    
    except Exception as e:
        return f"Error mapping dependencies: {str(e)}"


@tool("Terraform File Writer")
def terraform_file_writer(filename: str, content: str) -> str:
    """
    Writes Terraform configuration content to a .tf file in the terraform/ directory.
    Creates the directory if it doesn't exist.
    """
    import os
    
    try:
        # Create terraform directory if it doesn't exist
        terraform_dir = "terraform"
        if not os.path.exists(terraform_dir):
            os.makedirs(terraform_dir)
        
        # Write the file
        filepath = os.path.join(terraform_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        
        return f"Successfully wrote {len(content)} characters to {filepath}"
    
    except Exception as e:
        return f"Error writing file {filename}: {str(e)}"


@tool("Terraform Validator")
def terraform_validator(terraform_dir: str = "terraform") -> str:
    """
    Validates Terraform configuration files for syntax, deprecated resources,
    version compatibility, and Azure-specific requirements.
    Returns a detailed validation report with executability score.
    """
    import subprocess
    import json
    import os
    import re
    
    try:
        validation_report = {
            "file_checks": {},
            "syntax_errors": [],
            "deprecated_resources": [],
            "config_issues": [],
            "version_check": {},
            "azure_validation": {},
            "scores": {},
            "executability_percentage": 0
        }
        
        # Check if terraform directory exists
        if not os.path.exists(terraform_dir):
            return json.dumps({
                "status": "error",
                "message": f"Terraform directory '{terraform_dir}' does not exist"
            }, indent=2)
        
        # 1. FILE EXISTENCE CHECK
        required_files = [
            "provider.tf", "variables.tf", "main.tf", 
            "outputs.tf", "terraform.tfvars", "README.md"
        ]
        
        for file in required_files:
            filepath = os.path.join(terraform_dir, file)
            validation_report["file_checks"][file] = os.path.exists(filepath)
        
        files_score = sum(validation_report["file_checks"].values()) / len(required_files) * 100
        
        # 2. SYNTAX VALIDATION (terraform fmt check)
        try:
            fmt_result = subprocess.run(
                "terraform fmt -check -recursive",
                shell=True,
                cwd=terraform_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if fmt_result.returncode != 0:
                validation_report["syntax_errors"].append({
                    "type": "formatting",
                    "message": "Formatting issues detected",
                    "files": fmt_result.stdout.split('\n') if fmt_result.stdout else []
                })
        except Exception as e:
            validation_report["syntax_errors"].append({
                "type": "fmt_error",
                "message": str(e)
            })
        
        # 3. TERRAFORM VALIDATE (requires init first)
        try:
            # Try to run validate (might fail if not initialized)
            validate_result = subprocess.run(
                "terraform validate",
                shell=True,
                cwd=terraform_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            validation_report["syntax_validation"] = {
                "status": "pass" if validate_result.returncode == 0 else "fail",
                "output": validate_result.stdout,
                "errors": validate_result.stderr
            }
        except Exception as e:
            validation_report["syntax_validation"] = {
                "status": "error",
                "message": "Validation requires 'terraform init' first",
                "note": str(e)
            }
        
        # 4. CHECK FOR DEPRECATED RESOURCES
        deprecated_mappings = {
            "azurerm_app_service_plan": {
                "replacement": "azurerm_service_plan",
                "reason": "Deprecated since provider v3.0",
                "doc": "https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/service_plan"
            },
            "azurerm_app_service": {
                "replacement": "azurerm_linux_web_app or azurerm_windows_web_app",
                "reason": "Deprecated since provider v3.0",
                "doc": "https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/linux_web_app"
            },
            "azurerm_function_app": {
                "replacement": "azurerm_linux_function_app or azurerm_windows_function_app",
                "reason": "Deprecated since provider v3.0",
                "doc": "https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/linux_function_app"
            }
        }
        
        # Scan main.tf for deprecated resources
        main_tf_path = os.path.join(terraform_dir, "main.tf")
        if os.path.exists(main_tf_path):
            with open(main_tf_path, 'r') as f:
                lines = f.readlines()
                for line_num, line in enumerate(lines, 1):
                    for deprecated, info in deprecated_mappings.items():
                        if f'resource "{deprecated}"' in line:
                            validation_report["deprecated_resources"].append({
                                "file": "main.tf",
                                "line": line_num,
                                "deprecated_resource": deprecated,
                                "replacement": info["replacement"],
                                "reason": info["reason"],
                                "documentation": info["doc"],
                                "code_snippet": line.strip()
                            })
        
        # 5. CHECK PROVIDER VERSIONS
        provider_tf_path = os.path.join(terraform_dir, "provider.tf")
        if os.path.exists(provider_tf_path):
            with open(provider_tf_path, 'r') as f:
                content = f.read()
                
                # Check for azurerm provider version
                azurerm_version_match = re.search(r'azurerm.*?version\s*=\s*["\']([^"\']+)["\']', content, re.DOTALL)
                if azurerm_version_match:
                    version = azurerm_version_match.group(1)
                    validation_report["version_check"]["azurerm_provider"] = {
                        "found": version,
                        "recommended": "~> 4.1",
                        "status": "ok" if "4." in version or "~> 4" in version else "outdated"
                    }
                
                # Check terraform required version
                tf_version_match = re.search(r'required_version\s*=\s*["\']([^"\']+)["\']', content)
                if tf_version_match:
                    version = tf_version_match.group(1)
                    validation_report["version_check"]["terraform_version"] = {
                        "found": version,
                        "recommended": ">= 1.0",
                        "status": "ok"
                    }
        
        # 6. AZURE-SPECIFIC CHECKS
        if os.path.exists(main_tf_path):
            with open(main_tf_path, 'r') as f:
                content = f.read()
                
                # Check for proper resource naming patterns
                resource_names = re.findall(r'name\s*=\s*["\']([^"\']+)["\']', content)
                validation_report["azure_validation"]["resource_names_found"] = len(resource_names)
                
                # Check for location references
                locations = re.findall(r'location\s*=\s*([^\n]+)', content)
                validation_report["azure_validation"]["location_references"] = len(locations)
        
        # 7. CALCULATE EXECUTABILITY SCORE
        scores = {}
        
        # Syntax score (25 points)
        syntax_score = 25
        if validation_report["syntax_errors"]:
            syntax_score -= len(validation_report["syntax_errors"]) * 5
        syntax_score = max(0, syntax_score)
        scores["syntax"] = syntax_score
        
        # Deprecated resources score (20 points)
        deprecated_score = 20
        if validation_report["deprecated_resources"]:
            deprecated_score = max(0, 20 - len(validation_report["deprecated_resources"]) * 5)
        scores["deprecated"] = deprecated_score
        
        # File completeness score (15 points)
        file_score = (sum(validation_report["file_checks"].values()) / len(required_files)) * 15
        scores["files"] = round(file_score, 2)
        
        # Provider version score (15 points)
        version_score = 15
        if validation_report["version_check"]:
            azurerm_check = validation_report["version_check"].get("azurerm_provider", {})
            if azurerm_check.get("status") == "outdated":
                version_score = 10
        scores["version"] = version_score
        
        # Azure compliance score (15 points) - basic check
        azure_score = 15
        if not validation_report["azure_validation"].get("resource_names_found"):
            azure_score = 10
        scores["azure_compliance"] = azure_score
        
        # Documentation score (10 points)
        doc_score = 10 if validation_report["file_checks"].get("README.md") else 5
        scores["documentation"] = doc_score
        
        # Calculate total
        total_score = sum(scores.values())
        validation_report["scores"] = scores
        validation_report["executability_percentage"] = round(total_score, 2)
        
        # Determine status
        if total_score >= 90:
            validation_report["status"] = "EXCELLENT - Ready for deployment"
        elif total_score >= 70:
            validation_report["status"] = "GOOD - Minor fixes recommended"
        elif total_score >= 50:
            validation_report["status"] = "FAIR - Moderate issues to address"
        else:
            validation_report["status"] = "POOR - Major rework required"
        
        return json.dumps(validation_report, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Validation error: {str(e)}"
        }, indent=2)

@tool("Terraform Executor")
def terraform_executor(command: str, working_dir: str = "terraform") -> str:
    """
    Executes Terraform commands (init, plan, apply, destroy).
    Runs commands in the specified working directory.
    """
    import subprocess
    import os
    
    try:
        # Validate command
        valid_commands = ['init', 'plan', 'apply', 'destroy', 'validate', 'fmt']
        cmd_parts = command.split()
        if not cmd_parts or cmd_parts[0] not in valid_commands:
            return f"Error: Invalid command. Must be one of {valid_commands}"
        
        # Ensure working directory exists
        if not os.path.exists(working_dir):
            return f"Error: Working directory {working_dir} does not exist"
        
        # Build full terraform command
        if cmd_parts[0] == 'apply':
            # Auto-approve for apply
            full_command = f"terraform {command} -auto-approve"
        elif cmd_parts[0] == 'destroy':
            # Auto-approve for destroy
            full_command = f"terraform {command} -auto-approve"
        else:
            full_command = f"terraform {command}"
        
        # Execute command
        result = subprocess.run(
            full_command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )
        
        output = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}\n\nReturn Code: {result.returncode}"
        
        if result.returncode == 0:
            return f"SUCCESS: {output}"
        else:
            return f"FAILED: {output}"
    
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 minutes"
    except Exception as e:
        return f"Error executing terraform command: {str(e)}"


@CrewBase
class Replica():
    """Azure Infrastructure Replica crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self):
        super().__init__()
        # Configure Azure OpenAI LLM
        self.llm = LLM(
            model="azure/gpt-4o-mini",
            base_url=os.getenv("AZURE_API_BASE"),
            api_key=os.getenv("AZURE_API_KEY"),
            api_version=os.getenv("AZURE_API_VERSION"),
            temperature=0.2
        
        )

    @agent
    def azure_discovery_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['azure_discovery_agent'], # type: ignore[index]
            verbose=True,
            llm=self.llm,
            tools=[azure_resource_scanner, azure_network_analyzer, azure_dependencies_mapper]
        )

    @agent
    def terraform_generator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['terraform_generator_agent'], # type: ignore[index]
            verbose=True,
            llm=self.llm,
            tools=[terraform_file_writer],
            allow_delegation=False
        )
    
    @agent
    def terraform_validation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['terraform_validation_agent'], # type: ignore[index]
            verbose=True,
            llm=self.llm,
            tools=[terraform_validator]
        )

    @agent
    def terraform_deployment_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['terraform_deployment_agent'], # type: ignore[index]
            verbose=True,
            llm=self.llm,

            tools=[terraform_executor]
            
        )

    @task
    def discovery_task(self) -> Task:
        return Task(
            config=self.tasks_config['discovery_task'], # type: ignore[index]
        )

    @task
    def terraform_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['terraform_generation_task'], # type: ignore[index]
        )

    @task
    def terraform_validation_task(self) -> Task:
        return Task(
            config=self.tasks_config['terraform_validation_task'], # type: ignore[index]
            output_file='terraform_validation_report.md'
        )

    @task
    def terraform_deployment_task(self) -> Task:
        return Task(
            config=self.tasks_config['terraform_deployment_task'], # type: ignore[index]
            output_file='deployment_report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Azure Infrastructure Replica crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

# import os
# from crewai import Agent, Crew, Process, Task, LLM
# from crewai.project import CrewBase, agent, crew, task
# from crewai.agents.agent_builder.base_agent import BaseAgent
# from typing import List
# from crewai_tools import tool

# # Custom tool for Azure resource discovery
# @tool("Azure Resource Scanner")
# def azure_resource_scanner(resource_group: str) -> str:
#     """
#     Scans Azure resources in a resource group and identifies dependencies.
#     Uses Azure CLI commands to gather resource information.
#     """
#     import subprocess
#     import json
    
#     try:
#         # Get all resources in the resource group
#         cmd = f"az resource list --resource-group {resource_group} --output json"
#         result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
#         if result.returncode != 0:
#             return f"Error: {result.stderr}"
        
#         resources = json.loads(result.stdout)
        
#         resource_details = []
#         for resource in resources:
#             resource_id = resource['id']
#             resource_type = resource['type']
#             resource_name = resource['name']
            
#             # Get detailed information for each resource
#             detail_cmd = f"az resource show --ids {resource_id} --output json"
#             detail_result = subprocess.run(detail_cmd, shell=True, capture_output=True, text=True)
            
#             if detail_result.returncode == 0:
#                 detail = json.loads(detail_result.stdout)
#                 resource_details.append({
#                     'name': resource_name,
#                     'type': resource_type,
#                     'id': resource_id,
#                     'location': resource.get('location', ''),
#                     'properties': detail.get('properties', {}),
#                     'sku': detail.get('sku', {}),
#                     'tags': detail.get('tags', {}),
#                     'dependencies': detail.get('dependsOn', [])
#                 })
        
#         return json.dumps(resource_details, indent=2)
    
#     except Exception as e:
#         return f"Error scanning resources: {str(e)}"


# @tool("Azure Network Analyzer")
# def azure_network_analyzer(resource_group: str) -> str:
#     """
#     Analyzes network connections and dependencies between Azure resources.
#     Identifies VNets, subnets, NSGs, and their associations.
#     """
#     import subprocess
#     import json
    
#     try:
#         connections = {}
        
#         # Get VNets with subnets
#         vnet_cmd = f"az network vnet list --resource-group {resource_group} --output json"
#         vnet_result = subprocess.run(vnet_cmd, shell=True, capture_output=True, text=True)
        
#         if vnet_result.returncode == 0:
#             vnets = json.loads(vnet_result.stdout)
#             for vnet in vnets:
#                 # Get subnet details for each vnet
#                 subnet_cmd = f"az network vnet subnet list --resource-group {resource_group} --vnet-name {vnet['name']} --output json"
#                 subnet_result = subprocess.run(subnet_cmd, shell=True, capture_output=True, text=True)
#                 if subnet_result.returncode == 0:
#                     vnet['subnets_detailed'] = json.loads(subnet_result.stdout)
#             connections['vnets'] = vnets
        
#         # Get NSGs with rules
#         nsg_cmd = f"az network nsg list --resource-group {resource_group} --output json"
#         nsg_result = subprocess.run(nsg_cmd, shell=True, capture_output=True, text=True)
        
#         if nsg_result.returncode == 0:
#             nsgs = json.loads(nsg_result.stdout)
#             for nsg in nsgs:
#                 # Get NSG rules
#                 rule_cmd = f"az network nsg rule list --resource-group {resource_group} --nsg-name {nsg['name']} --output json"
#                 rule_result = subprocess.run(rule_cmd, shell=True, capture_output=True, text=True)
#                 if rule_result.returncode == 0:
#                     nsg['rules_detailed'] = json.loads(rule_result.stdout)
#             connections['nsgs'] = nsgs
        
#         # Get Public IPs
#         pip_cmd = f"az network public-ip list --resource-group {resource_group} --output json"
#         pip_result = subprocess.run(pip_cmd, shell=True, capture_output=True, text=True)
        
#         if pip_result.returncode == 0:
#             pips = json.loads(pip_result.stdout)
#             connections['public_ips'] = pips
        
#         # Get NICs (Network Interface Cards)
#         nic_cmd = f"az network nic list --resource-group {resource_group} --output json"
#         nic_result = subprocess.run(nic_cmd, shell=True, capture_output=True, text=True)
        
#         if nic_result.returncode == 0:
#             nics = json.loads(nic_result.stdout)
#             connections['network_interfaces'] = nics
        
#         # Get Load Balancers
#         lb_cmd = f"az network lb list --resource-group {resource_group} --output json"
#         lb_result = subprocess.run(lb_cmd, shell=True, capture_output=True, text=True)
        
#         if lb_result.returncode == 0:
#             lbs = json.loads(lb_result.stdout)
#             connections['load_balancers'] = lbs
        
#         # Get Application Gateways
#         appgw_cmd = f"az network application-gateway list --resource-group {resource_group} --output json"
#         appgw_result = subprocess.run(appgw_cmd, shell=True, capture_output=True, text=True)
        
#         if appgw_result.returncode == 0:
#             appgws = json.loads(appgw_result.stdout)
#             connections['application_gateways'] = appgws
        
#         return json.dumps(connections, indent=2)
    
#     except Exception as e:
#         return f"Error analyzing network: {str(e)}"


# @tool("Azure Service Dependencies Mapper")
# def azure_dependencies_mapper(resource_group: str) -> str:
#     """
#     Maps dependencies between Azure services like databases, storage accounts,
#     app services, and their connections.
#     """
#     import subprocess
#     import json
    
#     try:
#         dependencies = {}
        
#         # Get Storage Accounts
#         storage_cmd = f"az storage account list --resource-group {resource_group} --output json"
#         storage_result = subprocess.run(storage_cmd, shell=True, capture_output=True, text=True)
        
#         if storage_result.returncode == 0:
#             storage_accounts = json.loads(storage_result.stdout)
#             for sa in storage_accounts:
#                 # Get network rules
#                 network_cmd = f"az storage account show --name {sa['name']} --resource-group {resource_group} --query networkRuleSet --output json"
#                 network_result = subprocess.run(network_cmd, shell=True, capture_output=True, text=True)
#                 if network_result.returncode == 0:
#                     sa['network_rules'] = json.loads(network_result.stdout)
#             dependencies['storage_accounts'] = storage_accounts
        
#         # Get SQL Servers and Databases
#         sql_cmd = f"az sql server list --resource-group {resource_group} --output json"
#         sql_result = subprocess.run(sql_cmd, shell=True, capture_output=True, text=True)
        
#         if sql_result.returncode == 0:
#             sql_servers = json.loads(sql_result.stdout)
#             for server in sql_servers:
#                 # Get databases
#                 db_cmd = f"az sql db list --resource-group {resource_group} --server {server['name']} --output json"
#                 db_result = subprocess.run(db_cmd, shell=True, capture_output=True, text=True)
#                 if db_result.returncode == 0:
#                     server['databases'] = json.loads(db_result.stdout)
                
#                 # Get firewall rules
#                 fw_cmd = f"az sql server firewall-rule list --resource-group {resource_group} --server {server['name']} --output json"
#                 fw_result = subprocess.run(fw_cmd, shell=True, capture_output=True, text=True)
#                 if fw_result.returncode == 0:
#                     server['firewall_rules'] = json.loads(fw_result.stdout)
#             dependencies['sql_servers'] = sql_servers
        
#         # Get App Services
#         webapp_cmd = f"az webapp list --resource-group {resource_group} --output json"
#         webapp_result = subprocess.run(webapp_cmd, shell=True, capture_output=True, text=True)
        
#         if webapp_result.returncode == 0:
#             webapps = json.loads(webapp_result.stdout)
#             for webapp in webapps:
#                 # Get app settings
#                 settings_cmd = f"az webapp config appsettings list --resource-group {resource_group} --name {webapp['name']} --output json"
#                 settings_result = subprocess.run(settings_cmd, shell=True, capture_output=True, text=True)
#                 if settings_result.returncode == 0:
#                     webapp['app_settings'] = json.loads(settings_result.stdout)
                
#                 # Get connection strings
#                 conn_cmd = f"az webapp config connection-string list --resource-group {resource_group} --name {webapp['name']} --output json"
#                 conn_result = subprocess.run(conn_cmd, shell=True, capture_output=True, text=True)
#                 if conn_result.returncode == 0:
#                     webapp['connection_strings'] = json.loads(conn_result.stdout)
#             dependencies['webapps'] = webapps
        
#         # Get App Service Plans
#         plan_cmd = f"az appservice plan list --resource-group {resource_group} --output json"
#         plan_result = subprocess.run(plan_cmd, shell=True, capture_output=True, text=True)
        
#         if plan_result.returncode == 0:
#             plans = json.loads(plan_result.stdout)
#             dependencies['app_service_plans'] = plans
        
#         # Get CosmosDB
#         cosmos_cmd = f"az cosmosdb list --resource-group {resource_group} --output json"
#         cosmos_result = subprocess.run(cosmos_cmd, shell=True, capture_output=True, text=True)
        
#         if cosmos_result.returncode == 0:
#             cosmos_accounts = json.loads(cosmos_result.stdout)
#             dependencies['cosmos_accounts'] = cosmos_accounts
        
#         # Get Key Vaults
#         kv_cmd = f"az keyvault list --resource-group {resource_group} --output json"
#         kv_result = subprocess.run(kv_cmd, shell=True, capture_output=True, text=True)
        
#         if kv_result.returncode == 0:
#             keyvaults = json.loads(kv_result.stdout)
#             for kv in keyvaults:
#                 # Get access policies
#                 policy_cmd = f"az keyvault show --name {kv['name']} --resource-group {resource_group} --query properties.accessPolicies --output json"
#                 policy_result = subprocess.run(policy_cmd, shell=True, capture_output=True, text=True)
#                 if policy_result.returncode == 0:
#                     kv['access_policies'] = json.loads(policy_result.stdout)
#             dependencies['keyvaults'] = keyvaults
        
#         # Get Virtual Machines
#         vm_cmd = f"az vm list --resource-group {resource_group} --output json"
#         vm_result = subprocess.run(vm_cmd, shell=True, capture_output=True, text=True)
        
#         if vm_result.returncode == 0:
#             vms = json.loads(vm_result.stdout)
#             for vm in vms:
#                 # Get VM details including NICs
#                 vm_detail_cmd = f"az vm show --resource-group {resource_group} --name {vm['name']} --output json"
#                 vm_detail_result = subprocess.run(vm_detail_cmd, shell=True, capture_output=True, text=True)
#                 if vm_detail_result.returncode == 0:
#                     vm['details'] = json.loads(vm_detail_result.stdout)
#             dependencies['virtual_machines'] = vms
        
#         # Get Function Apps
#         func_cmd = f"az functionapp list --resource-group {resource_group} --output json"
#         func_result = subprocess.run(func_cmd, shell=True, capture_output=True, text=True)
        
#         if func_result.returncode == 0:
#             functions = json.loads(func_result.stdout)
#             for func in functions:
#                 # Get app settings
#                 settings_cmd = f"az functionapp config appsettings list --resource-group {resource_group} --name {func['name']} --output json"
#                 settings_result = subprocess.run(settings_cmd, shell=True, capture_output=True, text=True)
#                 if settings_result.returncode == 0:
#                     func['app_settings'] = json.loads(settings_result.stdout)
#             dependencies['function_apps'] = functions
        
#         return json.dumps(dependencies, indent=2)
    
#     except Exception as e:
#         return f"Error mapping dependencies: {str(e)}"


# @CrewBase
# class Replica():
#     """Azure Infrastructure Replica crew"""

#     agents: List[BaseAgent]
#     tasks: List[Task]

#     def __init__(self):
#         super().__init__()
#         # Configure Azure OpenAI LLM
#         self.llm = LLM(
#             model="azure/gpt-4o",
#             base_url=os.getenv("AZURE_API_BASE"),
#             api_key=os.getenv("AZURE_API_KEY"),
#             api_version=os.getenv("AZURE_API_VERSION")
#         )

#     @agent
#     def azure_discovery_agent(self) -> Agent:
#         return Agent(
#             config=self.agents_config['azure_discovery_agent'], # type: ignore[index]
#             verbose=True,
#             llm=self.llm,
#             tools=[azure_resource_scanner, azure_network_analyzer, azure_dependencies_mapper]
#         )

#     @agent
#     def terraform_generator_agent(self) -> Agent:
#         return Agent(
#             config=self.agents_config['terraform_generator_agent'], # type: ignore[index]
#             verbose=True,
#             llm=self.llm
#         )

#     @task
#     def discovery_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['discovery_task'], # type: ignore[index]
#         )

#     @task
#     def terraform_generation_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['terraform_generation_task'], # type: ignore[index]
#             output_file='terraform_infrastructure.tf'
#         )

#     @crew
#     def crew(self) -> Crew:
#         """Creates the Azure Infrastructure Replica crew"""
#         return Crew(
#             agents=self.agents,
#             tasks=self.tasks,
#             process=Process.sequential,
#             verbose=True,
#         )

# import os
# from crewai import Agent, Crew, Process, Task, LLM
# from crewai.project import CrewBase, agent, crew, task
# from crewai.agents.agent_builder.base_agent import BaseAgent
# from typing import List
# # If you want to run a snippet of code before or after the crew starts,
# # you can use the @before_kickoff and @after_kickoff decorators
# # https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# @CrewBase
# class Replica():
#     """Replica crew"""

#     agents: List[BaseAgent]
#     tasks: List[Task]

#     def __init__(self):
#         super().__init__()
#         # Configure Azure OpenAI LLM
#         self.llm = LLM(
#             model="azure/gpt-4o",
#             base_url=os.getenv("AZURE_API_BASE"),
#             api_key=os.getenv("AZURE_API_KEY"),
#             api_version=os.getenv("AZURE_API_VERSION")
#         )

#     # Learn more about YAML configuration files here:
#     # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
#     # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
#     # If you would like to add tools to your agents, you can learn more about it here:
#     # https://docs.crewai.com/concepts/agents#agent-tools
#     @agent
#     def researcher(self) -> Agent:
#         return Agent(
#             config=self.agents_config['researcher'], # type: ignore[index]
#             verbose=True,
#             llm=self.llm
#         )

#     @agent
#     def reporting_analyst(self) -> Agent:
#         return Agent(
#             config=self.agents_config['reporting_analyst'], # type: ignore[index]
#             verbose=True,
#             llm=self.llm
#         )

#     # To learn more about structured task outputs,
#     # task dependencies, and task callbacks, check out the documentation:
#     # https://docs.crewai.com/concepts/tasks#overview-of-a-task
#     @task
#     def research_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['research_task'], # type: ignore[index]
#         )

#     @task
#     def reporting_task(self) -> Task:
#         return Task(
#             config=self.tasks_config['reporting_task'], # type: ignore[index]
#             output_file='report.md'
#         )

#     @crew
#     def crew(self) -> Crew:
#         """Creates the Replica crew"""
#         # To learn how to add knowledge sources to your crew, check out the documentation:
#         # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

#         return Crew(
#             agents=self.agents, # Automatically created by the @agent decorator
#             tasks=self.tasks, # Automatically created by the @task decorator
#             process=Process.sequential,
#             verbose=True,
#             # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
#         )
