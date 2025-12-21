import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

from utils import Header, make_dash_table
import pandas as pd
import requests


def get_github_repos(username='danhngo'):
    """
    Fetch repositories for a GitHub user and sort by most active (based on push date).
    Falls back to mock data if GitHub API is unavailable.
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
                    'Description': (repo['description'] or 'No description')[:60] + '...' if repo['description'] and len(repo['description']) > 60 else (repo['description'] or 'No description'),
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
    except Exception as e:
        # Return mock data on exception
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


def create_layout(app):
    # Fetch GitHub repos
    df_repos = get_github_repos('danhngo')
    
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
                                        f"Showing repositories for user 'danhngo' sorted by most recent activity ({len(df_repos)} repos)",
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
