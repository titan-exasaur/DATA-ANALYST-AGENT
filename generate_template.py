"""
AI Data Analyst Agent — Project Structure Generator
Run: python generate_structure.py
Creates the full folder + file skeleton in root directory
"""

import os

ROOT = r"/Users/amith2831/Desktop/PROJECTS/DATA ANALYST AGENT"

files = [
    # Root
    ".gitignore",
    "README.md",
    "requirements.txt",
    "requirements-dev.txt",
    "pyproject.toml",
    "Dockerfile",
    "docker-compose.yml",
    "generate_diagrams.py",

    # Config
    "src/__init__.py",
    "src/config/__init__.py",
    "src/config/settings.py",

    # Graph
    "src/graph/__init__.py",
    "src/graph/state.py",
    "src/graph/router.py",
    "src/graph/graph_builder.py",

    # Agents
    "src/agents/__init__.py",
    "src/agents/base_agent.py",
    "src/agents/schema_agent.py",
    "src/agents/cleaning_agent.py",
    "src/agents/query_agent.py",
    "src/agents/analysis_agent.py",
    "src/agents/viz_agent.py",
    "src/agents/report_agent.py",

    # API
    "src/api/__init__.py",
    "src/api/main.py",
    "src/api/middleware.py",
    "src/api/routes/__init__.py",
    "src/api/routes/upload.py",
    "src/api/routes/analyse.py",
    "src/api/routes/sessions.py",

    # DB
    "src/db/__init__.py",
    "src/db/client.py",
    "src/db/models.py",
    "src/db/repositories/__init__.py",
    "src/db/repositories/file_repo.py",
    "src/db/repositories/session_repo.py",

    # Storage
    "src/storage/__init__.py",
    "src/storage/blob_client.py",

    # Static + Templates
    "src/static/css/style.css",
    "src/static/js/app.js",
    "src/templates/index.html",
    "src/templates/result.html",

    # Data Ingestion
    "src/ingestion/__init__.py",
    "src/ingestion/base_loader.py",      
    "src/ingestion/csv_loader.py",        
    "src/ingestion/excel_loader.py",       
    "src/ingestion/url_loader.py",         
    "src/ingestion/validator.py",

    # Tests
    "tests/__init__.py",
    "tests/conftest.py",
    "tests/unit/__init__.py",
    "tests/unit/test_schema_agent.py",
    "tests/unit/test_cleaning_agent.py",
    "tests/unit/test_analysis_agent.py",
    "tests/unit/test_router.py",
    "tests/integration/__init__.py",
    "tests/integration/test_graph_pipeline.py",
    "tests/integration/test_api.py",

    # Notebooks
    "notebooks/research.ipynb",

    # Infra
    "infra/azure/deploy.sh",
    "infra/azure/container_app.bicep",

    # CI/CD
    ".github/workflows/ci.yml",
    ".github/workflows/cd.yml"
      
]

created_files = 0
created_dirs = set()

for rel_path in files:
    full_path = os.path.join(ROOT, rel_path)
    dir_path = os.path.dirname(full_path)

    if dir_path not in created_dirs:
        os.makedirs(dir_path, exist_ok=True)
        created_dirs.add(dir_path)

    with open(full_path, "w") as f:
        f.write("")  # empty file

    created_files += 1

print(f"Created {created_files} files across {len(created_dirs)} directories")
print(f"Project root: ./{ROOT}/\n")

# Print tree
for root_dir, dirs, fnames in os.walk(ROOT):
    dirs[:] = sorted([d for d in dirs if d not in {".git", "__pycache__"}])
    level = root_dir.replace(ROOT, "").count(os.sep)
    indent = "    " * level
    print(f"{indent}{'folder' if level > 0 else ''}{os.path.basename(root_dir)}/")
    for fname in sorted(fnames):
        print(f"{indent} {fname}")