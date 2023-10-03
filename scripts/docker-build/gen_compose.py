import requests


def latest_tag(repo_name: str):
    response = requests.get(
        f"https://hub.docker.com/v2/repositories/{repo_name}/tags/?page_size=1"
    )
    if response.status_code == 200:
        return response.json()["results"][0]["name"]
    else:
        raise Exception("Failed to fetch the latest tag")


def generate_compose_content(repo_name: str):
    latest_tag_value = latest_tag(repo_name)
    service = repo_name.split("/")[1]
    compose_content = f"""
version: "3"
services:
  {service}:
    image: {repo_name}:{latest_tag_value}
    environment:
      - DISPLAY=host.docker.internal:0.0
    volumes:
      - /tmp/.X11-unix:/tmp/.X11-unix
    network_mode: "host"
    command: python -m {service}
"""

    return compose_content.strip()


def write_compose_file(content: str, output_path: str):
    with open(output_path, "w") as output_file:
        output_file.write(content)


if __name__ == "__main__":
    compose_content = generate_compose_content(repo_name="ashgw/litecrypt")
    write_compose_file(content=compose_content, output_path="docker-compose.yml")
