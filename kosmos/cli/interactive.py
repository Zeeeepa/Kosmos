"""
Interactive mode for Kosmos CLI.

Provides an interactive interface for starting research with guided prompts,
domain selection, and configuration options.
"""

import sys
from typing import Optional, List, Dict, Any
from pathlib import Path

from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.console import Group
from rich.text import Text

from kosmos.cli.utils import (
    console,
    print_info,
    print_error,
    print_success,
    get_icon,
    create_table,
)
from kosmos.cli.themes import get_domain_color


# Example research questions by domain
EXAMPLE_QUESTIONS = {
    "biology": [
        "What are the metabolic pathway differences between cancer and normal cells?",
        "How do genetic variants affect protein expression in different tissues?",
        "What is the relationship between microbiome composition and disease states?",
    ],
    "neuroscience": [
        "How does synaptic connectivity relate to neural function in the brain?",
        "What are the molecular mechanisms of neurodegeneration in Alzheimer's disease?",
        "How do different brain regions contribute to cognitive processes?",
    ],
    "materials": [
        "What perovskite compositions optimize photovoltaic efficiency?",
        "How do crystal structures affect thermoelectric properties?",
        "What design principles govern high-temperature superconductors?",
    ],
    "physics": [
        "How do quantum effects influence material properties at nanoscale?",
        "What are the relationships between symmetry and phase transitions?",
        "How does topology affect electronic band structure?",
    ],
    "chemistry": [
        "What reaction mechanisms optimize catalytic efficiency?",
        "How do molecular interactions affect self-assembly?",
        "What structure-property relationships govern drug efficacy?",
    ],
    "general": [
        "What patterns exist in large-scale scientific data?",
        "How do complex systems exhibit emergent behavior?",
        "What are the fundamental principles underlying this phenomenon?",
    ],
}


# Domain descriptions
DOMAIN_DESCRIPTIONS = {
    "biology": "Genomics, proteomics, metabolomics, and biological systems",
    "neuroscience": "Brain connectivity, neurodegeneration, and neural function",
    "materials": "Material properties, crystal structures, and optimization",
    "physics": "Physical phenomena, quantum mechanics, and phase transitions",
    "chemistry": "Chemical reactions, molecular interactions, and synthesis",
    "general": "Cross-domain research and exploratory data analysis",
}


def show_welcome():
    """Display welcome message and introduction."""
    welcome_md = """
# Welcome to Kosmos Interactive Mode

Kosmos is an autonomous AI scientist that can:

* **Generate hypotheses** based on scientific literature and data
* **Design experiments** to test those hypotheses
* **Execute computational experiments** with proper validation
* **Analyze results** and synthesize insights
* **Learn iteratively** from outcomes to refine hypotheses

This interactive mode will guide you through setting up a research project.
"""
    console.print()
    console.print(
        Panel(
            Markdown(welcome_md),
            title=f"[bright_blue]{get_icon('rocket')} Kosmos AI Scientist[/bright_blue]",
            border_style="bright_blue",
        )
    )
    console.print()


def select_domain() -> str:
    """
    Prompt user to select research domain.

    Returns:
        Selected domain name
    """
    console.print(f"[h2]{get_icon('magnifying_glass')} Select Research Domain[/h2]")
    console.print()

    # Create domain table
    table = create_table(
        title="Available Domains",
        columns=["#", "Domain", "Description"],
        show_lines=True,
    )

    domains = list(DOMAIN_DESCRIPTIONS.keys())
    for i, domain in enumerate(domains, 1):
        color = get_domain_color(domain)
        table.add_row(
            str(i),
            Text(domain.title(), style=color),
            DOMAIN_DESCRIPTIONS[domain]
        )

    console.print(table)
    console.print()

    # Prompt for selection
    while True:
        choice = Prompt.ask(
            "[cyan]Choose domain[/cyan]",
            choices=[str(i) for i in range(1, len(domains) + 1)],
            default="6"  # general
        )

        try:
            domain_idx = int(choice) - 1
            selected_domain = domains[domain_idx]
            console.print(f"[success]Selected: {selected_domain.title()}[/success]")
            console.print()
            return selected_domain
        except (ValueError, IndexError):
            print_error("Invalid selection. Please try again.")


def show_examples(domain: str):
    """Show example questions for the selected domain."""
    examples = EXAMPLE_QUESTIONS.get(domain, EXAMPLE_QUESTIONS["general"])

    console.print(f"[h3]{get_icon('book')} Example Questions for {domain.title()}[/h3]")
    console.print()

    for i, example in enumerate(examples, 1):
        console.print(f"  [muted]{i}.[/muted] [italic]{example}[/italic]")

    console.print()


def get_research_question(domain: str) -> str:
    """
    Prompt user for research question.

    Args:
        domain: Selected domain

    Returns:
        Research question string
    """
    show_examples(domain)

    console.print("[cyan]Enter your research question:[/cyan]")
    console.print("[muted](This should be a clear, testable question)[/muted]")
    console.print()

    while True:
        question = Prompt.ask("> ")

        if not question or len(question.strip()) < 10:
            print_error("Question is too short. Please provide more detail.")
            continue

        # Confirm question
        console.print()
        console.print(
            Panel(
                question,
                title="[cyan]Your Research Question[/cyan]",
                border_style="cyan",
            )
        )
        console.print()

        if Confirm.ask("[cyan]Is this correct?[/cyan]", default=True):
            return question.strip()

        console.print()


def configure_research_parameters() -> Dict[str, Any]:
    """
    Configure research parameters.

    Returns:
        Dictionary of research parameters
    """
    console.print(f"[h2]{get_icon('flask')} Configure Research Parameters[/h2]")
    console.print()

    params = {}

    # Max iterations
    console.print("[cyan]Maximum research iterations:[/cyan]")
    console.print("[muted](How many hypothesis-experiment cycles to run)[/muted]")
    max_iterations = IntPrompt.ask(
        "Iterations",
        default=10,
        show_default=True,
    )
    # Validate max_iterations is positive
    if max_iterations < 1:
        console.print("[warning]Iterations must be at least 1. Using default value of 10.[/warning]")
        max_iterations = 10
    params["max_iterations"] = max_iterations
    console.print()

    # Experiment budget
    console.print("[cyan]Enable API budget limit?[/cyan]")
    console.print("[muted](Set a maximum cost for Claude API calls)[/muted]")
    enable_budget = Confirm.ask("Enable budget", default=False)

    if enable_budget:
        params["budget_usd"] = IntPrompt.ask(
            "Budget (USD)",
            default=50,
            show_default=True,
        )
    else:
        params["budget_usd"] = None

    console.print()

    # Cache usage
    console.print("[cyan]Enable caching?[/cyan]")
    console.print("[muted](Reuse previous results to save time and cost)[/muted]")
    params["enable_cache"] = Confirm.ask("Enable cache", default=True)
    console.print()

    # Auto model selection
    console.print("[cyan]Enable automatic model selection?[/cyan]")
    console.print("[muted](Automatically choose Haiku/Sonnet based on complexity)[/muted]")
    params["auto_model_selection"] = Confirm.ask("Auto model selection", default=True)
    console.print()

    # Parallel execution
    console.print("[cyan]Enable parallel execution?[/cyan]")
    console.print("[muted](Run independent experiments simultaneously)[/muted]")
    params["parallel_execution"] = Confirm.ask("Parallel execution", default=False)
    console.print()

    return params


def show_configuration_summary(
    domain: str,
    question: str,
    params: Dict[str, Any]
):
    """Show summary of research configuration."""
    console.print()
    console.print(f"[h2]{get_icon('info')} Research Configuration Summary[/h2]")
    console.print()

    # Configuration table
    table = create_table(
        title="Configuration",
        columns=["Setting", "Value"],
        show_lines=True,
    )

    # Add rows
    domain_text = Text(domain.title(), style=get_domain_color(domain))
    table.add_row("Domain", domain_text)
    table.add_row("Question", question[:60] + "..." if len(question) > 60 else question)
    table.add_row("Max Iterations", str(params["max_iterations"]))

    if params["budget_usd"]:
        table.add_row("Budget", f"${params['budget_usd']} USD")
    else:
        table.add_row("Budget", "[muted]No limit[/muted]")

    table.add_row("Caching", "[success]Enabled[/success]" if params["enable_cache"] else "[error]Disabled[/error]")
    table.add_row("Auto Model Selection", "[success]Enabled[/success]" if params["auto_model_selection"] else "[error]Disabled[/error]")
    table.add_row("Parallel Execution", "[success]Enabled[/success]" if params["parallel_execution"] else "[error]Disabled[/error]")

    console.print(table)
    console.print()


def confirm_and_start() -> bool:
    """
    Confirm configuration and start research.

    Returns:
        True if user confirms, False to cancel
    """
    console.print("[cyan]Ready to start research?[/cyan]")
    console.print()

    confirmed = Confirm.ask(
        "[bright_blue]Start autonomous research[/bright_blue]",
        default=True
    )

    if not confirmed:
        console.print("[warning]Research cancelled by user.[/warning]")
        return False

    console.print()
    print_success(
        "Research started! This may take several minutes to hours depending on complexity.",
        title="Starting Research"
    )
    console.print()

    return True


def run_interactive_mode() -> Optional[Dict[str, Any]]:
    """
    Run interactive research configuration mode.

    Returns:
        Dictionary with research configuration, or None if cancelled
    """
    try:
        # Show welcome
        show_welcome()

        # Select domain
        domain = select_domain()

        # Get research question
        question = get_research_question(domain)

        # Configure parameters
        params = configure_research_parameters()

        # Show summary
        show_configuration_summary(domain, question, params)

        # Confirm and start
        if not confirm_and_start():
            return None

        # Return configuration
        return {
            "domain": domain,
            "question": question,
            **params
        }

    except KeyboardInterrupt:
        console.print("\n[warning]Operation cancelled by user[/warning]")
        return None
    except Exception as e:
        print_error(f"Interactive mode failed: {str(e)}")
        return None


if __name__ == "__main__":
    # Test interactive mode
    result = run_interactive_mode()
    if result:
        console.print("\n[success]Configuration complete![/success]")
        console.print(f"\nResult: {result}")
    else:
        console.print("\n[error]Configuration cancelled.[/error]")
