"""
utils.py — Funções auxiliares para leitura, escrita e log.
"""

import os
from datetime import datetime


def ler_arquivo(caminho: str) -> str:
    """
    Lê arquivo TXT com fallback de encoding.
    Tenta UTF-8 primeiro, depois latin-1.
    """
    for encoding in ('utf-8', 'latin-1', 'cp1252'):
        try:
            with open(caminho, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Não foi possível decodificar o arquivo: {caminho}")


def salvar_arquivo(caminho: str, conteudo: str) -> None:
    """Salva conteúdo em arquivo TXT com encoding UTF-8."""
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(conteudo)


def gerar_log(caminho_log: str, nome_arquivo: str, mapeamentos: list[dict]) -> None:
    """
    Grava log de operação em arquivo.
    Cada entrada contém data/hora, nome do arquivo e detalhes das substituições.
    """
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linhas = [
        f"{'='*60}",
        f"Data/Hora: {agora}",
        f"Arquivo: {nome_arquivo}",
        f"{'─'*60}",
    ]
    total = 0
    for m in mapeamentos:
        linhas.append(f"  {m['incorreto']} → {m['correto']}  |  {m['contagem']} substituição(ões)")
        total += m['contagem']
    linhas.append(f"{'─'*60}")
    linhas.append(f"Total de substituições: {total}")
    linhas.append(f"{'='*60}\n")

    modo = 'a' if os.path.exists(caminho_log) else 'w'
    with open(caminho_log, modo, encoding='utf-8') as f:
        f.write('\n'.join(linhas))


def caminho_log_padrao(caminho_saida: str) -> str:
    """Retorna o caminho padrão do arquivo de log, ao lado do arquivo de saída."""
    pasta = os.path.dirname(caminho_saida) or '.'
    return os.path.join(pasta, 'sepfix_log.txt')
