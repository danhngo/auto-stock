import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from utils import Header, make_dash_table
import pandas as pd
import requests


def truncate_description(description, max_length=60):
    """Truncate description to a maximum length with ellipsis."""
    if not description:
        return 'No description'
    if len(description) > max_length:
        return description[:max_length] + '...'
    return description


def get_github_repos(username='danhngo'):
    """
    Fetch repositories for a GitHub user and sort by most active (based on push date).
    Falls back to mock data if GitHub API is unavailable.
    
    Note: This implementation does not use authentication, which means it's subject
    to GitHub's rate limits (60 requests/hour for unauthenticated requests).
    For production use, consider adding GitHub token authentication.
    """
    try:
        url = f'https://api.github.com/users/{username}/repos'
        params = {
            'sort': 'pushed',  # Sort by last push date
            'direction': 'desc',  # Descending order (most recent first)
            'per_page': 30  # Get up to 30 repos
        }
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            repos = response.json()
            
            # Create a DataFrame with relevant information
            repo_data = []
            for repo in repos:
                repo_data.append({
                    'Name': repo['name'],
                    'Description': truncate_description(repo.get('description')),
                    'Stars': repo['stargazers_count'],
                    'Forks': repo['forks_count'],
                    'Language': repo['language'] or 'N/A',
                    'Last Updated': repo['pushed_at'][:10]  # Just the date part
                })
            
            df = pd.DataFrame(repo_data)
            return df
        else:
            # Return mock data on error
            return get_mock_repos()
    except (requests.RequestException, requests.Timeout, ConnectionError) as e:
        # Log the error (in production, use proper logging)
        print(f"Failed to fetch GitHub repos: {e}")
        return get_mock_repos()
    except Exception as e:
        # Catch any other unexpected errors
        print(f"Unexpected error fetching GitHub repos: {e}")
        return get_mock_repos()


def get_mock_repos():
    """
    Return mock repository data for demonstration purposes.
    This is used when the GitHub API is unavailable.
    """
    mock_data = [
        {
            'Name': 'auto-stock',
            'Description': 'Financial dashboard for stock analysis',
            'Stars': 15,
            'Forks': 3,
            'Language': 'Python',
            'Last Updated': '2023-12-15'
        },
        {
            'Name': 'machine-learning-project',
            'Description': 'ML algorithms and data analysis tools',
            'Stars': 42,
            'Forks': 8,
            'Language': 'Python',
            'Last Updated': '2023-12-10'
        },
        {
            'Name': 'web-scraper',
            'Description': 'Web scraping tool for data collection',
            'Stars': 28,
            'Forks': 6,
            'Language': 'Python',
            'Last Updated': '2023-11-20'
        },
        {
            'Name': 'api-gateway',
            'Description': 'RESTful API gateway service',
            'Stars': 35,
            'Forks': 12,
            'Language': 'JavaScript',
            'Last Updated': '2023-10-15'
        },
        {
            'Name': 'data-pipeline',
            'Description': 'ETL pipeline for data processing',
            'Stars': 19,
            'Forks': 4,
            'Language': 'Python',
            'Last Updated': '2023-09-30'
        }
    ]
    
    return pd.DataFrame(mock_data)


# Default GitHub username - can be overridden via environment variable
DEFAULT_GITHUB_USER = 'danhngo'


def create_layout(app, username=None):
    """
    Create the layout for the GitHub repos page.
    
    Args:
        app: The Dash app instance
        username: GitHub username to fetch repos for (defaults to DEFAULT_GITHUB_USER)
    """
    if username is None:
        username = DEFAULT_GITHUB_USER
    
    # Fetch GitHub repos
    df_repos = get_github_repos(username)
    
    return html.Div(
        [
            Header(app),
            # page for GitHub repos
            html.Div(
                [
                    # Row 1
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H6("Most Active GitHub Repositories", className="subtitle padded"),
                                    html.P(
                                        f"Showing repositories for user '{username}' sorted by most recent activity ({len(df_repos)} repos)",
                                        style={"color": "#7a7a7a"}
                                    ),
                                    html.Div(
                                        id="div-github-repos",
                                        children=make_dash_table(df_repos),
                                        className="twelve columns"
                                    ),
                                ],
                                className="twelve columns",
                            )
                        ],
                        className="row ",
                    ),
                ],
                className="sub_page",
            ),
        ],
        className="page",
    )
