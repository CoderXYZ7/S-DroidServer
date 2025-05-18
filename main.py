from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import subprocess
import os
from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict

app = FastAPI()

# Allow CORS for your web app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Configuration
MAIN_REPO_URL = "https://github.com/CoderXYZ7/sdroid-repos"
BASE_DIR = Path("./repos_data")
MAIN_REPO_DIR = BASE_DIR / "sdroid-repos"
REPOS_JSON_PATH = MAIN_REPO_DIR / "repos.json"

def ensure_dir_exists():
    """Ensure base directory exists"""
    BASE_DIR.mkdir(exist_ok=True)

def run_git_command(cmd: List[str], cwd: str):
    """Run git command with error handling"""
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Git command failed: {result.stderr}")
        return result.stdout
    except Exception as e:
        raise Exception(f"Error executing git command: {str(e)}")

async def init_main_repo():
    """Initialize the main repository if it doesn't exist"""
    ensure_dir_exists()
    try:
        if MAIN_REPO_DIR.exists():
            print("Main repository already exists")
            return True
        else:
            print("Cloning main repository...")
            run_git_command(["git", "clone", MAIN_REPO_URL, str(MAIN_REPO_DIR)], str("./"))
            print("Main repository cloned successfully")
            return True
    except Exception as e:
        print(f"Error initializing main repository: {str(e)}")
        return False

@app.post("/UpdateRepoList")
async def update_repo_list():
    """Fetch and update the main repository"""
    ensure_dir_exists()
    try:
        if MAIN_REPO_DIR.exists():
            print("Updating existing repository...")
            run_git_command(["git", "pull"], str(MAIN_REPO_DIR))
        else:
            print("Cloning repository...")
            run_git_command(["git", "clone", MAIN_REPO_URL, str(MAIN_REPO_DIR)], str("./"))
        return {"status": "success", "message": "Repository updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/UpdateRepos")
async def update_repos():
    """Update all repositories listed in repos.json"""
    # Ensure main repo exists
    if not MAIN_REPO_DIR.exists():
        await init_main_repo()
    
    if not REPOS_JSON_PATH.exists():
        raise HTTPException(status_code=404, detail="repos.json not found")
    
    try:
        with open(REPOS_JSON_PATH) as f:
            repos = json.load(f)
        
        results = []
        for repo_url in repos:
            repo_name = repo_url.split("/")[-1]
            repo_dir = BASE_DIR / repo_name
            if repo_dir.exists():
                results.append(f"Updated {repo_name}: {run_git_command(['git', 'pull'], str(repo_dir))}")
            else:
                results.append(f"Cloned {repo_name}: {run_git_command(['git', 'clone', repo_url, str(repo_dir)], str("./"))}")
        
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/GetRepos")
async def get_repos():
    """Get list of all repositories"""
    # Initialize main repo if it doesn't exist
    if not MAIN_REPO_DIR.exists():
        success = await init_main_repo()
        if not success:
            raise HTTPException(status_code=500, detail="Failed to initialize repository")
    
    if not REPOS_JSON_PATH.exists():
        raise HTTPException(status_code=404, detail="repos.json not found. Try refreshing repositories first.")
    
    with open(REPOS_JSON_PATH) as f:
        repos = json.load(f)
    
    # Extract just the repo names
    repo_names = [url.split("/")[-1] for url in repos]
    return JSONResponse(content={"repos": repo_names})

@app.get("/GetDetails/{repo_name}")
async def get_details(repo_name: str):
    """Get details for a specific repository"""
    repo_dir = BASE_DIR / repo_name
    if not repo_dir.exists():
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Get README
    readme = ""
    readme_path = repo_dir / "README.md"
    if readme_path.exists():
        with open(readme_path) as f:
            readme = f.read()
    
    # Get versions
    versions_dir = repo_dir / "versions"
    versions = []
    if versions_dir.exists():
        versions = sorted([
            {
                "name": f.name,
                "size": f.stat().st_size,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            }
            for f in versions_dir.glob("*.apk")
        ], key=lambda x: x["modified"], reverse=True)
    
    return {
        "name": repo_name,
        "readme": readme,
        "versions": versions
    }

@app.get("/GetFile/{repo_name}/{filename}")
async def get_file(repo_name: str, filename: str):
    """Download a specific file from versions directory"""
    file_path = BASE_DIR / repo_name / "versions" / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        filename=filename,
        media_type="application/vnd.android.package-archive"
    )

@app.get("/GetFavicon/{repo_name}")
async def get_favicon(repo_name: str):
    """Get favicon for a repository"""
    # Check possible locations for favicon
    possible_paths = [
        BASE_DIR / repo_name / "favicon.png",
        BASE_DIR / repo_name / "icon.png",
        BASE_DIR / repo_name / "logo.png",
        BASE_DIR / repo_name / "assets" / "favicon.png",
        BASE_DIR / repo_name / "assets" / "icon.png",
        BASE_DIR / repo_name / "assets" / "logo.png",
        BASE_DIR / repo_name / "images" / "favicon.png",
        BASE_DIR / repo_name / "images" / "icon.png",
        BASE_DIR / repo_name / "images" / "logo.png"
    ]
    
    for path in possible_paths:
        if path.exists():
            return FileResponse(
                path,
                media_type="image/png"
            )
    
    # Return 404 if no favicon found
    raise HTTPException(status_code=404, detail="Favicon not found")

@app.get("/api/status")
async def get_status():
    """Check the status of repositories"""
    main_repo_exists = MAIN_REPO_DIR.exists()
    repos_json_exists = REPOS_JSON_PATH.exists()
    repos_count = 0
    
    if repos_json_exists:
        try:
            with open(REPOS_JSON_PATH) as f:
                repos = json.load(f)
                repos_count = len(repos)
        except:
            pass
    
    return {
        "mainRepoInitialized": main_repo_exists,
        "reposJsonExists": repos_json_exists,
        "reposCount": repos_count,
        "baseDir": str(BASE_DIR)
    }

@app.on_event("startup")
async def startup_event():
    """Initialize directories on startup"""
    ensure_dir_exists()
    # Initialize main repo at startup
    await init_main_repo()