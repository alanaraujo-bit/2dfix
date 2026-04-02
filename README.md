<div align="center">

<img src="logo.png" alt="2DFIX Logo" width="180"/>

<h1>2DFIX</h1>

<p><strong>Correção Inteligente de Dados em Arquivos de Texto</strong></p>

<p>
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/CustomTkinter-5.x-1E90FF?style=for-the-badge&logo=python&logoColor=white" alt="CustomTkinter"/>
  <img src="https://img.shields.io/badge/PyInstaller-executável-orange?style=for-the-badge" alt="PyInstaller"/>
  <img src="https://img.shields.io/badge/Tema-Dark%20%7C%20Light-8B949E?style=for-the-badge" alt="Temas"/>
  <img src="https://img.shields.io/badge/Plataforma-Windows-0078D4?style=for-the-badge&logo=windows&logoColor=white" alt="Windows"/>
</p>

<br/>

> Ferramenta desktop profissional para **localizar e substituir sequências de texto** em arquivos `.txt` — com interface moderna, suporte a múltiplas substituições simultâneas e geração automática de log.

</div>

---

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Demonstração Visual](#demonstração-visual)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Arquitetura](#arquitetura)
- [Pré-requisitos](#pré-requisitos)
- [Como Instalar e Executar](#como-instalar-e-executar)
- [Como Usar](#como-usar)
- [Geração do Executável](#geração-do-executável)
- [Estrutura de Arquivos](#estrutura-de-arquivos)
- [Log de Operações](#log-de-operações)
- [Configuração e Personalização](#configuração-e-personalização)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## Sobre o Projeto

O **2DFIX** surgiu da necessidade prática de corrigir dados em arquivos de texto em lote — sejam arquivos de dados legados, exports de sistemas, CSVs ou qualquer arquivo `.txt` com padrões incorretos que precisam ser padronizados.

A ferramenta combina uma **interface gráfica moderna e intuitiva** com uma **engine de substituição eficiente**, permitindo que usuários sem conhecimento técnico realizem correções em segundos, sem precisar abrir editores de código ou usar comandos de terminal.

---

## Demonstração Visual

| Tema Escuro | Tema Claro |
|:-:|:-:|
| Interface com fundo `#0E1117` e accent azul `#1E90FF` | Interface com fundo `#F5F7FA` e mesmo accent |

A interface é responsiva — redimensionável entre `800×460` e qualquer tamanho maior — e adapta todos os elementos ao tema selecionado em tempo real, sem necessidade de reinicialização.

---

## Funcionalidades

### Core
- **Substituição múltipla simultânea** — defina quantas regras de substituição precisar em uma única operação
- **Adição e remoção dinâmica de regras** — adicione ou remova pares `incorreto → correto` com um clique
- **Processamento em thread separada** — a UI nunca trava durante o processamento, mesmo em arquivos grandes
- **Auto-renomeação do arquivo de saída** — se o arquivo já existir, gera automaticamente `_1`, `_2`... sem sobrescrever
- **Sugestão automática de nome de saída** — ao selecionar o arquivo de entrada, o campo de saída é pré-preenchido com `_corrigido` no nome

### Compatibilidade
- **Detecção automática de encoding** — tenta `UTF-8`, `latin-1` e `cp1252` em sequência, garantindo leitura de arquivos legados sem erros
- **Saída sempre em UTF-8** — o arquivo corrigido é sempre salvo com encoding moderno e universal

### Interface
- **Tema Dark / Light** — alternância instantânea via botão ☀/☾, sem rebuild da interface
- **Barra de progresso animada** — feedback visual durante o processamento
- **Painel de resultados detalhado** — exibe tempo de execução, total de substituições e o detalhamento por regra
- **Acesso rápido ao resultado** — botões para abrir o arquivo gerado e a pasta de destino diretamente pela aplicação
- **Validação em tempo real** — o botão "Corrigir" só é habilitado quando todos os campos obrigatórios estão preenchidos

### Log Automático
- Gera `sepfix_log.txt` na mesma pasta do arquivo de saída
- Registra data/hora, arquivo processado, cada substituição realizada e o total acumulado
- Modo de escrita em **append** — preserva o histórico de todas as operações anteriores

---

## Tecnologias

| Tecnologia | Versão | Uso |
|---|---|---|
| **Python** | 3.11+ | Linguagem principal |
| **CustomTkinter** | 5.x | Interface gráfica moderna (widgets sobre Tkinter) |
| **Tkinter** | stdlib | Diálogos de sistema (`filedialog`) |
| **threading** | stdlib | Processamento não-bloqueante |
| **PyInstaller** | 6.x | Empacotamento em executável `.exe` standalone |

---

## Arquitetura

O projeto segue uma arquitetura modular de três camadas com separação clara de responsabilidades:

```
┌─────────────────────────────────────────────────────────┐
│                        ui.py                            │
│          Interface gráfica (CustomTkinter)              │
│  App2DFix — gerencia janela, temas, eventos e threads   │
└────────────────────┬────────────────────────────────────┘
                     │ chama
┌────────────────────▼────────────────────────────────────┐
│                    processor.py                         │
│             Engine de processamento                     │
│  processar_arquivo() — orquestra leitura, substituição  │
│  e escrita via funções de utils                         │
└────────────────────┬────────────────────────────────────┘
                     │ usa
┌────────────────────▼────────────────────────────────────┐
│                     utils.py                            │
│               Funções auxiliares puras                  │
│  ler_arquivo · salvar_arquivo · gerar_log               │
│  caminho_log_padrao                                     │
└─────────────────────────────────────────────────────────┘
```

### Fluxo de Execução

```
Usuário preenche campos
        │
        ▼
_campos_validos() → habilita botão
        │
  Clica em "Corrigir"
        │
        ▼
Thread de processamento é criada
        │
        ├── ler_arquivo()       ← fallback de encoding
        ├── substituir_sequencia() × N regras
        ├── salvar_arquivo()    ← sempre UTF-8
        └── gerar_log()         ← append no log
        │
        ▼
after(0, _on_success / _on_error)  ← retorna à thread UI
        │
        ▼
Exibe resultado + botões de acesso rápido
```

---

## Pré-requisitos

- **Python 3.11** ou superior
- **pip** atualizado

```bash
python --version   # deve ser 3.11+
pip --version
```

---

## Como Instalar e Executar

### 1. Clone o repositório

```bash
git clone https://github.com/alanaraujo-bit/2dfix.git
cd 2dfix
```

### 2. (Recomendado) Crie um ambiente virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install customtkinter
```

> **Nota:** todas as outras dependências (`tkinter`, `threading`, `os`, `datetime`) fazem parte da biblioteca padrão do Python e não requerem instalação.

### 4. Execute a aplicação

```bash
python main.py
```

---

## Como Usar

### Passo a passo

1. **Arquivo de entrada** — clique em `…` e selecione o arquivo `.txt` que deseja corrigir.  
   O campo "Arquivo de saída" será preenchido automaticamente com `_corrigido` no nome.

2. **Arquivo de saída** — confirme o caminho sugerido ou clique em `…` para escolher outro local.

3. **Regras de substituição** — preencha os pares:
   - **Sequência incorreta** → texto que você quer encontrar
   - **Sequência correta** → texto pelo qual será substituído

4. **Adicionar mais regras** — clique em `＋ Adicionar substituição` para incluir quantas regras precisar.

5. **Corrigir** — clique em `Corrigir Arquivo` (habilitado automaticamente quando todos os campos estão preenchidos).

6. **Resultado** — o painel exibirá:
   - Tempo de processamento
   - Total de substituições realizadas
   - Detalhamento por regra (`incorreto → correto (Nx)`)
   - Nome do arquivo de saída
   - Botões **Abrir arquivo** e **Abrir pasta**

### Exemplo prático

| Campo | Valor |
|---|---|
| Arquivo de entrada | `C:\dados\exportacao.txt` |
| Arquivo de saída | `C:\dados\exportacao_corrigido.txt` |
| Substituição 1 — incorreto | `CPF` |
| Substituição 1 — correto | `cpf` |
| Substituição 2 — incorreto | `;;` |
| Substituição 2 — correto | `;` |

Ao clicar em "Corrigir", ambas as substituições são aplicadas em uma única passagem pelo arquivo.

---

## Geração do Executável

Para distribuir o 2DFIX sem dependência de Python instalado, use o **PyInstaller** com o spec já configurado:

### Instalar o PyInstaller

```bash
pip install pyinstaller
```

### Gerar o executável

```bash
pyinstaller 2DFIX.spec
```

O executável `2DFIX.exe` será gerado em `dist/2DFIX/` (ou `dist/` no modo onefile). Ele é **standalone** — basta copiar e executar em qualquer máquina Windows, sem instalar Python.

### Configurações do spec

| Opção | Valor |
|---|---|
| `console` | `False` — janela sem terminal visível |
| `upx` | `True` — compressão do executável |
| `icon` | `icon.ico` |
| `onefile` | Sim (binaries + datas embutidos) |

---

## Estrutura de Arquivos

```
2dfix/
├── main.py          # Ponto de entrada — instancia e inicia App2DFix
├── ui.py            # Interface gráfica completa (CustomTkinter)
├── processor.py     # Lógica de processamento e orquestração
├── utils.py         # Funções puras: leitura, escrita e log
├── 2DFIX.spec       # Configuração do PyInstaller
├── icon.ico         # Ícone da aplicação
└── README.md        # Este arquivo
```

---

## Log de Operações

Após cada execução bem-sucedida, um arquivo `sepfix_log.txt` é criado (ou atualizado em append) na mesma pasta do arquivo de saída. Exemplo de conteúdo:

```
============================================================
Data/Hora: 2026-04-01 14:32:07
Arquivo: exportacao.txt
────────────────────────────────────────────────────────────
  CPF → cpf  |  1247 substituição(ões)
  ;; → ;     |  83 substituição(ões)
────────────────────────────────────────────────────────────
Total de substituições: 1330
============================================================
```

O log acumula todas as operações realizadas, facilitando auditoria e rastreabilidade das correções aplicadas.

---

## Configuração e Personalização

### Temas

Os temas são definidos em `ui.py` no dicionário `THEMES`. As cores principais são:

| Token | Dark | Light |
|---|---|---|
| `bg` | `#0E1117` | `#F5F7FA` |
| `card` | `#161B22` | `#FFFFFF` |
| `text` | `#E6EDF3` | `#0A2540` |
| `accent` | `#1E90FF` | `#1E90FF` |

Para personalizar, edite os valores em `THEMES` no início de `ui.py`.

### Encodings suportados na leitura

Definidos em `utils.py → ler_arquivo()`:
- `utf-8`
- `latin-1`
- `cp1252`

Para adicionar suporte a outros encodings, edite a tupla `('utf-8', 'latin-1', 'cp1252')`.

---

## Contribuindo

Contribuições são bem-vindas! Siga os passos:

1. Faça um **fork** do repositório
2. Crie uma branch para sua feature: `git checkout -b feature/minha-funcionalidade`
3. Commit suas mudanças: `git commit -m 'feat: adiciona minha funcionalidade'`
4. Push para a branch: `git push origin feature/minha-funcionalidade`
5. Abra um **Pull Request**

---

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

---

<div align="center">
  <sub>Desenvolvido por <a href="https://github.com/alanaraujo-bit">Alan Araujo</a></sub>
</div>
