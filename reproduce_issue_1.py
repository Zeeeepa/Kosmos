
import os
from kosmos.config import ResearchConfig, KosmosConfig
from pydantic_settings import BaseSettings

# Set env var to simulate the issue
os.environ["ENABLED_DOMAINS"] = "biology,physics"
os.environ["ANTHROPIC_API_KEY"] = "dummy" # satisfy validation

try:
    print("Attempting to load ResearchConfig directly...")
    config = ResearchConfig()
    print(f"ResearchConfig loaded: {config.enabled_domains}")
except Exception as e:
    print(f"ResearchConfig failed: {e}")

try:
    print("\nAttempting to load KosmosConfig...")
    # We need to ensure nested configs are also picked up if they are loading from env
    config = KosmosConfig()
    print(f"KosmosConfig loaded. Research domains: {config.research.enabled_domains}")
except Exception as e:
    print(f"KosmosConfig failed: {e}")
