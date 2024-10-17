from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)


# GitHub API URL
BASE_URL = "https://api.github.com"


def get_repositories():
    """Get all repositories (public and private) for the authenticated user."""
    repos = []
    page = 1
    while True:
        url = f"{BASE_URL}/user/repos?page={page}&per_page=100"
        response = requests.get(url, headers={
            "Authorization": f"Bearer {"  "}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })

        if response.status_code != 200:
            return []

        repo_data = response.json()
        if not repo_data:
            break
        repos.extend(repo_data)
        page += 1
    return repos


def is_contributor_present(repo_name, collaborator_username):
    """Check if the specified user is present as a contributor in a repository."""
    url = f"{BASE_URL}/repos/{repo_name}/collaborators"
    response = requests.get(url, headers={
        "Authorization": f"Bearer {"  "}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    })

    if response.status_code == 200:
        contributors_data = response.json()
        for contributor in contributors_data:
            if contributor['login'] == collaborator_username:
                return True
    return False


def remove_collaborator(repo_name, collaborator_username):
    """Remove a collaborator from a repository."""
    url = f"{BASE_URL}/repos/{repo_name}/collaborators/{collaborator_username}"
    response = requests.delete(url, headers={
        "Authorization": f"Bearer {" "}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    })

    return response.status_code == 204


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check_collaborator', methods=['POST'])
def check_collaborator():
    collaborator_username = request.form['collaborator_username']
    repos_with_contributor = []
    repos = get_repositories()

    for repo in repos:
        repo_name = repo['full_name']
        if is_contributor_present(repo_name, collaborator_username):
            repos_with_contributor.append(repo_name)

    return jsonify(repos_with_contributor)


@app.route('/remove_collaborator', methods=['POST'])
def remove_collaborator_route():
    collaborator_username = request.form['collaborator_username']
    repos = request.form.getlist('repos[]')

    results = {}
    for repo in repos:
        success = remove_collaborator(repo, collaborator_username)
        results[repo] = "Success" if success else "Failed"

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
