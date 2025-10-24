#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from replica.crew import Replica

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def run():
    """
    Run the Azure infrastructure replication crew.
    Resources will be replicated within the SAME resource group and automatically deployed.
    """
    # Get inputs from command line or use defaults
    if len(sys.argv) > 1:
        resource_group = sys.argv[1]
        name_prefix = sys.argv[2] if len(sys.argv) > 2 else "replica"
        target_env = sys.argv[3] if len(sys.argv) > 3 else "dev"
    else:
        print("\n" + "="*70)
        print("Azure Infrastructure Replication with Auto-Deployment")
        print("="*70 + "\n")
        resource_group = input("Enter resource group name: ").strip()
        name_prefix = input("Enter name prefix for replicas (e.g., 'dev', 'staging'): ").strip()
        target_env = input("Enter target environment (dev/staging/production): ").strip()
    
    inputs = {
        'resource_group': resource_group,
        'name_prefix': name_prefix,
        'target_environment': target_env,
        'current_year': str(datetime.now().year)
    }
    
    print(f"\n{'='*70}")
    print(f"Azure Infrastructure Replication with Auto-Deployment")
    print(f"{'='*70}")
    print(f"Resource Group: {resource_group}")
    print(f"Name Prefix for Replicas: {name_prefix}")
    print(f"Target Environment: {target_env}")
    print(f"{'='*70}")
    print(f"WORKFLOW:")
    print(f"1. Discover existing Azure resources")
    print(f"2. Generate Terraform configuration files")
    print(f"3. Initialize and validate Terraform")
    print(f"4. Deploy replicated infrastructure")
    print(f"{'='*70}")
    print(f"NOTE: All new resources will be created in the SAME resource group")
    print(f"      with names prefixed by '{name_prefix}-'")
    print(f"{'='*70}\n")
    
    # Confirm before proceeding
    if len(sys.argv) <= 1:
        confirm = input("Proceed with discovery and deployment? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("Deployment cancelled.")
            return
    
    try:
        print("\n🚀 Starting infrastructure replication workflow...\n")
        result = Replica().crew().kickoff(inputs=inputs)
        
        print(f"\n{'='*70}")
        print("✅ Infrastructure replication workflow completed!")
        print(f"{'='*70}")
        print(f"")
        print(f"Generated Files:")
        print(f"  📁 terraform/")
        print(f"     ├── provider.tf")
        print(f"     ├── variables.tf")
        print(f"     ├── main.tf")
        print(f"     ├── outputs.tf")
        print(f"     ├── terraform.tfvars")
        print(f"     └── README.md")
        print(f"  📄 deployment_report.md (deployment results)")
        print(f"")
        print(f"Check 'deployment_report.md' for detailed deployment results")
        print(f"{'='*70}\n")
        
        return result
    except Exception as e:
        print(f"\n❌ Error occurred during workflow execution:\n")
        print(f"{str(e)}\n")
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "resource_group": "training-rg",
        "name_prefix": "train",
        "target_environment": "dev",
        'current_year': str(datetime.now().year)
    }
    try:
        Replica().crew().train(
            n_iterations=int(sys.argv[1]), 
            filename=sys.argv[2], 
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Replica().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "resource_group": "test-rg",
        "name_prefix": "test",
        "target_environment": "dev",
        "current_year": str(datetime.now().year)
    }
    
    try:
        Replica().crew().test(
            n_iterations=int(sys.argv[1]), 
            eval_llm=sys.argv[2], 
            inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


def plan_only():
    """
    Run discovery and generate Terraform files but don't apply (plan only mode).
    """
    print("\n" + "="*70)
    print("Azure Infrastructure Replication (PLAN ONLY - No Deployment)")
    print("="*70 + "\n")
    
    resource_group = input("Enter resource group name: ").strip()
    name_prefix = input("Enter name prefix for replicas: ").strip()
    target_env = input("Enter target environment: ").strip()
    
    inputs = {
        'resource_group': resource_group,
        'name_prefix': name_prefix,
        'target_environment': target_env,
        'current_year': str(datetime.now().year),
        'plan_only': True
    }
    
    print(f"\n{'='*70}")
    print(f"Running in PLAN ONLY mode")
    print(f"Terraform files will be generated but NOT applied")
    print(f"{'='*70}\n")
    
    try:
        result = Replica().crew().kickoff(inputs=inputs)
        print(f"\n{'='*70}")
        print("✅ Plan generation completed!")
        print(f"Review the terraform/ directory and run 'terraform apply' manually")
        print(f"{'='*70}\n")
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running plan: {e}")


if __name__ == "__main__":
    # Check if plan-only mode requested
    if len(sys.argv) > 1 and sys.argv[1] == "--plan-only":
        plan_only()
    else:
        run()

# #!/usr/bin/env python
# import sys
# import warnings
# from datetime import datetime
# from replica.crew import Replica

# warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# def run():
#     """
#     Run the Azure infrastructure replication crew.
#     Resources will be replicated within the SAME resource group.
#     """
#     # Get inputs from command line or use defaults
#     resource_group = sys.argv[1] if len(sys.argv) > 1 else input("Enter resource group name: ")
#     name_prefix = sys.argv[2] if len(sys.argv) > 2 else input("Enter name prefix for replicas (e.g., 'dev', 'staging'): ")
#     target_env = sys.argv[3] if len(sys.argv) > 3 else input("Enter target environment (dev/staging/production): ")
    
#     inputs = {
#         'resource_group': resource_group,
#         'name_prefix': name_prefix,
#         'target_environment': target_env,
#         'current_year': str(datetime.now().year)
#     }
    
#     print(f"\n{'='*70}")
#     print(f"Azure Infrastructure Replication (Same Resource Group)")
#     print(f"{'='*70}")
#     print(f"Resource Group: {resource_group}")
#     print(f"Name Prefix for Replicas: {name_prefix}")
#     print(f"Target Environment: {target_env}")
#     print(f"{'='*70}")
#     print(f"NOTE: All new resources will be created in the SAME resource group")
#     print(f"      with names prefixed by '{name_prefix}-'")
#     print(f"{'='*70}\n")
    
#     try:
#         result = Replica().crew().kickoff(inputs=inputs)
#         print(f"\n{'='*70}")
#         print("Infrastructure replication completed successfully!")
#         print(f"Check 'terraform_infrastructure.tf' for the generated Terraform code")
#         print(f"")
#         print(f"Next steps:")
#         print(f"1. Review the generated Terraform code")
#         print(f"2. Set up your terraform.tfvars file")
#         print(f"3. Run: terraform init")
#         print(f"4. Run: terraform plan")
#         print(f"5. Run: terraform apply")
#         print(f"{'='*70}\n")
#         return result
#     except Exception as e:
#         raise Exception(f"An error occurred while running the crew: {e}")


# def train():
#     """
#     Train the crew for a given number of iterations.
#     """
#     inputs = {
#         "resource_group": "training-rg",
#         "name_prefix": "train",
#         "target_environment": "dev",
#         'current_year': str(datetime.now().year)
#     }
#     try:
#         Replica().crew().train(
#             n_iterations=int(sys.argv[1]), 
#             filename=sys.argv[2], 
#             inputs=inputs
#         )
#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")


# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         Replica().crew().replay(task_id=sys.argv[1])
#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")


# def test():
#     """
#     Test the crew execution and returns the results.
#     """
#     inputs = {
#         "resource_group": "test-rg",
#         "name_prefix": "test",
#         "target_environment": "dev",
#         "current_year": str(datetime.now().year)
#     }
    
#     try:
#         Replica().crew().test(
#             n_iterations=int(sys.argv[1]), 
#             eval_llm=sys.argv[2], 
#             inputs=inputs
#         )
#     except Exception as e:
#         raise Exception(f"An error occurred while testing the crew: {e}")


# if __name__ == "__main__":
#     run()


# #!/usr/bin/env python
# import sys
# import warnings

# from datetime import datetime

# from replica.crew import Replica

# warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# # This main file is intended to be a way for you to run your
# # crew locally, so refrain from adding unnecessary logic into this file.
# # Replace with inputs you want to test with, it will automatically
# # interpolate any tasks and agents information

# def run():
#     """
#     Run the crew.
#     """
#     inputs = {
#         'topic': 'AI LLMs',
#         'current_year': str(datetime.now().year)
#     }
    
#     try:
#         Replica().crew().kickoff(inputs=inputs)
#     except Exception as e:
#         raise Exception(f"An error occurred while running the crew: {e}")


# def train():
#     """
#     Train the crew for a given number of iterations.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         'current_year': str(datetime.now().year)
#     }
#     try:
#         Replica().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while training the crew: {e}")

# def replay():
#     """
#     Replay the crew execution from a specific task.
#     """
#     try:
#         Replica().crew().replay(task_id=sys.argv[1])

#     except Exception as e:
#         raise Exception(f"An error occurred while replaying the crew: {e}")

# def test():
#     """
#     Test the crew execution and returns the results.
#     """
#     inputs = {
#         "topic": "AI LLMs",
#         "current_year": str(datetime.now().year)
#     }
    
#     try:
#         Replica().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

#     except Exception as e:
#         raise Exception(f"An error occurred while testing the crew: {e}")
