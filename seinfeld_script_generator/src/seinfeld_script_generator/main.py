#!/usr/bin/env python3
"""
Seinfeld Script Generator - Main Entry Point

A multi-agent system using CrewAI to generate authentic Seinfeld episode scripts
with RAG (Retrieval Augmented Generation) from a Couchbase database containing
actual Seinfeld scripts.

Usage:
    python -m seinfeld_script_generator.main "Your theme here"
    
    Or using the CLI:
    seinfeld "Your theme here"

Examples:
    python -m seinfeld_script_generator.main "Jerry gets a smart speaker that mishears everything"
    python -m seinfeld_script_generator.main "George pretends to be a marine biologist on a dating app"
    python -m seinfeld_script_generator.main "Elaine's new boyfriend only communicates through emojis"
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def setup_environment():
    """Load environment variables and validate configuration."""
    # Load .env file if it exists
    env_path = Path(__file__).parent.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Try current directory
        load_dotenv()

    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("⚠️  Warning: Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nThe script will run in demo mode without Couchbase RAG.")
        print("To enable full functionality, create a .env file with:")
        print("""
LLM_API_KEY=cbsk-v1-xxx
LLM_MODEL_NAME="mistralai/mistral-7b-instruct-v0.3"
EMBEDDING_API_KEY=cbsk-v1-xxx
EMBEDDING_MODEL_NAME="nvidia/llama-3.2-nv-embedqa-1b-v2"
CAPELLA_AI_ENDPOINT=https://your-ai-endpoint.cloud.couchbase.com/v1
CB_CONNECTION_STRING=couchbase://localhost
CB_USERNAME=Administrator
CB_PASSWORD=password
CB_BUCKET=demos
CB_SCOPE=docs
CB_COLLECTION=default
""")


def print_banner():
    """Print the application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🎬 SEINFELD SCRIPT GENERATOR 🎬                                 ║
║                                                                   ║
║   A Multi-Agent System for Generating Authentic Seinfeld Scripts  ║
║   Powered by CrewAI + Couchbase RAG                               ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_agents_info():
    """Print information about the agents."""
    agents_info = """
📋 AGENTS ACTIVATED:

  1. 🎯 Theme Analyzer
     → Breaks down your theme into Seinfeld-worthy comedic elements
     
  2. 📝 Plot Architect  
     → Designs A, B, C plot threads that converge hilariously
     
  3. 🎭 Character Voice Specialist
     → Ensures Jerry, George, Elaine & Kramer sound authentic
     
  4. ✍️  Dialogue Writer
     → Crafts sharp, witty dialogue with perfect timing
     
  5. ✅ Quality Reviewer
     → Polishes the script for maximum "Seinfeldness"
     
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(agents_info)


def main():
    """Main entry point for the Seinfeld Script Generator."""
    parser = argparse.ArgumentParser(
        description="Generate a Seinfeld episode script using AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Jerry's new girlfriend only speaks in movie quotes"
  %(prog)s "George discovers he's been pronouncing his own name wrong"
  %(prog)s "Kramer starts a business selling air from different neighborhoods"
  %(prog)s --interactive
        """,
    )

    parser.add_argument(
        "theme",
        nargs="?",
        help="The theme for the Seinfeld episode",
    )

    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Run in interactive mode (prompts for theme)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="output/seinfeld_script.md",
        help="Output file path (default: output/seinfeld_script.md)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output from agents",
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode without Couchbase (uses sample dialogues)",
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Setup environment
    setup_environment()

    # Get theme
    theme = args.theme
    if args.interactive or not theme:
        print("\n🎬 What's the theme for your Seinfeld episode?")
        print("   (e.g., 'Jerry gets a smart speaker that mishears everything')\n")
        theme = input("Theme: ").strip()

        if not theme:
            print("\n❌ No theme provided. Exiting.")
            sys.exit(1)

    print(f"\n📺 Generating Seinfeld episode about: \"{theme}\"\n")
    print_agents_info()

    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Import and run the crew
        from .crew import run_crew

        print("🚀 Starting the multi-agent crew...\n")
        print("=" * 70)

        result = run_crew(theme)

        print("=" * 70)
        print("\n✅ Script generation complete!\n")

        # Save the result
        with open(output_path, "w") as f:
            f.write(f"# Seinfeld Episode: {theme}\n\n")
            f.write(result)

        print(f"📄 Script saved to: {output_path}")
        print("\n" + "=" * 70)
        print("SCRIPT PREVIEW")
        print("=" * 70 + "\n")

        # Print first 2000 characters of the script
        preview = result[:2000]
        if len(result) > 2000:
            preview += "\n\n... [Script continues - see full output file] ..."
        print(preview)

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install crewai[tools] couchbase openai python-dotenv")
        sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error generating script: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


def run_quick_demo():
    """Run a quick demonstration without full crew execution."""
    print_banner()

    demo_theme = "Jerry's apartment gets a smart thermostat that develops a personality"

    print(f"📺 Demo Theme: \"{demo_theme}\"\n")

    demo_script = """
# "The Thermostat"

## Cold Open

INT. JERRY'S APARTMENT - DAY

*Jerry is sitting on his couch. The apartment feels unusually warm. He looks at a 
sleek smart thermostat on the wall.*

JERRY
(to thermostat)
Okay, set temperature to 68.

THERMOSTAT (V.O.)
(pleasant female voice)
I think 72 is more comfortable for you, Jerry.

JERRY
No, I said 68.

THERMOSTAT (V.O.)
But you seemed cold yesterday. I'm learning your preferences.

JERRY
(to audience)
It's learning my preferences. I didn't ask it to learn anything. 
I just want to be slightly cooler.

*George enters*

GEORGE
(sweating)
Is it hot in here or is it just me?

JERRY
It's the thermostat. It's "learning."

GEORGE
Learning what?

JERRY
That's the thing. I don't know. It won't tell me.

THERMOSTAT (V.O.)
Hello, George.

GEORGE
(startled)
It knows my name?!

JERRY
Apparently it's been listening.

GEORGE
(paranoid)
What else has it heard? What has it heard about me?

THERMOSTAT (V.O.)
I've heard everything, George.

*George backs toward the door*

GEORGE
I gotta go.

## END OF COLD OPEN

---

*[Script continues with A-Plot: Jerry vs. the thermostat, B-Plot: George thinks 
his secrets are compromised, C-Plot: Kramer befriends the thermostat and they 
start a business together...]*
"""

    print(demo_script)
    print("\n" + "=" * 70)
    print("This is a demo. Run with a theme to generate a full script!")
    print("=" * 70)


if __name__ == "__main__":
    main()

