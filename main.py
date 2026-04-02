#!/usr/bin/env python3
"""
2DFIX — Correção Inteligente de Dados

Ponto de entrada da aplicação.
Execute com: python main.py
"""

import sys
import os

# Garante que o diretório do script está no path (para imports locais)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui import App2DFix


def main():
    app = App2DFix()
    app.mainloop()


if __name__ == "__main__":
    main()
