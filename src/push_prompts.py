"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

# Garante que o .env da raiz do projeto seja carregado independente do CWD
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        api_key = os.environ.get("LANGSMITH_API_KEY")
        username = os.environ.get("USERNAME_LANGSMITH_HUB")

        if not api_key:
            print("Erro: LANGSMITH_API_KEY não definido no .env")
            return False
        if not username:
            print("Erro: USERNAME_LANGSMITH_HUB não definido no .env")
            return False

        # Usa apenas o nome do prompt — o LangSmith infere o owner pela API key.
        # Passar "username/name" causa erro "Cannot create a prompt for another tenant"
        # porque o SDK tenta resolver o tenant pelo handle, não pela sessão autenticada.
        hub_path = prompt_name

        system_prompt = prompt_data.get("system_prompt", "")
        user_prompt = prompt_data.get("user_prompt", "")

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])

        print(f"Fazendo push para {username}/{hub_path}...")

        description = prompt_data.get("description", "")

        # Usa o Client do langsmith diretamente para garantir autenticação correta
        client = Client(api_key=api_key)
        url = client.push_prompt(
            hub_path,
            object=prompt_template,
            is_public=False,
            description=description or None,
        )
        print(f"Push bem-sucedido! URL: {url}")

        tags = prompt_data.get("tags", [])
        if tags:
            print(f"Tags identificadas no YAML: {', '.join(tags)}")

        return True
    except Exception as e:
        print(f"Erro ao fazer push para o LangSmith: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []
    
    if "system_prompt" not in prompt_data:
        errors.append("Falta a chave 'system_prompt'")
    if "user_prompt" not in prompt_data:
        errors.append("Falta a chave 'user_prompt'")
        
    return len(errors) == 0, errors


def main():
    """Função principal"""
    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB", "LANGSMITH_ENDPOINT", "LANGSMITH_PROJECT"]
    if not check_env_vars(required_vars):
        return 1
        
    print_section_header("Inicia o push dos prompts para o LangSmith Prompt Hub")
    
    yaml_path = "prompts/bug_to_user_story_v2.yml"
    print(f"Lendo {yaml_path}...")
    
    data = load_yaml(yaml_path)
    if not data:
        print("Erro ao carregar o arquivo yaml de prompts.")
        return 1
        
    for prompt_name, prompt_data in data.items():
        is_valid, errors = validate_prompt(prompt_data)
        if not is_valid:
            print(f"O prompt '{prompt_name}' não é válido: {errors}")
            continue
            
        push_prompt_to_langsmith(prompt_name, prompt_data)
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
