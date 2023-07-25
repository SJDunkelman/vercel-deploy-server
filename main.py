import requests
import subprocess
import os
import shutil
import uuid

vercel_access_token = "6glHQZKOQ4eTJHsOOSvOL3ta"
github_repo_url = "https://github.com/SJDunkelman/test-astro-build"
GITHUB_REPO = "SJDunkelman/test-astro-build"

def create_vercel_project(access_token, github_repo):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    data = {
        "name": "api-deployment-test",  # Set your desired project name here
        "gitRepository": {
            "repo": github_repo,
            "type": "github"
        },
        "framework": "astro"  # Set the framework to "astro" for Astro JS projects
    }

    response = requests.post("https://api.vercel.com/v12/projects", headers=headers, json=data)
    response_data = response.json()

    if "error" in response_data:
        raise Exception(f"Error creating Vercel project: {response_data['error']['message']}")

    project_id = response_data["id"]
    return project_id

def set_deployment_alias(access_token, deployment_id, alias):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    data = {
        "alias": alias
    }

    response = requests.post(f"https://api.vercel.com/v12/now/deployments/{deployment_id}/aliases", headers=headers, json=data)
    response_data = response.json()

    if "error" in response_data:
        raise Exception(f"Error setting up deployment alias: {response_data['error']['message']}")

    print(f"Alias '{alias}' set up for the deployment!")

def main():
    try:
        # Clone the GitHub repository
        subprocess.run(["git", "clone", f"https://github.com/{GITHUB_REPO}.git"])
        # Change directory to the cloned repository
        os.chdir(GITHUB_REPO.split("/")[1])

        # Assuming the Astro build output is in the "dist" directory
        build_command = "npm run build"
        subprocess.run(build_command, shell=True, check=True)

        # Step 1: Create the Vercel project
        project_id = create_vercel_project(vercel_access_token, github_repo_url)
        print(f"Vercel project created! Project ID: {project_id}")

        # Step 2: Deploy the project
        deploy_command = f"npx vercel --token {vercel_access_token} --prod"
        subprocess.run(deploy_command, shell=True, check=True)

        # Step 3: Set up an alias for the deployment
        alias = uuid.uuid4()  # Replace with your desired alias
        set_deployment_alias(vercel_access_token, project_id, alias)

        # Print the deployment URL with the alias
        deployment_url = f"https://{alias}"
        print(f"Successfully deployed Astro JS website to Vercel: {deployment_url}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up the local repository
        os.chdir("..")
        shutil.rmtree(GITHUB_REPO.split("/")[1])

if __name__ == "__main__":
    pass
