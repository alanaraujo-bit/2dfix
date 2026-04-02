"""
processor.py — Lógica de substituição de sequências em arquivos TXT.
"""

from utils import (
    ler_arquivo,
    salvar_arquivo,
    gerar_log,
    caminho_log_padrao,
)


def substituir_sequencia(texto: str, seq_antiga: str, seq_nova: str) -> tuple[str, int]:
    """
    Substitui todas as ocorrências de uma sequência pela nova.
    Retorna (texto_corrigido, total_substituicoes).
    """
    contagem = texto.count(seq_antiga)
    if contagem > 0:
        texto = texto.replace(seq_antiga, seq_nova)
    return texto, contagem


def processar_arquivo(
    caminho_entrada: str,
    caminho_saida: str,
    mapeamentos: list[tuple[str, str]],
) -> list[dict]:
    """
    Processa o arquivo de entrada aplicando todas as substituições.

    Parâmetros:
        caminho_entrada: caminho do arquivo TXT original
        caminho_saida: caminho do arquivo TXT corrigido
        mapeamentos: lista de tuplas (sequencia_antiga, sequencia_nova)

    Retorna lista de dicts com detalhes de cada substituição.
    """
    texto = ler_arquivo(caminho_entrada)
    resultados = []

    for seq_antiga, seq_nova in mapeamentos:
        texto, contagem = substituir_sequencia(texto, seq_antiga, seq_nova)
        resultados.append({
            'incorreto': seq_antiga,
            'correto': seq_nova,
            'contagem': contagem,
        })

    salvar_arquivo(caminho_saida, texto)

    # Gerar log ao lado do arquivo de saída
    caminho_log = caminho_log_padrao(caminho_saida)
    nome_arquivo = caminho_entrada.replace('\\', '/').split('/')[-1]
    gerar_log(caminho_log, nome_arquivo, resultados)

    return resultados
