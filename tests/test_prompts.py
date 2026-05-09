"""
Testes automatizados para validação do prompt otimizado.

Os 6 testes obrigatórios validam o prompt `bug_to_user_story_v2`:

1. test_prompt_has_system_prompt   — campo existe e não está vazio
2. test_prompt_has_role_definition — define uma persona (Role Prompting)
3. test_prompt_mentions_format     — exige formato User Story / Critérios de Aceitação
4. test_prompt_has_few_shot_examples — contém exemplos de entrada/saída (Few-shot)
5. test_prompt_no_todos            — não há [TODO]/FIXME/XXX pendentes
6. test_minimum_techniques         — pelo menos 2 técnicas declaradas no metadata

Executar:
    poetry run pytest tests/test_prompts.py -v
"""
import re
import sys
from pathlib import Path

import pytest
import yaml

# Permite import de utils.py se necessário
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


@pytest.fixture(scope="module")
def prompt_data():
    """Carrega o YAML do prompt v2 uma única vez por módulo de teste."""
    assert PROMPT_FILE.exists(), f"Arquivo de prompt não encontrado: {PROMPT_FILE}"
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert PROMPT_KEY in data, f"Chave '{PROMPT_KEY}' ausente no YAML"
    return data[PROMPT_KEY]


@pytest.fixture(scope="module")
def system_prompt(prompt_data):
    return prompt_data.get("system_prompt", "") or ""


class TestPrompts:

    def test_prompt_has_system_prompt(self, system_prompt):
        """Campo `system_prompt` existe, é string e não está vazio."""
        assert isinstance(system_prompt, str), "system_prompt deve ser string"
        assert system_prompt.strip(), "system_prompt está vazio"
        assert len(system_prompt) >= 100, (
            f"system_prompt muito curto ({len(system_prompt)} chars) — "
            "esperado um prompt elaborado"
        )

    def test_prompt_has_role_definition(self, system_prompt):
        """Define uma persona explícita (Role Prompting).

        Aceita variações como 'Você é um Product Owner', 'You are a',
        'Atue como', 'Aja como'.
        """
        patterns = [
            r"\bvocê é\b",
            r"\byou are\b",
            r"\batue como\b",
            r"\baja como\b",
            r"\bact as\b",
        ]
        text = system_prompt.lower()
        matched = [p for p in patterns if re.search(p, text)]
        assert matched, (
            "Nenhuma definição de persona encontrada. Esperado algo como "
            "'Você é um Product Owner...' no início do system_prompt."
        )

    def test_prompt_mentions_format(self, system_prompt):
        """Exige formato User Story / Critérios de Aceitação ou estrutura Markdown.

        O prompt v2 usa formato User Story padrão BDD ('Como ... eu quero ... para que')
        e seções de Critérios de Aceitação (Dado/Quando/Então).
        """
        format_signals = [
            r"user story",
            r"critérios de aceit",
            r"como um .* eu quero",
            r"dado que",
            r"quando .*",
            r"então .*",
            r"=== USER STORY PRINCIPAL ===",
        ]
        text = system_prompt.lower()
        matched = [p for p in format_signals if re.search(p, text)]
        assert len(matched) >= 3, (
            "Prompt não exige formato User Story/Critérios de Aceitação. "
            f"Sinais encontrados: {matched}"
        )

    def test_prompt_has_few_shot_examples(self, system_prompt):
        """Contém pelo menos 2 exemplos completos de entrada/saída (Few-shot).

        O prompt v2 contém 7 exemplos numerados (### Exemplo 1 ... ### Exemplo 7)
        com blocos 'Entrada:' e 'Saída:'.
        """
        example_headers = re.findall(r"###?\s*Exemplo\s+\d+", system_prompt, flags=re.IGNORECASE)
        entradas = len(re.findall(r"\bEntrada:", system_prompt))
        saidas = len(re.findall(r"\bSaída:", system_prompt))

        assert len(example_headers) >= 2, (
            f"Esperados pelo menos 2 cabeçalhos '### Exemplo N', encontrados: "
            f"{len(example_headers)}"
        )
        assert entradas >= 2, f"Esperados pelo menos 2 blocos 'Entrada:', encontrados: {entradas}"
        assert saidas >= 2, f"Esperados pelo menos 2 blocos 'Saída:', encontrados: {saidas}"

    def test_prompt_no_todos(self, prompt_data, system_prompt):
        """Garante que não há marcadores [TODO]/FIXME/XXX/TBD pendentes em
        nenhum campo string do prompt.
        """
        forbidden_markers = ["[TODO]", "TODO:", "FIXME", "XXX", "TBD", "<placeholder>"]

        # Junta todos os campos string do prompt para inspeção
        textual_fields = []
        for key, value in prompt_data.items():
            if isinstance(value, str):
                textual_fields.append((key, value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        textual_fields.append((key, item))

        offenders = []
        for field_name, content in textual_fields:
            for marker in forbidden_markers:
                if marker in content:
                    offenders.append(f"{field_name}: '{marker}'")

        assert not offenders, (
            f"Marcadores pendentes encontrados no prompt: {offenders}"
        )

    def test_minimum_techniques(self, prompt_data):
        """Metadados declaram pelo menos 2 técnicas (campo `techniques`).

        Aceita variações comuns: `techniques`, `techniques_applied`.
        """
        techniques = (
            prompt_data.get("techniques")
            or prompt_data.get("techniques_applied")
            or []
        )
        assert isinstance(techniques, list), (
            f"Campo 'techniques' deve ser lista, encontrado: {type(techniques).__name__}"
        )
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requerido, encontradas: {len(techniques)} "
            f"({techniques})"
        )
        # Garante que as técnicas declaradas são strings não vazias
        for t in techniques:
            assert isinstance(t, str) and t.strip(), (
                f"Técnica inválida no metadata: {t!r}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
