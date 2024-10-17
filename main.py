import requests
import os

COLLABORATOR_USERNAME = input("Enter username : ")
BASE_URL = "https://api.github.com"

def get_repositories():
    repos = []
    page = 1
    while True:
        url = f"{BASE_URL}/user/repos?page={page}&per_page=100"
        response = requests.get(url, headers={
            "Authorization": f"Bearer {"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"}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })

        if response.status_code != 200:
            print(f"Error fetching repositories: {response.status_code}, {response.text}")
            break

        repo_data = response.json()

        if not repo_data:
            break

        repos.extend(repo_data)
        page += 1

    return repos


def is_collaborator_present(repo_name):

    url = f"{BASE_URL}/repos/{repo_name}/collaborators"
    response = requests.get(url, headers={
        "Authorization": f"Bearer {"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"}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    })

    if response.status_code == 200:
        contributors_data = response.json()
        for contributor in contributors_data:
            if contributor['login'] == COLLABORATOR_USERNAME:
                return True  # User is a contributor
    elif response.status_code != 404:
        print(f"Error fetching contributors for {repo_name}: {response.status_code}, {response.text}")

    return False  # User not found in contributors


def remove_collaborator(repo_name):

    url = f"{BASE_URL}/repos/{repo_name}/collaborators/{COLLABORATOR_USERNAME}"
    response = requests.delete(url, headers={
        "Authorization": f"Bearer {"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"}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    })

    if response.status_code == 204:
        print(f"Successfully removed {COLLABORATOR_USERNAME} from {repo_name}")
    else:
        print(f"Failed to remove {COLLABORATOR_USERNAME} from {repo_name}: {response.status_code}, {response.text}")


def main():

    print("Fetching repositories...")
    repos = get_repositories()

    if not repos:
        print("No repositories found!")
        return

    # Check which repositories have the contributor
    repos_with_contributor = []
    for repo in repos:
        repo_name = repo['full_name']  # Use the full name (including the username) for the repo
        print(f"Checking {repo_name} for {COLLABORATOR_USERNAME}...")
        if is_collaborator_present(repo_name):
            repos_with_contributor.append(repo_name)

    if not repos_with_contributor:
        print(f"{COLLABORATOR_USERNAME} is not a collaborator in any of your repositories.")
        return

    # Display the repositories with the contributor and ask for confirmation
    print(f"\n{COLLABORATOR_USERNAME} is a collaborator in the following repositories:")
    for repo in repos_with_contributor:
        print(f"- {repo}")

    # Ask for confirmation before proceeding with the removal
    confirmation = input(f"\nDo you want to remove {COLLABORATOR_USERNAME} from all these repositories? (yes/no): ").lower()

    if confirmation == 'yes':
        for repo in repos_with_contributor:
            print(f"Removing {COLLABORATOR_USERNAME} from {repo}...")
            remove_collaborator(repo)
        print(f"\n{COLLABORATOR_USERNAME} has been removed from all listed repositories.")
    else:
        print("\nOperation canceled. No changes were made.")


if __name__ == "__main__":
    main()
