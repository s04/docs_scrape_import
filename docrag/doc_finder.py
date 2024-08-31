import requests
from github_docs_extractor import clone_or_pull_repo, find_markdown_files
from urllib.parse import urlparse

def find_package_docs(package_info):
    if package_info['doc_url']:
        # Use the custom doc URL if provided
        parsed_url = urlparse(package_info['doc_url'])
        if parsed_url.netloc == 'github.com':
            return {"type": "github", "url": package_info['doc_url']}
        elif 'readthedocs.io' in parsed_url.netloc:
            return {"type": "readthedocs", "url": package_info['doc_url']}
        else:
            return {"type": "custom", "url": package_info['doc_url']}

    # If no custom URL, proceed with the default search
    package_name = package_info['name']
    
    # Try to find documentation on ReadTheDocs
    rtd_url = f"https://{package_name}.readthedocs.io/en/latest/"
    response = requests.get(rtd_url)
    if response.status_code == 200:
        return {"type": "readthedocs", "url": rtd_url}

    # If not on ReadTheDocs, try GitHub
    github_api_url = f"https://api.github.com/search/repositories?q={package_name}"
    response = requests.get(github_api_url)
    if response.status_code == 200:
        data = response.json()
        if data["total_count"] > 0:
            repo_url = data["items"][0]["html_url"]
            return {"type": "github", "url": repo_url}

    # If no documentation found
    return None

def process_package_docs(package_info, target_dir):
    doc_info = find_package_docs(package_info)
    if doc_info is None:
        print(f"No documentation found for {package_info['name']}")
        return []

    if doc_info["type"] == "github":
        clone_or_pull_repo(doc_info["url"], target_dir)
        return find_markdown_files(target_dir)
    elif doc_info["type"] == "readthedocs":
        # For ReadTheDocs, we'd need to implement a web scraper
        # This is a placeholder for now
        print(f"ReadTheDocs scraping not implemented for {package_info['name']}")
        return []
    elif doc_info["type"] == "custom":
        print(f"Custom documentation URL provided for {package_info['name']}: {doc_info['url']}")
        # Here you could implement custom handling for different types of documentation sites
        # For now, we'll just print the URL
        return []