import os
import json
from liquid import Environment, FileSystemLoader

# Configuration
# This script is now located in prompts/src/
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
# Output directory is the parent directory (prompts/)
PROMPTS_DIR = os.path.dirname(SRC_DIR)
TEMPLATES_DIR = os.path.join(SRC_DIR, "templates")
PARTIALS_DIR = os.path.join(SRC_DIR, "partials")
DATA_FILE = os.path.join(SRC_DIR, "data.json")

def load_data():
    """Load data from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def main():
    # Ensure directories exist
    if not os.path.exists(TEMPLATES_DIR):
        print(f"Templates directory not found: {TEMPLATES_DIR}")
        return

    # Setup Liquid Environment
    # We point loader to SRC_DIR so we can reference partials like 'partials/header.liquid'
    env = Environment(loader=FileSystemLoader(SRC_DIR))

    # Load Data
    data = load_data()

    # List all templates in templates dir
    for root, _, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith(".liquid"):
                template_path = os.path.join(root, file)
                # rel_path for loader should be relative to SRC_DIR
                rel_path = os.path.relpath(template_path, SRC_DIR) # e.g. templates/PAGELOVE.liquid
                
                # Render template
                try:
                    template = env.get_template(rel_path)
                    output = template.render(**data)
                    
                    # Determine output filename (remove .liquid extension)
                    # Output goes to PROMPTS_DIR
                    filename = os.path.splitext(file)[0] + ".md"
                    output_path = os.path.join(PROMPTS_DIR, filename)
                    
                    print(f"Generating {output_path}...")
                    with open(output_path, "w") as f:
                        f.write(output)
                except Exception as e:
                    print(f"Error rendering {rel_path}: {e}")

if __name__ == "__main__":
    main()
