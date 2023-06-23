import os
import subprocess
import requests
import tempfile
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage


# Set the Vercel token
VERCEL_TOKEN = "your vercel token here"
OPENAI_API_KEY = "your opeanai api key here"

# Function to deploy website to Vercel
def deploy_to_vercel(html_content: str, project_name: str, vercel_token: str):
    # Create a temporary directory to store the files for deployment
    with tempfile.TemporaryDirectory() as temp_dir:
        project_dir = Path(temp_dir) / project_name
        os.makedirs(project_dir)

        # Write the HTML content to the index.html file
        with open(project_dir / "index.html", "w") as file:
            file.write(html_content)

        # Write the vercel.json configuration file
        vercel_config = {
            "name": project_name,
            "version": 2,
            "builds": [{"src": "index.html", "use": "@vercel/static"}]
        }

        with open(project_dir / "vercel.json", "w") as file:
            json.dump(vercel_config, file)

        # Deploy to Vercel using the CLI
        cmd = ["vercel", "--token", vercel_token, "-y", "--prod"]
        result = subprocess.run(cmd, cwd=project_dir, capture_output=True, text=True)

        # Output the result of the deployment
        if result.returncode == 0:
            print("Deployment is successful!")
            print(f"Your website is live at: {result.stdout.strip()}")
        else:
            print("Deployment failed. Please see the error message below:")
            print(result.stderr)

# Function to generate the website content
def generate_website_content(github_profile):
    # Use a specific and detailed prompt for the AI model
    prompt = f"""Create a professional, elegant, and responsive portfolio website for a developer.
    The website should include a navigation bar, a header section with the user's name and a brief introduction,
    an About Me section with the user's profile image and a description, a Projects section showcasing the user's work,
    and a Contact section with a form. It should also include a footer with copyright information.
    The design should be modern, with a clean layout, appealing visuals, and subtle animations.
    Include the following information from the provided GitHub profile:
    ---
    {github_profile}
    """

    # Initialize the Chat model
    chat = ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.2, max_tokens=2500)

    # Messages to pass to the Chat model
    messages = [
        SystemMessage(content="You are an expert web designer. Generate HTML and CSS code that is professional, aesthetically pleasing, and user-friendly."),
        HumanMessage(content=prompt)
    ]

    # Get the response from the model
    response = chat(messages)
    return response.content

# Function to create a portfolio website for a GitHub user
def create_portfolio_for_github_user(username):
    # Fetch GitHub user data
    response = requests.get(f"https://api.github.com/users/{username}")
    if response.status_code != 200:
        print(f"Error fetching GitHub profile data. Status code: {response.status_code}")
        return

    # Generate website content
    github_profile_data = response.json()
    html_content = generate_website_content(github_profile_data)

    # Define the project name for Vercel deployment
    project_name = f"{username}-portfolio"

    # Deploy the website content to Vercel
    deploy_to_vercel(html_content, project_name, VERCEL_TOKEN)

# Input GitHub username and create a portfolio
github_username = "add_your_username"
create_portfolio_for_github_user(github_username)
