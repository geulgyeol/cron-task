import os
import re
from huggingface_hub import HfApi
import requests
from datetime import datetime, timezone, timedelta

HF_TOKEN = os.getenv("HF_TOKEN") # will be injected by kubernetes secret
if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is not set.")
HTML_STORAGE_PATH: str = "html-storage.default.svc.cluster.local"
SPACE_NAME = "geulgyeol/README"

hf_api = HfApi(token=HF_TOKEN)

def fetch_files_data():
    url = f"http://{HTML_STORAGE_PATH}/files"
    response = requests.get(url)
    response.raise_for_status()

    return response.json()

def get_updated_page_content(old_page: str, new_page_count: int):
    # find <!-- geulgyeol-read-start -->0<!-- geulgyeol-read-end --> then update the page count, keeping the same format
    # use regex to find and replace

    pretty_number = f"{new_page_count:,}"
    new_page = re.sub(r"(<!-- geulgyeol-read-start -->)([0-9,]+)(<!-- geulgyeol-read-end -->)",
                      lambda m: m.group(1) + pretty_number + m.group(3),
                      old_page)
    
    # update the last updated time <!-- geulgyeol-read-time-start -->KST 2025-11-29 1:00:30<!-- geulgyeol-read-time-end -->
    now_kst = datetime.now(timezone.utc) + timedelta(hours=9)
    formatted_time = now_kst.strftime("KST %Y-%m-%d %H:%M:%S")
    new_page = re.sub(r"(<!-- geulgyeol-read-time-start -->)(.*?)(<!-- geulgyeol-read-time-end -->)",
                      lambda m: m.group(1) + formatted_time + m.group(3),
                      new_page)
    
    return new_page

def update():
    files_data = fetch_files_data()
    total = files_data["total"]

    if not isinstance(total, int):
        raise ValueError("total is not an integer.")
    
    readme_file = hf_api.hf_hub_download(repo_id=SPACE_NAME, filename="README.md", repo_type="space")
    with open(readme_file, "r", encoding="utf-8") as f:
        old_readme_content = f.read()
    new_readme_content = get_updated_page_content(old_readme_content, total)
    hf_api.upload_file(
        path_or_fileobj=new_readme_content.encode("utf-8"),
        path_in_repo="README.md",
        repo_id=SPACE_NAME,
        repo_type="space"
    )

def main():
    update()

if __name__ == "__main__":
    main()