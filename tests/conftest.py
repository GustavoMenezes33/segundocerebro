"""Fixtures compartilhadas.

Regra que vale para todo teste de configuração: nenhum deles pode ler o `.env`
real da máquina. Um teste que passa porque a máquina do desenvolvedor estava
bem configurada não testa nada — por isso `carregar(env_file=None)` em todos.
"""

from __future__ import annotations

import os

import pytest

# Os oito obrigatórios com valores válidos mínimos.
BASE_VALIDA = {
    "TELEGRAM_BOT_TOKEN": "123456:AAHtestetestetestetestetesteteste",
    "TELEGRAM_USUARIO_AUTORIZADO": "42",
    "LLM_API_KEY": "chave-de-teste",
    "LLM_PROVEDOR": "provedor-de-teste",
    "LLM_MODELO": "modelo-de-teste",
    "DIGEST_EMAIL_DESTINO": "gustavo@example.com",
    "DIGEST_EMAIL_REMETENTE": "cerebro@example.com",
    "SMTP_SERVIDOR": "smtp.example.com",
}

_PREFIXOS = (
    "TELEGRAM_", "LLM_", "DIGEST_", "SMTP_", "PAINEL_",
    "ACERVO_", "WHISPER_", "CAPTURA_", "FILA_", "AUDIO_", "LOG_",
)


@pytest.fixture
def ambiente_limpo(monkeypatch):
    """Remove qualquer variável do projeto herdada do ambiente real."""
    for chave in list(os.environ):
        if chave.startswith(_PREFIXOS):
            monkeypatch.delenv(chave, raising=False)
    return monkeypatch


@pytest.fixture
def ambiente_valido(ambiente_limpo, tmp_path):
    """Ambiente mínimo suficiente para o sistema iniciar."""
    for chave, valor in BASE_VALIDA.items():
        ambiente_limpo.setenv(chave, valor)
    # Caminhos isolados: nenhum teste escreve na pasta de dados real.
    ambiente_limpo.setenv("ACERVO_PASTA", str(tmp_path / "acervo"))
    ambiente_limpo.setenv("CAPTURA_PASTA_AUDIO", str(tmp_path / "audios"))
    ambiente_limpo.setenv("WHISPER_PASTA_MODELOS", str(tmp_path / "modelos"))
    ambiente_limpo.setenv("FILA_PASTA", str(tmp_path / "fila"))
    ambiente_limpo.setenv("ACERVO_INDICE_ARQUIVO", str(tmp_path / "indice.json"))
    ambiente_limpo.setenv("CAPTURA_ESTADO_POLLING", str(tmp_path / "estado.json"))
    return ambiente_limpo
