"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header
from langsmith import Client

load_dotenv()


def pull_prompts_from_langsmith():
    client = Client()
    prompt = client.pull_prompt("leonanluppi/bug_to_user_story_v1")


def main():
    """Função principal"""
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB", "LANGSMITH_ENDPOINT", "LANGSMITH_PROJECT"]
    check_env_vars(required_vars)
    print_section_header("Inicia o pull dos prompts do LangSmith Prompt Hub")
    pull_prompts_from_langsmith()
    print("Prompts puxados e salvos em prompts/bug_to_user_story_v1.yml")


if __name__ == "__main__":
    sys.exit(main())
