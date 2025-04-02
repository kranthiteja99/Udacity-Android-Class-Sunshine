from typing import Optional
import typer
from rich.console import Console
from battle_test.main import run_benchmark  # Imports main benchmark function

# Initialize Typer app with description
app = typer.Typer(
    name="livekit-battle-test",
    help="CLI to benchmark AI voice agents against simulated customers."
)

console = Console()  # Rich console for nicer output

import json
import typer  # Re-import not necessary; already imported above

app = typer.Typer()  # Duplicate definition; keep only one if cleaning up

# Command to display persona information from the JSON file
@app.command("show-personas")
def show_personas():
    with open("personas.json") as f:
        personas = json.load(f)

    for i, p in enumerate(personas, 1):
        print(f"\nPersona {i}:")
        print(f"  Name: {p['name']}")
        print(f"  ZIP Code: {p['zip_code']}")
        print(f"  Traits: {', '.join(p['persona_traits'])}")
        print(f"  Audio File: {p['audio_file']}")

# Simple command to echo input text
@app.command()
def echo(text: str):
    """Echo back text."""
    console.print(text)

# Command to greet user by name (or fallback)
@app.command()
def hello(name: Optional[str] = None):
    """Say hello."""
    console.print(f"Hello {name or 'Stranger'}")

# Main benchmark runner via CLI
@app.command()
def benchmark():
    """Run the benchmark suite on defined personas."""
    run_benchmark()

# Entry point for CLI when script is run directly
if __name__ == "__main__":
    app()
