import re

def parse_requirements(file_path):
    packages = {}
    current_package = None

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract package name and version
                match = re.match(r'^([^=<>]+).*$', line)
                if match:
                    current_package = match.group(1).strip()
                    packages[current_package] = {'name': current_package, 'doc_url': None}
            elif line.startswith('#'):
                # Check for doc link in comment
                doc_match = re.search(r'#\s*(\w+)-docrag:\s*"(https?://[^"]+)"', line)
                if doc_match:
                    package_name, doc_url = doc_match.groups()
                    if package_name in packages:
                        packages[package_name]['doc_url'] = doc_url
                    elif current_package:
                        # If the comment is on a new line, associate it with the last seen package
                        packages[current_package]['doc_url'] = doc_url

    return list(packages.values())