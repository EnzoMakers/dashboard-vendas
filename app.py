import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import time

# ===== CONFIGURAÇÃO DE PÁGINAS =====
def configurar_paginas():
    """Configurar sistema de páginas do dashboard"""
    if "pagina_atual" not in st.session_state:
        st.session_state.pagina_atual = "Dashboard Principal"
    paginas = {
        "Dashboard Principal": "📊 Dashboard Principal",
        "Faturamento e Metas": "🎯 Faturamento e Metas",
        "Análise por Sabor": "🍦 Análise por Sabor",  # NOVA PÁGINA
    }
    return paginas

# Configurar páginas
paginas_disponiveis = configurar_paginas()

# ADICIONAR ESTAS LINHAS AQUI:
if "page_mode" not in st.session_state:
    st.session_state.page_mode = "dashboard"


def calcular_margem_percentual(valor_net, custo_total):
    """
    Calcula margem percentual usando a fórmula: (1 - Custo Total/Valor NET) * 100
    """
    if valor_net == 0 or pd.isna(valor_net) or pd.isna(custo_total) or custo_total == 0:
        return 0
    # ✅ FÓRMULA EXATA: 1 - (Custo Total / Valor NET Total)
    margem = (1 - (custo_total / valor_net)) * 100
    return margem  # Sem limitação artificial de min/max


# ✅ FUNÇÃO PARA QUEBRAR NOMES LONGOS NA LEGENDA
def quebrar_nome_legenda(nome, max_chars=25):
    """
    Quebra nomes longos em múltiplas linhas para a legenda
    """
    if len(nome) <= max_chars:
        return nome

    # Tentar quebrar por espaços primeiro
    palavras = nome.split(" ")
    linhas = []
    linha_atual = ""

    for palavra in palavras:
        if len(linha_atual + " " + palavra) <= max_chars:
            if linha_atual:
                linha_atual += " " + palavra
            else:
                linha_atual = palavra
        else:
            if linha_atual:
                linhas.append(linha_atual)
                linha_atual = palavra
            else:
                # Palavra muito longa, forçar quebra
                linhas.append(palavra[:max_chars])
                linha_atual = palavra[max_chars:]

    if linha_atual:
        linhas.append(linha_atual)

    return "<br>".join(linhas)


# ============ CSS E VISUAL PREMIUM HEADER E UPLOAD ============

st.set_page_config(
    page_title="DashBoard de Faturamento",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========== CONTROLE DE PÁGINAS ===========
if "page_mode" not in st.session_state:
    st.session_state.page_mode = "dashboard"

st.markdown(
    """
<style>
@keyframes pulse {
  from { filter: brightness(1.0);}
  to { filter: brightness(1.25) drop-shadow(0 0 8px #99D0FA55);}
}
@keyframes bounceIn {
  0%{transform:scale(.7);}
  40%{transform:scale(1.12);}
  60%{transform:scale(.97);}
  100%{transform:scale(1);}
}
hr.custom-hr {
  border: 0;
  border-top: 1.5px solid #444444;
  margin: 34px 0 16px 0;
}
</style>
""",
    unsafe_allow_html=True,
)


# Header com logo da empresa
def create_header_with_logo():
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        # Logo da empresa
        try:
            st.image("assets/logo.png", width=250)
        except:
            st.markdown("# 🏢")  # Fallback

    # ✅ TEXTO EM LARGURA TOTAL (preservando seu estilo original)
    st.markdown(
        """
    <h1 style="text-align:center; color:#fff; font-size:3.2em; font-weight:900; margin-bottom:0; margin-top:10px;">
      DashBoard de Faturamento <span style="color:#ADD8E6">- TPMB</span>
    </h1>
    <div style="text-align:center; color:#bfcfe6; font-size:1.26em; font-weight:500; margin-bottom:1.4em; margin-top:20px;">
      Este dashboard interativo permite analisar dados de faturamento, margem e custos.<br>
      Faça o upload do seu arquivo <b>CSV</b> ou <b>Excel</b> e explore as métricas e gráficos!
    </div>
    """,
        unsafe_allow_html=True,
    )


# Chamar a função
create_header_with_logo()

# ======= BLOCO VISUAL DE UPLOAD MULTIARQUIVO + SELEÇÃO =======

uploaded_files = st.file_uploader(
    "Arraste e solte um ou mais arquivos (CSV/Excel)",
    type=["csv", "xlsx"],
    accept_multiple_files=True,
    key="custom_uploader",  # key única, usada só aqui!
)
file_selected = None
if uploaded_files:
    # Salvar arquivos carregados no session_state
    st.session_state.uploaded_files = uploaded_files

    file_names = [f.name for f in uploaded_files]

    # Restaurar seleção anterior se existir
    default_index = 0
    if (
        "selected_file_name" in st.session_state
        and st.session_state.selected_file_name in file_names
    ):
        default_index = file_names.index(st.session_state.selected_file_name)

    selected_name = st.selectbox(
        "Selecione o arquivo que deseja analisar:", file_names, index=default_index
    )

    # Salvar nome do arquivo selecionado
    st.session_state.selected_file_name = selected_name

    # Vincula o arquivo selecionado
    file_selected = next((f for f in uploaded_files if f.name == selected_name), None)

# Restaurar arquivos do session_state se disponível
elif "uploaded_files" in st.session_state:
    uploaded_files = st.session_state.uploaded_files
    file_names = [f.name for f in uploaded_files]

    if (
        "selected_file_name" in st.session_state
        and st.session_state.selected_file_name in file_names
    ):
        selected_name = st.session_state.selected_file_name
        file_selected = next(
            (f for f in uploaded_files if f.name == selected_name), None
        )

        # Mostrar qual arquivo está sendo usado
        st.info(f"📁 Usando arquivo: **{selected_name}**")

# =========== FEEDBACK VISUAL PREMIUM: ARQUIVO EM ANÁLISE ===========
if file_selected is not None:
    st.markdown(
        f"""
        <div style="margin: 1.2em auto 2.2em auto; max-width:560px; padding:16px 32px;
                    background: linear-gradient(98deg, #2e5137 70%, #3AD28A 100%);
                    border-radius: 14px; box-shadow:0 1px 7px -2px #3AD28A55; color:#fff;
                    font-size:1.12em; display:flex; align-items:center; justify-content:center;">
          <span style="font-size:2em; margin-right:10px; animation: bounceIn 1.3s;">✅</span>
          <span><b>Arquivo <span style='color:#D0FFCE'>{file_selected.name}</span> carregado para análise!</b></span>
        </div>
    """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div style="margin: 1.2em auto 2.2em auto; max-width:650px; padding:20px 38px;
                    background: linear-gradient(94deg, #1e3449 70%, #29415a 100%);
                    border-radius: 13px; box-shadow:0 1px 6px -2px #99D0FA22;
                    color:#ADD8E6; font-size:1.15em; font-weight: 500;
                    display:flex; align-items:center; justify-content:center;">
          <span style="font-size:1.6em; margin-right:14px;">ℹ️</span>
          <span>Aguardando o upload de um arquivo CSV ou Excel para começar a análise...</span>
        </div>
    """,
        unsafe_allow_html=True,
    )

# =========== CARREGAMENTO E PRÉ-PROCESSAMENTO DO ARQUIVO ESCOLHIDO ===========
df = None
if file_selected is not None:
    try:
        file_extension = file_selected.name.split(".")[-1]
        if file_extension == "csv":
            df = pd.read_csv(file_selected, sep=";", decimal=",", encoding="latin1")
        elif file_extension == "xlsx":
            df = pd.read_excel(file_selected)
        else:
            st.error(
                "Formato de arquivo não suportado. Por favor, faça o upload de um arquivo CSV ou Excel."
            )
            st.stop()
        # (aqui segue o restante do seu pipeline: normalização, renomeação de colunas, filtros, etc.)
    except Exception as e:
        st.error(
            f"Ocorreu um erro ao processar o arquivo: {e}. Por favor, verifique o formato e o conteúdo do arquivo."
        )
        st.stop()


# ============ LAYOUT VISUAL INTEGRADO ============
def apply_integrated_layout(fig, title=""):
    fig.update_layout(
        title={
            "text": title,
            "y": 0.93,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 30, "color": "#ADD8E6", "family": "Segoe UI, sans-serif"},
        },
        font=dict(family="Segoe UI, sans-serif", size=18, color="#E0E0E0"),
        plot_bgcolor="#22232B",
        paper_bgcolor="#22232B",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=18, color="#ADD8E6"),
        ),
        margin=dict(l=40, r=40, t=70, b=40),
        xaxis=dict(
            title_font=dict(size=20, color="#ADD8E6", family="Segoe UI, sans-serif"),
            tickfont=dict(size=16, color="#E0E0E0"),
            gridcolor="rgba(160, 160, 160, 0.15)",
            showgrid=True,
            zeroline=False,
            tickangle=-25,
        ),
        yaxis=dict(
            title_font=dict(size=20, color="#ADD8E6", family="Segoe UI, sans-serif"),
            tickfont=dict(size=16, color="#E0E0E0"),
            gridcolor="rgba(160, 160, 160, 0.12)",
            showgrid=True,
            zeroline=False,
        ),
        width=1400,
        height=500,
    )
    fig.update_traces(
        marker=dict(color="#6C5B7B", line=dict(width=0), opacity=0.96),
        hoverlabel=dict(
            font_size=18,
            font_family="Segoe UI, sans-serif",
            bgcolor="#6C5B7B",
            font_color="#E0E0E0",
        ),
        textfont=dict(color="#ADD8E6", size=16),
    )
    return fig


# ======= FORMATADOR BR TOOLTIP =======
def tooltip_fmt_br(valor, tipo="R$"):
    if pd.isna(valor):
        return ""
    if tipo == "R$":
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    elif tipo == "%":
        return f"{valor:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")
    else:
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# =========== FUNÇÕES DE FORMATAÇÃO ===========
def format_currency_br(value):
    if pd.isna(value):
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percentage_br(value):
    if pd.isna(value):
        return "0,00%"
    return f"{value:,.2f}%".replace(",", "X").replace(".", ",").replace("X", ".")


def parse_percentage_string(percentage_str):
    if pd.isna(percentage_str) or not isinstance(percentage_str, str):
        return np.nan
    try:
        return float(percentage_str.replace("%", "").replace(".", "").replace(",", "."))
    except ValueError:
        return np.nan


# =========== CSS PREMIUM ===========

st.markdown(
    """
    <style>
    /* HEADER DATAFRAME */
    .stDataFrame th {
        background-color: #6C5B7B !important;
        color: #E0E0E0 !important;
        font-size: 1.15em !important;
        font-weight: bold !important;
        border-bottom: 2px solid #ADD8E6 !important;
    }
    .stDataFrame tbody tr:nth-child(odd) {
        background-color: #2b2c36 !important;
    }
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #23242b !important;
    }
    .stDataFrame td {
        border: 1px solid #444444 !important;
        font-size: 1.06em !important;
        color: #E0E0E0 !important;
        padding: 7px 6px !important;
    }
    .stDataFrame tbody tr:hover {
        background-color: #383953 !important;
        color: #ADD8E6 !important;
    }
    .stDataFrame thead tr th {
        position: sticky !important;
        top: 0 !important;
        z-index: 2;
    }
    /* KPIS - MÉTRICAS CHAVE */
    .kpi-metric-box {
        max-width: 100%;
        min-width: 0;
        background: linear-gradient(135deg, #383953 65%, #6C5B7B 100%);
        border: 2.5px solid #6C5B7B;
        border-radius: 22px;
        box-shadow: 0 6px 26px -12px #00000040;
        padding: 28px 30px 18px 30px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: flex-start;
        min-height: 134px;
        position: relative;
        overflow: hidden;
        margin-bottom: 22px; /* Espaçamento regular entre os cards */
        transition: box-shadow 0.25s;
    }
    .kpi-metric-box:last-child {
        margin-bottom: 0 !important; /* Remove espaço extra do último card */
    }
    .kpi-topline {
        display: flex;
        align-items: baseline;
        width: 100%;
        min-width: 0;
        margin-bottom: 6px;
    }
    .kpi-prefix {
        color: #E0E0E0;
        font-size: 1.6em;
        font-weight: bold;
        margin-right: 8px;
        flex-shrink: 0;
        white-space: nowrap;
    }
    .kpi-value {
        color: #FFF;
        font-size: 2.5em;
        font-weight: 900;
        letter-spacing: 0.02em;
        line-height: 1.03;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
        flex-shrink: 1;
    }
    .kpi-label {
        color: #99D0FA;
        font-size: 1.24em;
        font-weight: 700;
        letter-spacing: 0.02em;
        margin-top: 2px;
        margin-bottom: 0;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
        max-width: 100%;
    }
    .kpi-icon {
        position: absolute;
        top: 20px; right: 30px;
        font-size: 2.2em;
        opacity: 0.18;
        pointer-events: none;
    }
    .big-font { font-size: 3em !important; font-weight: bold; color: #E0E0E0; text-align: center; margin-bottom: 0.5em; }
    .subheader-font { font-size: 1.8em !important; font-weight: bold; color: #ADD8E6; margin-top: 1em; margin-bottom: 0.8em; }
    section[data-testid="stSidebar"] { background-color: #3A3A3A; border-right: 1px solid #555555; padding-top: 20px;}
    .centered-text { text-align: center;}
    
    /* Estilização do botão Limpar Filtros */
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: linear-gradient(135deg, #6C5B7B 0%, #ADD8E6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.9em !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(108, 91, 123, 0.3) !important;
    }

    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(108, 91, 123, 0.5) !important;
        filter: brightness(1.1) !important;
    }

    div[data-testid="stButton"] > button[kind="secondary"]:active {
        transform: translateY(0px) !important;
    }
    
    /* Estilização do dropdown de páginas */
    div[data-testid="stSelectbox"] > div > div {
        background: linear-gradient(135deg, rgba(108, 91, 123, 0.1) 0%, rgba(173, 216, 230, 0.05) 100%) !important;
        border: 1px solid rgba(173, 216, 230, 0.3) !important;
        border-radius: 10px !important;
    }

    div[data-testid="stSelectbox"] label {
        color: #ADD8E6 !important;
        font-weight: 600 !important;
        font-size: 1.1em !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# =========== CARREGAMENTO E PRÉ-PROCESSAMENTO DO ARQUIVO ESCOLHIDO ===========
df = None
filtered_df = None
if file_selected is not None:
    try:
        file_extension = file_selected.name.split(".")[-1]
        if file_extension == "csv":
            df = pd.read_csv(file_selected, sep=";", decimal=",", encoding="latin1")
        elif file_extension == "xlsx":
            df = pd.read_excel(file_selected)
        else:
            st.error(
                "Formato de arquivo não suportado. Por favor, faça o upload de um arquivo CSV ou Excel."
            )
            st.stop()
        # =========== CORREÇÃO PARA O PROBLEMA DO ARQUIVO ===========
        # 🔧 CORREÇÃO: Remove linhas que começam com "PDF:"
        if len(df.columns) > 0 and not df.empty:
            # Remove a primeira linha se for header incorreto
            first_col = df.columns[0]
            if "PDF:" in str(first_col) or df.iloc[0, 0] == "PDF:":
                df = df.iloc[1:].reset_index(drop=True)
        # 🔧 CORREÇÃO: Limpa linhas vazias ou problemáticas
        df = df.dropna(how="all")  # Remove linhas completamente vazias
        # 🔧 CORREÇÃO: Garante que todas as colunas sejam tratadas como string inicialmente
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype(str).replace("nan", "")
        # PLUGUE AQUI O CÓDIGO DE DEBUG:
        for col in [
            "data",
            "valor_bruto",
            "custo_total",
            "valor_net",
            "margem_em_valor",
            "margem_em_porcentagem",
            "qtd",
            "quantidade",
        ]:
            if col in df.columns:
                if "data" in col:
                    # Para datas
                    problemas = df[
                        pd.to_datetime(df[col], errors="coerce").isna()
                        & df[col].notna()
                    ]
                else:
                    # Para números
                    problemas = df[
                        pd.to_numeric(df[col], errors="coerce").isna() & df[col].notna()
                    ]
                if not problemas.empty:
                    st.write(f"Linhas problemáticas na coluna '{col}':")
                    st.write(problemas)
        # ======= PATCH: Conversão robusta de campos numéricos =========
        numeric_columns = [
            "valor_bruto",
            "custo_total",
            "margem_em_valor",
            "margem_em_porcentagem",
            "valor_net",
            "qtd",
            "custo_unitario",
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace("%", "", regex=False)
                    .str.replace(".", "", regex=False)
                    .str.replace(",", ".", regex=False)
                    .str.replace(" ", "")
                    .replace("", np.nan)
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")
        # Normalização dos nomes das colunas (igual seu padrão)
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("ç", "c")
            .str.replace("ã", "a")
            .str.replace("á", "a")
            .str.replace("é", "e")
            .str.replace("í", "i")
            .str.replace("ó", "o")
            .str.replace("ú", "u")
            .str.replace("â", "a")
            .str.replace("ê", "e")
            .str.replace("ô", "o")
            .str.replace("ü", "u")
            .str.replace("[^a-z0-9_]", "", regex=True)
        )
        if "representante" in df.columns:
            df = df[
                ~df["representante"]
                .astype(str)
                .str.contains("total", case=False, na=False)
            ]
        if "cliente" in df.columns:
            df = df[
                ~df["cliente"].astype(str).str.contains("total", case=False, na=False)
            ]
        colunas_numericas = [
            "valor_bruto",
            "custo_total",
            "valor_net",
            "margem_em_valor",
            "margem_em_porcentagem",
            "qtd",
            "quantidade",
        ]
        for col in colunas_numericas:
            if col in df.columns:
                df = df[pd.to_numeric(df[col], errors="coerce").notnull()]
                df[col] = pd.to_numeric(df[col], errors="coerce")
        if "valor_bruto" in df.columns:
            df = df[df["valor_bruto"].notnull()]
        column_mapping = {
            "data_venda": "data",
            "data_do_pedido": "data",
            "data_da_venda": "data",
            "valor_bruto_da_venda": "valor_bruto",
            "valor_bruto": "valor_bruto",
            "custo_total_da_venda": "custo_total",
            "custo_total": "custo_total",
            "margem_em_valor": "margem_em_valor",
            "margem_em_porcentagem": "margem_em_porcentagem",
            "representante_de_vendas": "representante",
            "nome_do_representante": "representante",
            "nome_do_cliente": "cliente",
            "produto": "descricao",
            "descricao_do_produto": "descricao",
        }
        df = df.rename(columns=column_mapping)
        # 3. ELIMINA LINHAS DE TOTAIS (não só em 'representante', mas em todas relevantes)
        for col in ["representante", "cliente", "descricao"]:
            if col in df.columns:
                df = df[
                    ~df[col]
                    .astype(str)
                    .str.lower()
                    .str.contains("total|geral|totais", na=False)
                ]
        if "data" in df.columns:
            df["data"] = pd.to_datetime(df["data"], errors="coerce")
            df.dropna(subset=["data"], inplace=True)
        # Mapeia percentuais
        if "margem_em_porcentagem" in df.columns:
            # Corrige para garantir tipo float
            df["margem_em_porcentagem"] = pd.to_numeric(
                df["margem_em_porcentagem"], errors="coerce"
            )
            # Se ainda tiver string, tenta converter
            if df["margem_em_porcentagem"].isnull().any():
                df["margem_em_porcentagem"] = df["margem_em_porcentagem"].fillna(
                    df["margem_em_porcentagem"]
                    .astype(str)
                    .apply(parse_percentage_string)
                )
            # Somente faz ajuste se for realmente float
            try:
                if (df["margem_em_porcentagem"].dropna().astype(float) < 2).all() and (
                    df["valor_bruto"].mean() > 1000
                ):
                    df["margem_em_porcentagem"] *= 100
            except Exception as err:
                st.warning(f"Erro ao ajustar margem_em_porcentagem: {err}")
        else:
            if "margem_em_valor" in df.columns and "valor_bruto" in df.columns:
                df["margem_em_porcentagem"] = (
                    (df["margem_em_valor"] / df["valor_bruto"] * 100)
                    .replace([np.inf, -np.inf], np.nan)
                    .fillna(0)
                )
            else:
                df["margem_em_porcentagem"] = 0
        required_cols = [
            "valor_bruto",
            "custo_total",
            "margem_em_valor",
            "margem_em_porcentagem",
        ]
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0

        # ===== SELETOR DE PÁGINAS NA SIDEBAR =====
        st.sidebar.markdown(
            '<p class="subheader-font" style="text-align: center; margin-bottom: 15px;">Navegação</p>',
            unsafe_allow_html=True,
        )

        pagina_selecionada = st.sidebar.selectbox(
            "Selecione a Página:",
            options=list(paginas_disponiveis.keys()),
            format_func=lambda x: paginas_disponiveis[x],
            index=list(paginas_disponiveis.keys()).index(st.session_state.pagina_atual),
            key="selector_pagina",
        )

        # Atualizar página atual
        if pagina_selecionada != st.session_state.pagina_atual:
            st.session_state.pagina_atual = pagina_selecionada
            st.rerun()

        st.sidebar.markdown("---")

        # ✅ TÍTULO DOS FILTROS (apenas para Dashboard Principal)
        st.sidebar.markdown(
        '<p class="subheader-font" style="text-align: center; margin-bottom: 20px;">Filtros de Dados</p>',
        unsafe_allow_html=True,
        )

        # ✅ BOTÃO LIMPAR FILTROS CENTRALIZADO
        col1, col2, col3 = st.sidebar.columns([1, 3, 1])
        with col2:
            if st.button(
                "🔄 Limpar Filtros",
                key="clear_filters",
                help="Restaura todos os filtros para o estado original",
            ):
                # Limpar todos os filtros salvos
                keys_to_clear = [
                    "saved_date_range",
                    "saved_tp_mov",
                    "saved_representantes",
                    "saved_clientes",
                    "saved_produtos",
                    "filter_key_suffix",
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]

                # Gerar novo sufixo para forçar reset dos widgets
                import random

                st.session_state.filter_key_suffix = str(random.randint(1000, 9999))

                # Flag para indicar que filtros foram limpos
                st.session_state.filters_cleared = True

                # Rerun para aplicar as mudanças
                st.rerun()

        # Mostrar feedback se filtros foram limpos (com espaçamento reduzido)
        if st.session_state.get("filters_cleared", False):
            st.sidebar.success("✅ Filtros restaurados!")
            # Limpar a flag após mostrar a mensagem
            st.session_state.filters_cleared = False

        # ✅ ESPAÇAMENTO MAIOR ANTES DA LINHA DIVISÓRIA
        st.sidebar.markdown(
            """
            <div style="margin-top: 20px; margin-bottom: 10px;">
                <hr style="border: 0; border-top: 1px solid #444444; margin: 0;">
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Flag para saber se acabou de voltar da apresentação
        just_returned = st.session_state.get("just_returned_from_presentation", False)
        if just_returned:
            st.session_state.just_returned_from_presentation = False  # Reset imediato

        # Filtro por Data
        if "data" in df.columns and not df["data"].empty:
            min_date = df["data"].min().to_pydatetime().date()
            max_date = df["data"].max().to_pydatetime().date()

            # Só usar valores salvos se acabou de voltar
            if just_returned and "saved_date_range" in st.session_state:
                default_date = st.session_state.saved_date_range
            else:
                default_date = (min_date, max_date)

            date_range = st.sidebar.date_input(
                "Selecione o período:",
                value=default_date,
                min_value=min_date,
                max_value=max_date,
                key=f"date_filter_{st.session_state.get('filter_key_suffix', '')}",
            )

            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_df = df[
                    (df["data"].dt.date >= start_date)
                    & (df["data"].dt.date <= end_date)
                ]
                # Sempre salvar para a próxima volta da apresentação
                if not just_returned:  # Só salvar se não acabou de voltar
                    st.session_state.saved_date_range = date_range
            else:
                filtered_df = df.copy()
        else:
            filtered_df = df.copy()
            st.sidebar.info(
                "Coluna 'data' não encontrada ou vazia para aplicar filtro de data."
            )

        # ✅ FILTRO: TP MOV
        if "tp_mov" in filtered_df.columns and not filtered_df["tp_mov"].empty:
            all_tp_mov = sorted(filtered_df["tp_mov"].unique().tolist())

            if just_returned and "saved_tp_mov" in st.session_state:
                default_tp_mov = [
                    x for x in st.session_state.saved_tp_mov if x in all_tp_mov
                ]
                if not default_tp_mov:
                    default_tp_mov = all_tp_mov
            else:
                default_tp_mov = all_tp_mov

            selected_tp_mov = st.sidebar.multiselect(
                "Selecione o Tipo de Movimento:",
                options=all_tp_mov,
                default=default_tp_mov,
                key=f"tp_mov_filter_{st.session_state.get('filter_key_suffix', '')}",
            )

            if selected_tp_mov:
                filtered_df = filtered_df[filtered_df["tp_mov"].isin(selected_tp_mov)]
            if not just_returned:
                st.session_state.saved_tp_mov = selected_tp_mov
        else:
            st.sidebar.info(
                "Coluna 'tp_mov' não encontrada ou vazia para aplicar filtro."
            )

        # Filtro por Representante (multi)
        if (
            "representante" in filtered_df.columns
            and not filtered_df["representante"].empty
        ):
            all_representantes = sorted(filtered_df["representante"].unique().tolist())

            if just_returned and "saved_representantes" in st.session_state:
                default_representantes = [
                    x
                    for x in st.session_state.saved_representantes
                    if x in all_representantes
                ]
                if not default_representantes:
                    default_representantes = all_representantes
            else:
                default_representantes = all_representantes

            selected_representantes = st.sidebar.multiselect(
                "Selecione o(s) Representante(s):",
                options=all_representantes,
                default=default_representantes,
                key=f"representante_filter_{st.session_state.get('filter_key_suffix', '')}",
            )

            if selected_representantes:
                filtered_df = filtered_df[
                    filtered_df["representante"].isin(selected_representantes)
                ]
            if not just_returned:
                st.session_state.saved_representantes = selected_representantes
        else:
            st.sidebar.info(
                "Coluna 'representante' não encontrada ou vazia para aplicar filtro."
            )

        # Filtro por Cliente (multi)
        if "cliente" in filtered_df.columns and not filtered_df["cliente"].empty:
            all_clientes = sorted(filtered_df["cliente"].unique().tolist())

            if just_returned and "saved_clientes" in st.session_state:
                default_clientes = [
                    x for x in st.session_state.saved_clientes if x in all_clientes
                ]
                if not default_clientes:
                    default_clientes = all_clientes
            else:
                default_clientes = all_clientes

            selected_clientes = st.sidebar.multiselect(
                "Selecione o(s) Cliente(s):",
                options=all_clientes,
                default=default_clientes,
                key=f"cliente_filter_{st.session_state.get('filter_key_suffix', '')}",
            )

            if selected_clientes:
                filtered_df = filtered_df[
                    filtered_df["cliente"].isin(selected_clientes)
                ]
            if not just_returned:
                st.session_state.saved_clientes = selected_clientes
        else:
            st.sidebar.info(
                "Coluna 'cliente' não encontrada ou vazia para aplicar filtro."
            )

        # Filtro por Produto (multi)
        if "descricao" in filtered_df.columns and not filtered_df["descricao"].empty:
            all_produtos = sorted(filtered_df["descricao"].unique().tolist())

            if just_returned and "saved_produtos" in st.session_state:
                default_produtos = [
                    x for x in st.session_state.saved_produtos if x in all_produtos
                ]
                if not default_produtos:
                    default_produtos = all_produtos
            else:
                default_produtos = all_produtos

            selected_produtos = st.sidebar.multiselect(
                "Selecione o(s) Produto(s):",
                options=all_produtos,
                default=default_produtos,
                key=f"produto_filter_{st.session_state.get('filter_key_suffix', '')}",
            )

            if selected_produtos:
                filtered_df = filtered_df[
                    filtered_df["descricao"].isin(selected_produtos)
                ]
            if not just_returned:
                st.session_state.saved_produtos = selected_produtos
        else:
            st.sidebar.info(
                "Coluna 'descricao' não encontrada ou vazia para aplicar filtro."
            )
            
            # ✅ CRIAR COLUNA MES_ANO LOGO APÓS OS FILTROS
        if 'data' in filtered_df.columns:
            filtered_df['mes_ano'] = filtered_df['data'].dt.to_period('M').astype(str)

        st.divider()
    except Exception as e:
        st.error(
            f"Ocorreu um erro ao processar o arquivo: {e}. Por favor, verifique o formato e o conteúdo do arquivo."
        )
        st.stop()

    # ===== ESTRUTURA PRINCIPAL BASEADA NA PÁGINA SELECIONADA =====
    if st.session_state.pagina_atual == "Dashboard Principal":

            #=========== EXIBIÇÃO DA TABELA ===========
            if file_selected is not None and 'filtered_df' in locals() and not filtered_df.empty:
                
                df_display = filtered_df.copy()
                # Dicionário de nomes amigáveis para todas as colunas (incluindo as novas)
                display_column_names = {
                    "tp_mov": "TP Mov",
                    "nf": "NF",
                    "data": "Data da Venda",
                    "cliente": "Cliente",
                    "segmentacao": "Segmentação",
                    "representante": "Representante",
                    "cod_produto": "Cód. Produto",
                    "descricao": "Descrição do Produto",
                    "valor_bruto": "Faturamento Bruto",
                    "valor_net": "Valor Net",
                    "qtd": "Quantidade",
                    "custo_unitario": "Custo Unitário",
                    "custo_total": "Custo Total",
                    "margem_em_valor": "Margem em Valor",
                    "margem_em_porcentagem": "Margem (%)",
                }
                # Renomeia apenas colunas existentes no DataFrame
                df_display = df_display.rename(
                    columns={
                        k: v for k, v in display_column_names.items() if k in df_display.columns
                    }
                )
                # Alinha Quantidade para inteiro à direita
                if "Quantidade" in df_display.columns:
                    df_display["Quantidade"] = (
                        df_display["Quantidade"].fillna(0).astype(float).round(0).astype(int)
                    )
                format_dict = {
                    "Faturamento Bruto": lambda x: (
                        format_currency_br(x) if pd.notna(x) else "R$ 0,00"
                    ),
                    "Valor Net": lambda x: format_currency_br(x) if pd.notna(x) else "R$ 0,00",
                    "Custo Total": lambda x: format_currency_br(x) if pd.notna(x) else "R$ 0,00",
                    "Custo Unitário": lambda x: format_currency_br(x) if pd.notna(x) else "R$ 0,00",
                    "Margem em Valor": lambda x: (
                        format_currency_br(x) if pd.notna(x) else "R$ 0,00"
                    ),
                    "Margem (%)": lambda x: format_percentage_br(x) if pd.notna(x) else "0,00%",
                }
                final_format_dict = {
                    col: fmt for col, fmt in format_dict.items() if col in df_display.columns
                }
                # Ajustes NF e Data
                if "NF" in df_display.columns:
                    try:
                        df_display["NF"] = (
                            df_display["NF"].astype(float).astype(pd.Int64Dtype()).astype(str)
                        )
                    except:
                        pass
                if "Data da Venda" in df_display.columns:
                    try:
                        df_display["Data da Venda"] = pd.to_datetime(
                            df_display["Data da Venda"], errors="coerce"
                        ).dt.strftime("%d/%m/%Y")
                    except:
                        pass
                # EXIBIÇÃO COM ALINHAMENTO: Números sempre à direita
                styler = df_display.style.format(final_format_dict)
                if "Quantidade" in df_display.columns:
                    styler = styler.set_properties(subset=["Quantidade"], **{"text-align": "right"})
                st.dataframe(styler, use_container_width=True)
                st.divider()
                # =========== MÉTRICAS CHAVE VISUAL PREMIUM ===========
            
                st.markdown('<p class="subheader-font">Métricas Chave</p>', unsafe_allow_html=True)
                total_valor_bruto = (
                    filtered_df["valor_bruto"].sum() if "valor_bruto" in filtered_df.columns else 0
                )
                total_custo_total = (
                    filtered_df["custo_total"].sum() if "custo_total" in filtered_df.columns else 0
                )
                total_valor_net = (
                    filtered_df["valor_net"].sum() if "valor_net" in filtered_df.columns else 0
                )
                total_margem_valor = (
                    filtered_df["margem_em_valor"].sum()
                    if "margem_em_valor" in filtered_df.columns
                    else 0
                )
                # NOVO CÁLCULO DA MARGEM MÉDIA (%) – cálculo correto, conforme book de melhores práticas
                if total_valor_net > 0:
                    nova_margem_media = (
                        (total_valor_net - total_custo_total) / total_valor_net * 100
                    )
                else:
                    nova_margem_media = 0
                st.markdown(
                    f"""
                <div class="kpi-metric-box">
                    <div class="kpi-topline">
                        <span class="kpi-prefix">R$</span>
                        <span class="kpi-value">{format_currency_br(total_valor_bruto)[3:]}</span>
                    </div>
                    <div class="kpi-label">Faturamento Bruto</div>
                    <div class="kpi-icon">💸</div>
                </div>
                <div class="kpi-metric-box">
                    <div class="kpi-topline">
                        <span class="kpi-prefix">R$</span>
                        <span class="kpi-value">{format_currency_br(total_custo_total)[3:]}</span>
                    </div>
                    <div class="kpi-label">Custo Total</div>
                    <div class="kpi-icon">🧾</div>
                </div>
                <div class="kpi-metric-box">
                    <div class="kpi-topline">
                        <span class="kpi-prefix">R$</span>
                        <span class="kpi-value">{format_currency_br(total_valor_net)[3:]}</span>
                    </div>
                    <div class="kpi-label">Valor NET Total</div>
                    <div class="kpi-icon">💳</div>
                </div>
                <div class="kpi-metric-box">
                    <div class="kpi-topline">
                        <span class="kpi-prefix">R$</span>
                        <span class="kpi-value">{format_currency_br(total_margem_valor)[3:]}</span>
                    </div>
                    <div class="kpi-label">Margem em Valor</div>
                    <div class="kpi-icon">📈</div>
                </div>
                <div class="kpi-metric-box">
                    <div class="kpi-topline">
                        <span class="kpi-value">{format_percentage_br(nova_margem_media)}</span>
                    </div>
                    <div class="kpi-label">Margem Bruta (%)</div>
                    <div class="kpi-icon">💹</div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.divider()
                
                # =========== GRÁFICOS COM TOOLTIPS FORMATADOS BR ===========
                st.markdown('<p class="subheader-font">Análise Gráfica</p>', unsafe_allow_html=True)

                # Margem por Representante
                st.markdown("#### Margem por Representante")
                if (
                    "representante" in filtered_df.columns
                    and "margem_em_valor" in filtered_df.columns
                    and "valor_net" in filtered_df.columns
                    and "custo_total" in filtered_df.columns
                ):
                    df_rep_margem = (
                        filtered_df.groupby("representante")
                        .agg(
                            valor_net=("valor_net", "sum"),
                            custo_total=("custo_total", "sum"),
                            margem_em_valor=("margem_em_valor", "sum"),
                        )
                        .reset_index()
                    )
                    # ✅ NOVA FÓRMULA DA MARGEM %
                    df_rep_margem["margem_em_porcentagem"] = df_rep_margem.apply(
                        lambda row: calcular_margem_percentual(
                            row["valor_net"], row["custo_total"]
                        ),
                        axis=1,
                    )
                    df_rep_margem = df_rep_margem.sort_values("margem_em_valor", ascending=False)
                    # ✅ FORMATAÇÃO DOS NOVOS CAMPOS
                    df_rep_margem["valor_net_fmt"] = df_rep_margem["valor_net"].apply(
                        tooltip_fmt_br
                    )
                    df_rep_margem["custo_total_fmt"] = df_rep_margem["custo_total"].apply(
                        tooltip_fmt_br
                    )
                    df_rep_margem["margem_valor_fmt"] = df_rep_margem["margem_em_valor"].apply(
                        tooltip_fmt_br
                    )
                    df_rep_margem["margem_perc_fmt"] = df_rep_margem["margem_em_porcentagem"].apply(
                        lambda x: f"{x:.2f}%"
                    )
                    fig_rep_margem = px.bar(
                        df_rep_margem,
                        x="representante",
                        y="margem_em_valor",
                        text_auto=".2s",
                        labels={
                            "margem_em_valor": "Margem em Valor (R$)",
                            "representante": "Representante",
                        },
                        custom_data=[
                            "valor_net_fmt",
                            "custo_total_fmt",
                            "margem_valor_fmt",
                            "margem_perc_fmt",
                        ],
                    )
                    # ✅ NOVO TEMPLATE DO TOOLTIP
                    fig_rep_margem.update_traces(
                        hovertemplate="<b>Representante:</b> %{x}<br>"
                        + "<b>Valor NET Total (R$):</b> %{customdata[0]}<br>"
                        + "<b>Custo Total (R$):</b> %{customdata[1]}<br>"
                        + "<b>Margem em Valor (R$):</b> %{customdata[2]}<br>"
                        + "<b>Margem (%):</b> %{customdata[3]}<extra></extra>"
                    )
                    fig_rep_margem = apply_integrated_layout(
                        fig_rep_margem, title="Margem por Representante"
                    )
                    st.plotly_chart(fig_rep_margem, use_container_width=True)
                else:
                    st.info("Colunas necessárias não encontradas para o gráfico de Representantes.")

                # Participação por Representante (Gráfico de Barras com Toggle)
                st.markdown("#### Participação por Representante")
                if (
                    "representante" in filtered_df.columns
                    and "valor_net" in filtered_df.columns
                    and "valor_bruto" in filtered_df.columns
                ):
                    # Calcular participação por representante
                    df_participacao_rep = (
                        filtered_df.groupby("representante")
                        .agg(valor_net=("valor_net", "sum"), valor_bruto=("valor_bruto", "sum"))
                        .reset_index()
                    )

                    # Calcular totais
                    valor_net_total = df_participacao_rep["valor_net"].sum()
                    faturamento_bruto_total = df_participacao_rep["valor_bruto"].sum()

                    # Calcular ambos os percentuais
                    df_participacao_rep["participacao_net"] = (
                        df_participacao_rep["valor_net"] / valor_net_total * 100
                    )
                    df_participacao_rep["participacao_bruto"] = (
                        df_participacao_rep["valor_bruto"] / faturamento_bruto_total * 100
                    )

                    # Ordenar por valor_net decrescente
                    df_participacao_rep = df_participacao_rep.sort_values(
                        "valor_net", ascending=False
                    )

                    # ✅ BOTÃO DE ALTERNÂNCIA CENTRALIZADO COM ESPAÇAMENTO REDUZIDO

                    # Centralizar os botões radio
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        metrica_selecionada = st.radio(
                            "",  # Label vazio já que colocamos acima
                            options=["Valor NET", "Faturamento Bruto"],
                            horizontal=True,
                            key="toggle_participacao",
                            label_visibility="collapsed",  # Esconde o label padrão
                        )

                    # Definir dados baseados na seleção
                    if metrica_selecionada == "Valor NET":
                        y_column = "participacao_net"
                        y_label = "Participação por Valor NET (%)"
                        titulo_grafico = "Participação por Representante - Valor NET"
                        total_referencia = valor_net_total
                        valor_referencia_col = "valor_net"
                    else:
                        y_column = "participacao_bruto"
                        y_label = "Participação por Faturamento Bruto (%)"
                        titulo_grafico = "Participação por Representante - Faturamento Bruto"
                        total_referencia = faturamento_bruto_total
                        valor_referencia_col = "valor_bruto"

                    # Formatação para tooltips
                    df_participacao_rep["valor_net_fmt"] = df_participacao_rep["valor_net"].apply(
                        tooltip_fmt_br
                    )
                    df_participacao_rep["valor_bruto_fmt"] = df_participacao_rep[
                        "valor_bruto"
                    ].apply(tooltip_fmt_br)
                    df_participacao_rep["participacao_net_fmt"] = df_participacao_rep[
                        "participacao_net"
                    ].apply(lambda x: f"{x:.2f}%")
                    df_participacao_rep["participacao_bruto_fmt"] = df_participacao_rep[
                        "participacao_bruto"
                    ].apply(lambda x: f"{x:.2f}%")
                    total_referencia_fmt = tooltip_fmt_br(total_referencia)

                    # Criar gráfico de barras verticais
                    fig_participacao_rep = px.bar(
                        df_participacao_rep,
                        x="representante",
                        y=y_column,
                        text_auto=".1f",
                        labels={y_column: y_label, "representante": "Representante"},
                        custom_data=[
                            "valor_net_fmt",
                            "valor_bruto_fmt",
                            "participacao_net_fmt",
                            "participacao_bruto_fmt",
                        ],
                    )

                    # Template de tooltip dinâmico
                    if metrica_selecionada == "Valor NET":
                        hovertemplate = (
                            "<b>Representante:</b> %{x}<br>"
                            + "<b>Valor NET:</b> %{customdata[0]}<br>"
                            + "<b>Participação NET:</b> %{customdata[2]}<br>"
                            + f"<b>Valor NET Total:</b> {total_referencia_fmt}<br>"
                            + "<extra></extra>"
                        )
                    else:
                        hovertemplate = (
                            "<b>Representante:</b> %{x}<br>"
                            + "<b>Faturamento Bruto:</b> %{customdata[1]}<br>"
                            + "<b>Participação Bruto:</b> %{customdata[3]}<br>"
                            + f"<b>Faturamento Bruto Total:</b> {total_referencia_fmt}<br>"
                            + "<extra></extra>"
                        )

                    # Aplicar template de tooltip personalizado
                    fig_participacao_rep.update_traces(
                        hovertemplate=hovertemplate,
                        texttemplate="%{y:.1f}%",
                        textposition="auto",
                        marker=dict(color="#6C5B7B", line=dict(width=0), opacity=0.96),
                        textfont=dict(color="#ADD8E6", size=16),
                        hoverlabel=dict(
                            font_size=18,
                            font_family="Segoe UI, sans-serif",
                            bgcolor="#6C5B7B",
                            font_color="#E0E0E0",
                            align="left",
                        ),
                    )

                    # Aplicar layout integrado
                    fig_participacao_rep = apply_integrated_layout(
                        fig_participacao_rep, title=titulo_grafico
                    )

                    st.plotly_chart(fig_participacao_rep, use_container_width=True)
                else:
                    st.info(
                        "Colunas necessárias não encontradas para o gráfico de Participação por Representante."
                    )

                # Margem por Cliente (Top 10)
                st.markdown("#### Margem por Cliente")
                if (
                    "cliente" in filtered_df.columns
                    and "margem_em_valor" in filtered_df.columns
                    and "valor_net" in filtered_df.columns
                    and "custo_total" in filtered_df.columns
                ):
                    df_cliente_margem = (
                        filtered_df.groupby("cliente")
                        .agg(
                            valor_net=("valor_net", "sum"),
                            custo_total=("custo_total", "sum"),
                            margem_em_valor=("margem_em_valor", "sum"),
                        )
                        .reset_index()
                    )
                    # ✅ NOVA FÓRMULA DA MARGEM %
                    df_cliente_margem["margem_em_porcentagem"] = df_cliente_margem.apply(
                        lambda row: calcular_margem_percentual(
                            row["valor_net"], row["custo_total"]
                        ),
                        axis=1,
                    )
                    df_cliente_margem = df_cliente_margem.sort_values(
                        "margem_em_valor", ascending=False
                    ).head(10)
                    # ✅ FORMATAÇÃO DOS NOVOS CAMPOS
                    df_cliente_margem["valor_net_fmt"] = df_cliente_margem["valor_net"].apply(
                        tooltip_fmt_br
                    )
                    df_cliente_margem["custo_total_fmt"] = df_cliente_margem["custo_total"].apply(
                        tooltip_fmt_br
                    )
                    df_cliente_margem["margem_valor_fmt"] = df_cliente_margem[
                        "margem_em_valor"
                    ].apply(tooltip_fmt_br)
                    df_cliente_margem["margem_perc_fmt"] = df_cliente_margem[
                        "margem_em_porcentagem"
                    ].apply(lambda x: f"{x:.2f}%")
                    # ✅ TRUNCAR NOMES DOS CLIENTES PARA MELHOR VISUALIZAÇÃO
                    df_cliente_margem["cliente_display"] = df_cliente_margem["cliente"].apply(
                        lambda x: x[:50] + "..." if len(x) > 50 else x
                    )
                    fig_cliente_margem = px.bar(
                        df_cliente_margem,
                        x="cliente_display",
                        y="margem_em_valor",
                        text_auto=".2s",
                        labels={
                            "margem_em_valor": "Margem em Valor (R$)",
                            "cliente_display": "Cliente",
                        },
                        custom_data=[
                            "valor_net_fmt",
                            "custo_total_fmt",
                            "margem_valor_fmt",
                            "margem_perc_fmt",
                        ],
                    )
                    # ✅ NOVO TEMPLATE DO TOOLTIP
                    fig_cliente_margem.update_traces(
                        hovertemplate="<b>Cliente:</b> %{x}<br>"
                        + "<b>Valor NET Total (R$):</b> %{customdata[0]}<br>"
                        + "<b>Custo Total (R$):</b> %{customdata[1]}<br>"
                        + "<b>Margem em Valor (R$):</b> %{customdata[2]}<br>"
                        + "<b>Margem (%):</b> %{customdata[3]}<extra></extra>"
                    )
                    # ✅ APLICAR LAYOUT PADRÃO (igual aos outros gráficos)
                    fig_cliente_margem = apply_integrated_layout(
                        fig_cliente_margem, title="Top 10 Clientes por Margem Total"
                    )
                    # ✅ APENAS CONFIGURAÇÕES MÍNIMAS ESPECÍFICAS PARA CLIENTES
                    fig_cliente_margem.update_layout(
                        height=600,  # Manter altura maior por causa dos nomes longos
                        margin=dict(l=80, r=50, t=80, b=150),  # Margem embaixo para os nomes
                    )
                    # ✅ EIXOS COM TAMANHOS PADRÃO (mesmos dos outros gráficos)
                    fig_cliente_margem.update_xaxes(
                        tickangle=-45,
                        # ✅ SEM override de font - usar padrão do apply_integrated_layout
                    )
                    st.plotly_chart(fig_cliente_margem, use_container_width=True)
                else:
                    st.info("Colunas necessárias não encontradas para o gráfico de Clientes.")

                # Margem Total Mensal com Representantes
                st.markdown("#### Margem Total Mensal")
                if (
                    "data" in filtered_df.columns
                    and "margem_em_valor" in filtered_df.columns
                    and "valor_net" in filtered_df.columns
                    and "custo_total" in filtered_df.columns
                    and "representante" in filtered_df.columns
                ):
                    

                    # ✅ DADOS DO TOTAL GERAL (linha principal)
                    df_mensal_total = (
                        filtered_df.groupby("mes_ano")
                        .agg(
                            valor_net=("valor_net", "sum"),
                            custo_total=("custo_total", "sum"),
                            margem_em_valor=("margem_em_valor", "sum"),
                        )
                        .reset_index()
                    )

                    # ✅ DADOS POR REPRESENTANTE (linhas individuais)
                    df_mensal_representantes = (
                        filtered_df.groupby(["mes_ano", "representante"])
                        .agg(
                            valor_net=("valor_net", "sum"),
                            custo_total=("custo_total", "sum"),
                            margem_em_valor=("margem_em_valor", "sum"),
                        )
                        .reset_index()
                    )

                    # ✅ NOVA FÓRMULA DA MARGEM % (para ambos)
                    df_mensal_total["margem_em_porcentagem"] = df_mensal_total.apply(
                        lambda row: calcular_margem_percentual(
                            row["valor_net"], row["custo_total"]
                        ),
                        axis=1,
                    )
                    df_mensal_representantes["margem_em_porcentagem"] = (
                        df_mensal_representantes.apply(
                            lambda row: calcular_margem_percentual(
                                row["valor_net"], row["custo_total"]
                            ),
                            axis=1,
                        )
                    )

                    # Ordenar por data
                    df_mensal_total = df_mensal_total.sort_values("mes_ano")
                    df_mensal_representantes = df_mensal_representantes.sort_values("mes_ano")

                    # ✅ CRIAR GRÁFICO COM MÚLTIPLAS LINHAS
                    fig_mensal_multi = go.Figure()

                    # ✅ LINHA DO TOTAL (mais destacada)
                    df_mensal_total["valor_net_fmt"] = df_mensal_total["valor_net"].apply(
                        tooltip_fmt_br
                    )
                    df_mensal_total["custo_total_fmt"] = df_mensal_total["custo_total"].apply(
                        tooltip_fmt_br
                    )
                    df_mensal_total["margem_valor_fmt"] = df_mensal_total["margem_em_valor"].apply(
                        tooltip_fmt_br
                    )
                    df_mensal_total["margem_perc_fmt"] = df_mensal_total[
                        "margem_em_porcentagem"
                    ].apply(lambda x: f"{x:.2f}%")

                    fig_mensal_multi.add_trace(
                        go.Scatter(
                            x=df_mensal_total["mes_ano"],
                            y=df_mensal_total["margem_em_valor"],
                            mode="lines+markers",
                            name="📊 TOTAL GERAL",
                            line=dict(width=4, color="#ADD8E6"),
                            marker=dict(size=10, color="#ADD8E6"),
                            customdata=list(
                                zip(
                                    df_mensal_total["valor_net_fmt"],
                                    df_mensal_total["custo_total_fmt"],
                                    df_mensal_total["margem_valor_fmt"],
                                    df_mensal_total["margem_perc_fmt"],
                                )
                            ),
                            hovertemplate=(
                                "<b>📊 TOTAL GERAL</b><br>"
                                + "<b>Mês/Ano:</b> %{x}<br>"
                                + "<b>Valor NET Total:</b> %{customdata[0]}<br>"
                                + "<b>Custo Total:</b> %{customdata[1]}<br>"
                                + "<b>Margem em Valor:</b> %{customdata[2]}<br>"
                                + "<b>Margem (%):</b> %{customdata[3]}<extra></extra>"
                            ),
                            visible=True,  # Sempre visível por padrão
                        )
                    )

                    # ✅ LINHAS DOS REPRESENTANTES (cores diferentes)
                    cores_representantes = [
                        "#6C5B7B",
                        "#FF6B6B",
                        "#4ECDC4",
                        "#45B7D1",
                        "#96CEB4",
                        "#FFEAA7",
                        "#DDA0DD",
                        "#98D8C8",
                        "#F7DC6F",
                        "#BB8FCE",
                        "#85C1E9",
                        "#F8C471",
                        "#82E0AA",
                        "#F1948A",
                        "#D7BDE2",
                    ]

                    representantes_unicos = sorted(
                        df_mensal_representantes["representante"].unique()
                    )

                    for i, rep in enumerate(representantes_unicos):
                        df_rep = df_mensal_representantes[
                            df_mensal_representantes["representante"] == rep
                        ].copy()

                        # Formatação para tooltips
                        df_rep["valor_net_fmt"] = df_rep["valor_net"].apply(tooltip_fmt_br)
                        df_rep["custo_total_fmt"] = df_rep["custo_total"].apply(tooltip_fmt_br)
                        df_rep["margem_valor_fmt"] = df_rep["margem_em_valor"].apply(tooltip_fmt_br)
                        df_rep["margem_perc_fmt"] = df_rep["margem_em_porcentagem"].apply(
                            lambda x: f"{x:.2f}%"
                        )

                        cor = cores_representantes[i % len(cores_representantes)]

                        # ✅ NOME COM QUEBRA DE LINHA PARA A LEGENDA
                        nome_quebrado = quebrar_nome_legenda(rep, max_chars=25)

                        fig_mensal_multi.add_trace(
                            go.Scatter(
                                x=df_rep["mes_ano"],
                                y=df_rep["margem_em_valor"],
                                mode="lines+markers",
                                name=f"👤 {nome_quebrado}",  # ✅ NOME QUEBRADO
                                line=dict(width=2.5, color=cor),
                                marker=dict(size=6, color=cor),
                                customdata=list(
                                    zip(
                                        df_rep["valor_net_fmt"],
                                        df_rep["custo_total_fmt"],
                                        df_rep["margem_valor_fmt"],
                                        df_rep["margem_perc_fmt"],
                                    )
                                ),
                                hovertemplate=(
                                    f"<b>👤 {rep}</b><br>"  # ✅ TOOLTIP COM NOME ORIGINAL (sem quebra)
                                    + "<b>Mês/Ano:</b> %{x}<br>"
                                    + "<b>Valor NET Total:</b> %{customdata[0]}<br>"
                                    + "<b>Custo Total:</b> %{customdata[1]}<br>"
                                    + "<b>Margem em Valor:</b> %{customdata[2]}<br>"
                                    + "<b>Margem (%):</b> %{customdata[3]}<extra></extra>"
                                ),
                                visible="legendonly",  # Oculto por padrão, mas pode ser ativado na legenda
                            )
                        )

                    # ✅ APLICAR LAYOUT COM LEGENDA VERTICAL EXTERNA E NOMES QUEBRADOS
                    fig_mensal_multi.update_layout(
                        title={
                            "text": "Evolução da Margem Mensal por Representante",
                            "y": 0.93,
                            "x": 0.5,
                            "xanchor": "center",
                            "yanchor": "top",
                            "font": {
                                "size": 30,
                                "color": "#ADD8E6",
                                "family": "Segoe UI, sans-serif",
                            },
                        },
                        font=dict(family="Segoe UI, sans-serif", size=18, color="#E0E0E0"),
                        plot_bgcolor="#22232B",
                        paper_bgcolor="#22232B",
                        legend=dict(
                            orientation="v",  # ✅ VERTICAL (uma embaixo da outra)
                            yanchor="middle",  # Centralizada verticalmente
                            y=0.5,
                            xanchor="left",
                            x=1.02,  # ✅ FORA DO GRÁFICO (à direita)
                            font=dict(size=13, color="#ADD8E6"),  # Fonte um pouco maior
                            bgcolor="rgba(34, 35, 43, 0.95)",
                            bordercolor="#6C5B7B",
                            borderwidth=1,
                            itemwidth=30,  # Símbolos menores para economizar espaço
                            itemsizing="constant",
                            traceorder="normal",
                            tracegroupgap=5,  # Espaçamento menor entre itens
                            itemclick="toggle",
                            itemdoubleclick="toggleothers",
                        ),
                        margin=dict(l=40, r=90, t=70, b=40),  # ✅ MARGEM DIREITA OTIMIZADA (menor)
                        xaxis=dict(
                            title="Mês/Ano",
                            title_font=dict(
                                size=20, color="#ADD8E6", family="Segoe UI, sans-serif"
                            ),
                            tickfont=dict(size=16, color="#E0E0E0"),
                            gridcolor="rgba(160, 160, 160, 0.15)",
                            showgrid=True,
                            zeroline=False,
                            tickangle=-45,
                            domain=[0, 1],  # ✅ LARGURA TOTAL DISPONÍVEL
                        ),
                        yaxis=dict(
                            title="Margem em Valor (R$)",
                            title_font=dict(
                                size=20, color="#ADD8E6", family="Segoe UI, sans-serif"
                            ),
                            tickfont=dict(size=16, color="#E0E0E0"),
                            gridcolor="rgba(160, 160, 160, 0.12)",
                            showgrid=True,
                            zeroline=False,
                            domain=[0, 1],  # ✅ ALTURA TOTAL DISPONÍVEL
                        ),
                        width=1400,
                        height=500,  # ✅ ALTURA NORMAL
                        hoverlabel=dict(
                            font_size=18,
                            font_family="Segoe UI, sans-serif",
                            bgcolor="#6C5B7B",
                            font_color="#E0E0E0",
                        ),
                    )

                    st.plotly_chart(fig_mensal_multi, use_container_width=True)
                else:
                    st.info("Colunas necessárias não encontradas para o gráfico mensal.")

                # Margem por Produto com Toggle
                st.markdown("### Análise por Produto")
                if (
                    "descricao" in filtered_df.columns
                    and "margem_em_valor" in filtered_df.columns
                    and "qtd" in filtered_df.columns
                ):
                    # ✨ CSS LIMPO E FUNCIONAL
                    st.markdown(
                        """
                    <style>
                    /* Estilização do slider */
                    div[data-testid="stSlider"] {
                        background: linear-gradient(135deg, rgba(108, 91, 123, 0.1) 0%, rgba(173, 216, 230, 0.05) 100%);
                        border: 1px solid rgba(173, 216, 230, 0.2);
                        border-radius: 15px;
                        padding: 20px;
                        margin: 15px 0;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    }
                    /* Track do slider */
                    div[data-testid="stSlider"] .stSlider > div > div > div > div {
                        background: linear-gradient(90deg, #6C5B7B 0%, #ADD8E6 100%) !important;
                        height: 10px !important;
                        border-radius: 10px !important;
                    }
                    /* Thumb do slider */
                    div[data-testid="stSlider"] .stSlider > div > div > div > div > div {
                        background: linear-gradient(135deg, #ADD8E6 0%, #6C5B7B 100%) !important;
                        border: 3px solid #ffffff !important;
                        width: 24px !important;
                        height: 24px !important;
                        border-radius: 50% !important;
                        box-shadow: 0 4px 12px rgba(108, 91, 123, 0.4) !important;
                        transition: all 0.3s ease !important;
                    }
                    /* Hover effect */
                    div[data-testid="stSlider"] .stSlider > div > div > div > div > div:hover {
                        transform: scale(1.2) !important;
                        box-shadow: 0 6px 16px rgba(108, 91, 123, 0.6) !important;
                    }
                    /* Label do slider */
                    div[data-testid="stSlider"] .stSlider > label {
                        color: #ADD8E6 !important;
                        font-weight: 600 !important;
                        font-size: 1.2em !important;
                        text-align: center !important;
                        display: block !important;
                        margin-bottom: 15px !important;
                    }
                    </style>
                    """,
                        unsafe_allow_html=True,
                    )

                    # SLIDER PARA NÚMERO DE PRODUTOS
                    num_products = st.slider(
                        "🎚️ Selecione a Quantidade de Produtos",
                        min_value=2,
                        max_value=30,
                        value=10,
                        step=1,
                        help="Deslize para escolher quantos produtos mostrar no gráfico",
                    )

                    # ✅ BOTÃO DE ALTERNÂNCIA PARA PRODUTOS
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        metrica_produto = st.radio(
                            "",
                            options=["Margem Total", "Quantidade Total"],
                            horizontal=True,
                            key="toggle_produtos",
                            label_visibility="collapsed",
                        )

                    # Agrupar dados por produto
                    df_prod_analise = (
                        filtered_df.groupby("descricao")
                        .agg(
                            valor_net=("valor_net", "sum"),
                            custo_total=("custo_total", "sum"),
                            margem_em_valor=("margem_em_valor", "sum"),
                            qtd=("qtd", "sum"),
                        )
                        .reset_index()
                    )

                    # ✅ NOVA FÓRMULA DA MARGEM %
                    df_prod_analise["margem_em_porcentagem"] = df_prod_analise.apply(
                        lambda row: calcular_margem_percentual(
                            row["valor_net"], row["custo_total"]
                        ),
                        axis=1,
                    )

                    # Definir dados baseados na seleção
                    if metrica_produto == "Margem Total":
                        y_column = "margem_em_valor"
                        y_label = "Margem em Valor (R$)"
                        titulo_grafico = f"Top {num_products} Produtos por Margem Total"
                        sort_column = "margem_em_valor"
                        text_format = ".2s"
                    else:  # Quantidade Total
                        y_column = "qtd"
                        y_label = "Quantidade Total"
                        titulo_grafico = f"Top {num_products} Produtos por Quantidade"
                        sort_column = "qtd"
                        text_format = ".0f"

                    # Ordenar e pegar top N
                    df_prod_analise = df_prod_analise.sort_values(
                        sort_column, ascending=False
                    ).head(num_products)

                    # ✅ FORMATAÇÃO DOS CAMPOS
                    df_prod_analise["valor_net_fmt"] = df_prod_analise["valor_net"].apply(
                        tooltip_fmt_br
                    )
                    df_prod_analise["custo_total_fmt"] = df_prod_analise["custo_total"].apply(
                        tooltip_fmt_br
                    )
                    df_prod_analise["margem_valor_fmt"] = df_prod_analise["margem_em_valor"].apply(
                        tooltip_fmt_br
                    )
                    df_prod_analise["margem_perc_fmt"] = df_prod_analise[
                        "margem_em_porcentagem"
                    ].apply(lambda x: f"{x:.2f}%")
                    df_prod_analise["qtd_fmt"] = df_prod_analise["qtd"].apply(
                        lambda x: f"{x:,.0f}".replace(",", ".")
                    )

                    # Criar gráfico
                    fig_prod_analise = px.bar(
                        df_prod_analise,
                        x="descricao",
                        y=y_column,
                        text_auto=text_format,
                        labels={y_column: y_label, "descricao": "Produto"},
                        custom_data=[
                            "valor_net_fmt",
                            "custo_total_fmt",
                            "margem_valor_fmt",
                            "margem_perc_fmt",
                            "qtd_fmt",
                        ],
                    )

                    # Template de tooltip dinâmico
                    if metrica_produto == "Margem Total":
                        hovertemplate = (
                            "<b>Produto:</b> %{x}<br>"
                            + "<b>Valor NET Total:</b> %{customdata[0]}<br>"
                            + "<b>Custo Total:</b> %{customdata[1]}<br>"
                            + "<b>Margem em Valor:</b> %{customdata[2]}<br>"
                            + "<b>Margem (%):</b> %{customdata[3]}<br>"
                            + "<b>Quantidade:</b> %{customdata[4]}<extra></extra>"
                        )
                    else:  # Quantidade Total
                        hovertemplate = (
                            "<b>Produto:</b> %{x}<br>"
                            + "<b>Quantidade Total:</b> %{customdata[4]}<br>"
                            + "<b>Valor NET Total:</b> %{customdata[0]}<br>"
                            + "<b>Margem em Valor:</b> %{customdata[2]}<br>"
                            + "<b>Margem (%):</b> %{customdata[3]}<extra></extra>"
                        )

                    # Aplicar configurações do gráfico
                    fig_prod_analise.update_traces(
                        hovertemplate=hovertemplate,
                        marker=dict(color="#6C5B7B", line=dict(width=0), opacity=0.96),
                        textfont=dict(color="#ADD8E6", size=16),
                        hoverlabel=dict(
                            font_size=18,
                            font_family="Segoe UI, sans-serif",
                            bgcolor="#6C5B7B",
                            font_color="#E0E0E0",
                            align="left",
                        ),
                    )

                    # Aplicar layout
                    fig_prod_analise = apply_integrated_layout(
                        fig_prod_analise, title=titulo_grafico
                    )
                    if num_products > 15:
                        fig_prod_analise.update_xaxes(tickangle=-35, rangeslider_visible=True)

                    st.plotly_chart(fig_prod_analise, use_container_width=True)
                else:
                    st.info("Colunas necessárias não encontradas para o gráfico de Produtos.")
                
            else:
                st.warning("⚠️ Faça o upload de um arquivo para visualizar o dashboard.")
            
    elif st.session_state.pagina_atual == "Faturamento e Metas":
        
        # ===== GRÁFICO DE FATURAMENTO ACUMULADO COM METAS =====
        if file_selected is not None and 'filtered_df' in locals() and not filtered_df.empty:
        
            # ===== GRÁFICO DE FATURAMENTO ACUMULADO COM METAS =====
            st.markdown("#### Faturamento Acumulado com Metas")
            if "data" in filtered_df.columns and "valor_net" in filtered_df.columns:

                # ✅ INTERFACE PARA GERENCIAR METAS
                st.markdown("##### 🎯 Configurar Metas de Faturamento")

                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    valor_meta_str = st.text_input(
                        "Valor da Meta (R$)",
                        value="1.000.000,00",
                        help="Digite o valor da meta (formato: 1.000.000,00)",
                        placeholder="Ex: 2.500.000,00"
                    )

                    # Converter para número
                    try:
                        nova_meta = float(valor_meta_str.replace(".", "").replace(",", "."))
                    except:
                        nova_meta = 0.0
                        st.error("⚠️ Formato inválido. Use: 1.000.000,00")

                with col2:
                    nome_meta = st.text_input(
                        "Nome da Meta",
                        value=f"Meta {len(st.session_state.get('metas_faturamento', [])) + 1}",
                        help="Nome para identificar a meta",
                    )

                with col3:
                    st.markdown("<br>", unsafe_allow_html=True)  # Espaçamento
                    if st.button("➕ Adicionar Meta", help="Adicionar nova meta ao gráfico"):
                        if "metas_faturamento" not in st.session_state:
                            st.session_state.metas_faturamento = []

                        # Verificar se a meta já existe
                        meta_existente = any(
                            meta["valor"] == nova_meta and meta["nome"] == nome_meta
                            for meta in st.session_state.metas_faturamento
                        )

                        if not meta_existente and nova_meta > 0:
                            st.session_state.metas_faturamento.append(
                                {"nome": nome_meta, "valor": nova_meta}
                            )
                            st.success(
                                f"✅ Meta '{nome_meta}' adicionada: {nova_meta:,.2f}".replace(
                                    ",", "."
                                )
                            )
                        else:
                            st.warning("⚠️ Meta já existe ou valor inválido!")

                # ✅ MOSTRAR METAS EXISTENTES E PERMITIR REMOÇÃO
                if st.session_state.get("metas_faturamento"):
                    st.markdown("##### 📋 Metas Configuradas")

                    metas_para_remover = []
                    cols = st.columns(min(len(st.session_state.metas_faturamento), 4))

                    for i, meta in enumerate(st.session_state.metas_faturamento):
                        with cols[i % 4]:
                            st.markdown(
                                f"""
                            <div style="background: rgba(108, 91, 123, 0.1); padding: 10px; border-radius: 8px; border: 1px solid #6C5B7B;">
                                <b>{meta['nome']}</b><br>
                                R$ {meta['valor']:,.2f}
                            </div>
                            """.replace(
                                    ",", "."
                                ),
                                unsafe_allow_html=True,
                            )
                            
                            # ✅ ESPAÇAMENTO ENTRE CARD E BOTÃO
                            st.markdown("<br>", unsafe_allow_html=True)

                            if st.button(
                                f"🗑️ Remover",
                                key=f"remove_meta_{i}",
                                help=f"Remover {meta['nome']}",
                            ):
                                metas_para_remover.append(i)

                    # Remover metas selecionadas
                    for i in sorted(metas_para_remover, reverse=True):
                        meta_removida = st.session_state.metas_faturamento.pop(i)
                        st.success(f"🗑️ Meta '{meta_removida['nome']}' removida!")
                        st.rerun()

                st.markdown("---")

                # === BASES DIÁRIAS PARA ANÁLISE DE METAS ===
                
                filtered_df["data"] = pd.to_datetime(filtered_df["data"])

                # Faturamento total diário
                df_faturamento_diario = (
                    filtered_df
                    .sort_values("data")
                    .groupby("data", as_index=False)
                    .agg(valor_net=("valor_net", "sum"))
                )
                df_faturamento_diario["faturamento_acumulado"] = df_faturamento_diario["valor_net"].cumsum()
                df_faturamento_diario["mes_ano"] = df_faturamento_diario["data"].dt.strftime("%Y-%m")

                # Faturamento diário por representante
                df_rep_final_diario = pd.DataFrame()
                if "representante" in filtered_df.columns:
                    reps_diario = filtered_df["representante"].unique()
                    lista_df_rep_diario = []
                    for rep in reps_diario:
                        df_tmp = (
                            filtered_df[filtered_df["representante"] == rep]
                            .sort_values("data")
                            .groupby("data", as_index=False)
                            .agg(valor_net=("valor_net", "sum"))
                        )
                        df_tmp["faturamento_acumulado"] = df_tmp["valor_net"].cumsum()
                        df_tmp["mes_ano"] = df_tmp["data"].dt.strftime("%Y-%m")
                        df_tmp["representante"] = rep
                        lista_df_rep_diario.append(df_tmp)
                    if lista_df_rep_diario:
                        df_rep_final_diario = pd.concat(lista_df_rep_diario, ignore_index=True)
                
                # ✅ CALCULAR FATURAMENTO ACUMULADO MENSAL (TOTAL + POR REPRESENTANTE)

                # Garante que 'mes_ano' existe
                if "mes_ano" not in filtered_df.columns:
                    filtered_df["mes_ano"] = filtered_df["data"].dt.strftime("%Y-%m")

                # --- FATURAMENTO TOTAL MENSAL ---
                df_faturamento = (
                    filtered_df
                    .groupby("mes_ano", as_index=False)
                    .agg(valor_net=("valor_net", "sum"))
                    .sort_values("mes_ano")
                )
                df_faturamento["faturamento_acumulado"] = df_faturamento["valor_net"].cumsum()

                # --- FATURAMENTO POR REPRESENTANTE MENSAL ---
                df_rep_final = pd.DataFrame()
                representantes = []

                if "representante" in filtered_df.columns:
                    df_rep = (
                        filtered_df
                        .groupby(["mes_ano", "representante"], as_index=False)
                        .agg(valor_net=("valor_net", "sum"))
                        .sort_values("mes_ano")
                    )

                    representantes = df_rep["representante"].unique()
                    df_rep_acumulado = []
                    for rep in representantes:
                        df_temp = df_rep[df_rep["representante"] == rep].copy()
                        df_temp["faturamento_acumulado"] = df_temp["valor_net"].cumsum()
                        df_rep_acumulado.append(df_temp)

                    if df_rep_acumulado:
                        df_rep_final = pd.concat(df_rep_acumulado, ignore_index=True)

                # --- Formatação para tooltips do TOTAL ---
                df_faturamento["valor_mensal_fmt"] = df_faturamento["valor_net"].apply(tooltip_fmt_br)
                df_faturamento["acumulado_fmt"] = df_faturamento["faturamento_acumulado"].apply(tooltip_fmt_br)

                # Calcular acumulado
                df_faturamento["faturamento_acumulado"] = df_faturamento["valor_net"].cumsum()

                # Formatação para tooltips
                df_faturamento["valor_mensal_fmt"] = df_faturamento["valor_net"].apply(
                    tooltip_fmt_br
                )
                df_faturamento["acumulado_fmt"] = df_faturamento["faturamento_acumulado"].apply(
                    tooltip_fmt_br
                )

                # ✅ CRIAR GRÁFICO DE FATURAMENTO ACUMULADO (USANDO BASE DIÁRIA)
                fig_faturamento = go.Figure()

                # Linha principal do faturamento acumulado (TOTAL) - diário
                df_total = df_faturamento_diario.copy()
                df_total["valor_dia_fmt"] = df_total["valor_net"].apply(tooltip_fmt_br)
                df_total["acumulado_fmt"] = df_total["faturamento_acumulado"].apply(tooltip_fmt_br)
                df_total["data_fmt"] = df_total["data"].dt.strftime("%d/%m/%Y")

                fig_faturamento.add_trace(
                    go.Scatter(
                        x=df_total["data"],  # eixo X em datas reais
                        y=df_total["faturamento_acumulado"],
                        mode="lines+markers",
                        name="💰 Faturamento Acumulado",
                        line=dict(width=4, color="#ADD8E6"),
                        marker=dict(size=8, color="#ADD8E6"),
                        customdata=list(
                            zip(
                                df_total["data_fmt"],
                                df_total["valor_dia_fmt"],
                                df_total["acumulado_fmt"],
                            )
                        ),
                        hovertemplate=(
                            "<b>💰 Faturamento Acumulado</b><br>"
                            + "<b>Data:</b> %{customdata[0]}<br>"
                            + "<b>Faturamento do Dia:</b> %{customdata[1]}<br>"
                            + "<b>Faturamento Acumulado:</b> %{customdata[2]}<extra></extra>"
                        ),
                        visible=True,
                    )
                )

                # ✅ ADICIONAR LINHAS DOS REPRESENTANTES - diário
                if not df_rep_final_diario.empty:
                    cores_representantes = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4",
                                            "#FFEAA7", "#DDA0DD", "#F8B500", "#FF8C94"]

                    reps = df_rep_final_diario["representante"].unique()
                    for i, rep in enumerate(reps):
                        df_rep_atual = df_rep_final_diario[df_rep_final_diario["representante"] == rep].copy()
                        df_rep_atual["valor_dia_fmt"] = df_rep_atual["valor_net"].apply(tooltip_fmt_br)
                        df_rep_atual["acumulado_fmt"] = df_rep_atual["faturamento_acumulado"].apply(tooltip_fmt_br)
                        df_rep_atual["data_fmt"] = df_rep_atual["data"].dt.strftime("%d/%m/%Y")

                        cor_rep = cores_representantes[i % len(cores_representantes)]

                        fig_faturamento.add_trace(
                            go.Scatter(
                                x=df_rep_atual["data"],
                                y=df_rep_atual["faturamento_acumulado"],
                                mode="lines+markers",
                                name=f"👤 {quebrar_nome_legenda(rep, 20)}",
                                line=dict(width=2, color=cor_rep),
                                marker=dict(size=5, color=cor_rep),
                                customdata=list(
                                    zip(
                                        df_rep_atual["data_fmt"],
                                        df_rep_atual["valor_dia_fmt"],
                                        df_rep_atual["acumulado_fmt"],
                                    )
                                ),
                                hovertemplate=(
                                    f"<b>👤 {rep}</b><br>"
                                    + "<b>Data:</b> %{customdata[0]}<br>"
                                    + "<b>Faturamento do Dia:</b> %{customdata[1]}<br>"
                                    + "<b>Faturamento Acumulado:</b> %{customdata[2]}<extra></extra>"
                                ),
                                visible="legendonly",
                            )
                        )

                # ✅ ADICIONAR LINHAS DE META
                cores_metas = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD"]

                if st.session_state.get("metas_faturamento"):
                    for i, meta in enumerate(st.session_state.metas_faturamento):
                        cor_meta = cores_metas[i % len(cores_metas)]

                        fig_faturamento.add_trace(
                            go.Scatter(
                                x=df_faturamento["mes_ano"],
                                y=[meta["valor"]] * len(df_faturamento),
                                mode="lines",
                                name=f"🎯 {meta['nome']}",
                                line=dict(width=3, color=cor_meta, dash="dash"),
                                hovertemplate=(
                                    f"<b>🎯 {meta['nome']}</b><br>"
                                    + f"<b>Valor da Meta:</b> {tooltip_fmt_br(meta['valor'])}<br>"
                                    + "<b>Mês/Ano:</b> %{x}<extra></extra>"
                                ),
                                visible=True,
                            )
                        )

                # ✅ LAYOUT DO GRÁFICO
                fig_faturamento.update_layout(
                    title={
                        "text": "Faturamento Acumulado vs Metas",
                        "y": 0.93,
                        "x": 0.5,
                        "xanchor": "center",
                        "yanchor": "top",
                        "font": {
                            "size": 30,
                            "color": "#ADD8E6",
                            "family": "Segoe UI, sans-serif",
                        },
                    },
                    font=dict(family="Segoe UI, sans-serif", size=18, color="#E0E0E0"),
                    plot_bgcolor="#22232B",
                    paper_bgcolor="#22232B",
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.02,
                        font=dict(size=13, color="#ADD8E6"),
                        bgcolor="rgba(34, 35, 43, 0.95)",
                        bordercolor="#6C5B7B",
                        borderwidth=1,
                        itemwidth=30,
                        itemsizing="constant",
                        traceorder="normal",
                        tracegroupgap=5,
                        itemclick="toggle",
                        itemdoubleclick="toggleothers",
                    ),
                    margin=dict(l=40, r=90, t=70, b=40),
                    xaxis=dict(
                        title="Data",
                        title_font=dict(size=20, color="#ADD8E6", family="Segoe UI, sans-serif"),
                        tickfont=dict(size=16, color="#E0E0E0"),
                        gridcolor="rgba(160, 160, 160, 0.15)",
                        showgrid=True,
                        zeroline=False,
                        type="date",          # eixo de datas
                        tickformat="%d/%m/%Y" # formato desejado
                    ),
                    yaxis=dict(
                        title="Faturamento Acumulado (R$)",
                        title_font=dict(
                            size=20, color="#ADD8E6", family="Segoe UI, sans-serif"
                        ),
                        tickfont=dict(size=16, color="#E0E0E0"),
                        gridcolor="rgba(160, 160, 160, 0.12)",
                        showgrid=True,
                        zeroline=False,
                    ),
                    width=1400,
                    height=600,
                    hoverlabel=dict(
                        font_size=18,
                        font_family="Segoe UI, sans-serif",
                        bgcolor="#6C5B7B",
                        font_color="#E0E0E0",
                    ),
                )

                st.plotly_chart(fig_faturamento, use_container_width=True)

                # ✅ ANÁLISE DE PERFORMANCE DAS METAS MELHORADA
                if st.session_state.get("metas_faturamento") and not df_faturamento.empty:
                    st.markdown("##### 📊 Análise de Performance das Metas")

                    # ✅ DROPDOWN PARA SELEÇÃO DE ANÁLISE
                    opcoes_analise = ["💰 Faturamento Total"]
                    if 'representante' in filtered_df.columns:
                        representantes = sorted(filtered_df['representante'].unique())
                        opcoes_analise.extend([f"👤 {rep}" for rep in representantes])

                    analise_selecionada = st.selectbox(
                        "Selecione a análise:",
                        opcoes_analise,
                        help="Escolha entre faturamento total ou representante individual"
                    )

                    # ✅ DETERMINAR DADOS PARA ANÁLISE (USANDO BASE DIÁRIA)
                    dados_analise = pd.DataFrame()
                    nome_analise = ""

                    if analise_selecionada == "💰 Faturamento Total":
                        # usa a base diária total
                        dados_analise = df_faturamento_diario.copy()
                        nome_analise = "Faturamento Total"
                    else:
                        rep_selecionado = analise_selecionada.replace("👤 ", "")

                        # usa a base diária por representante
                        if (
                            "df_rep_final_diario" in locals()
                            and not df_rep_final_diario.empty
                            and rep_selecionado in df_rep_final_diario["representante"].unique()
                        ):
                            dados_analise = df_rep_final_diario[
                                df_rep_final_diario["representante"] == rep_selecionado
                            ].copy()
                            dados_analise = dados_analise.sort_values("data")
                            nome_analise = f"Representante: {rep_selecionado}"
                        else:
                            dados_analise = df_faturamento_diario.copy()
                            nome_analise = "Faturamento Total (Fallback)"
                            st.warning(
                                f"⚠️ Dados para o representante '{rep_selecionado}' não encontrados. "
                                "Exibindo Faturamento Total diário."
                            )

                    st.markdown(f"**Analisando:** {nome_analise}")

                    # ✅ FUNÇÃO PARA ENCONTRAR DATA DE ATINGIMENTO DA META
                    def encontrar_data_meta(dados_df: pd.DataFrame, valor_meta: float):
                        if dados_df.empty or "data" not in dados_df.columns:
                            return None

                        dados_df = dados_df.sort_values("data")
                        linha = dados_df[dados_df["faturamento_acumulado"] >= valor_meta].head(1)
                        if linha.empty:
                            return None

                        return linha["data"].iloc[0]
                    
                    # ✅ ANÁLISE POR META
                    faturamento_atual = dados_analise['faturamento_acumulado'].iloc[-1] if not dados_analise.empty else 0
                    cols_analise = st.columns(min(len(st.session_state.metas_faturamento), 3))
                    for i, meta in enumerate(st.session_state.metas_faturamento):
                        with cols_analise[i % 3]:
                            percentual = (faturamento_atual / meta["valor"]) * 100 if meta["valor"] > 0 else 0
                            diferenca = faturamento_atual - meta["valor"]
                            # Inicializa as variáveis para cada meta
                            status_html = ""
                            cor_borda = ""
                            data_info_html = ""
                            data_atingimento_raw = encontrar_data_meta(dados_analise, meta["valor"])

                            if percentual >= 100:
                                cor_borda = "#4CAF50"
                                status_html = '<p style="margin: 5px 0; color: #4CAF50;"><b>✅ META ATINGIDA!</b></p>'
                                if data_atingimento_raw is not None:
                                    data_formatada = data_atingimento_raw.strftime("%d/%m/%Y")
                                    data_info_html = f'<p style="margin: 5px 0;"><b>Data Atingida:</b> {data_formatada}</p>'
                                else:
                                    data_info_html = ""                                  
                            elif percentual >= 80:
                                cor_borda = "#FF9800"
                                status_html = '<p style="margin: 5px 0; color: #FF9800;"><b>⚠️ Próximo da meta</b></p>'
                                data_info_html = ""

                            else:
                                cor_borda = "#F44336"
                                status_html = '<p style="margin: 5px 0; color: #F44336;"><b>❌ META NÃO ATINGIDA!</b></p>'
                                data_info_html = ""

                            card_html = """
                            <div style="background: rgba(108, 91, 123, 0.1); padding: 15px; border-radius: 10px; border: 2px solid {cor_borda};">
                                <h4 style="color: {cor_borda}; margin: 0;">{nome_meta}</h4>
                                <p style="margin: 5px 0;"><b>Meta:</b> {meta_valor}</p>
                                <p style="margin: 5px 0;"><b>Atual:</b> {atual}</p>
                                <p style="margin: 5px 0;"><b>Performance:</b> {percentual:.1f}%</p>
                                <p style="margin: 5px 0;"><b>Diferença:</b> {dif}</p>
                                {data_info}
                                {status}
                            </div>
                            """.format(
                                cor_borda=cor_borda,
                                nome_meta=meta["nome"],
                                meta_valor=tooltip_fmt_br(meta["valor"]),
                                atual=tooltip_fmt_br(faturamento_atual),
                                percentual=percentual,
                                dif=tooltip_fmt_br(diferenca),
                                data_info=data_info_html,
                                status=status_html,
                            )

                            st.markdown(card_html, unsafe_allow_html=True)

            else:
                st.info("Colunas necessárias não encontradas para o gráfico de faturamento.")
                
        else:
            st.warning("⚠️ Faça o upload de um arquivo para visualizar o faturamento e metas.")
    
    elif st.session_state.pagina_atual == "Análise por Sabor":
        
        # ===== PÁGINA: ANÁLISE POR SABOR =====
        if file_selected is not None and 'filtered_df' in locals() and filtered_df is not None and not filtered_df.empty:
            # Conferir se temos as colunas necessárias
            if "descricao" in filtered_df.columns and "cliente" in filtered_df.columns and "valor_net" in filtered_df.columns:
                st.markdown("### 🍦 Análise por Sabor (Produto) por Cliente")

                sabores_disponiveis = sorted(filtered_df["descricao"].unique().tolist())

                # Inicializa o estado se não existir
                if "termo_busca_sabor_atual" not in st.session_state:
                    st.session_state["termo_busca_sabor_atual"] = ""
                if "sabores_selecionados_sabor" not in st.session_state:
                    st.session_state["sabores_selecionados_sabor"] = []

                # Campo de texto para o termo de busca
                # Usamos on_change para atualizar o estado APENAS quando o input muda,
                # evitando re-execuções desnecessárias se o valor não mudou.
                termo_busca_sabor = st.text_input(
                    "Digite um termo para filtrar os sabores:",
                    value=st.session_state["termo_busca_sabor_atual"],
                    key="termo_busca_sabor_input",
                    help="Digite parte do nome do sabor para filtrar as opções abaixo.",
                    on_change=lambda: st.session_state.update(termo_busca_sabor_atual=st.session_state.termo_busca_sabor_input)
                )

                # Filtra as opções disponíveis para o multiselect com base no termo de busca
                if termo_busca_sabor:
                    opcoes_filtradas_sabor = [
                        s for s in sabores_disponiveis if termo_busca_sabor.lower() in s.lower()
                    ]
                else:
                    opcoes_filtradas_sabor = sabores_disponiveis

                # Garante que os sabores já selecionados ainda estão nas opções filtradas
                # Isso evita que o multiselect "perca" a seleção se o termo de busca mudar.
                opcoes_para_multiselect = sorted(list(set(opcoes_filtradas_sabor + st.session_state["sabores_selecionados_sabor"])))

                # Multiselect com as opções filtradas e mantendo as seleções anteriores
                # Usamos on_change para atualizar o estado APENAS quando a seleção muda.
                sabores_selecionados = st.multiselect(
                    "Opções de sabores filtradas:",
                    options=opcoes_para_multiselect,
                    default=st.session_state["sabores_selecionados_sabor"],
                    help="Selecione quantos produtos quiser da lista filtrada.",
                    key="multiselect_sabores_final",
                    on_change=lambda: st.session_state.update(sabores_selecionados_sabor=st.session_state.multiselect_sabores_final)
                )

                # Lógica de filtro para o DataFrame (mantida como antes)
                if sabores_selecionados:
                    df_sabor = filtered_df[filtered_df["descricao"].isin(sabores_selecionados)].copy()
                    titulo_sabor = ", ".join(sabores_selecionados[:3])
                    if len(sabores_selecionados) > 3:
                        titulo_sabor += " + outros"
                else:
                    df_sabor = filtered_df.copy()
                    titulo_sabor = "todos os sabores"
                    
                # 👉 ABREVIAR O TÍTULO PARA NÃO ESTOURAR A LARGURA DO GRÁFICO
                def abreviar_titulo(texto, max_chars=70):
                    texto = str(texto)
                    return texto if len(texto) <= max_chars else texto[: max_chars - 3] + "..."

                titulo_sabor_abrev = abreviar_titulo(titulo_sabor, max_chars=70)

                if df_sabor.empty:
                    st.info("Nenhum dado encontrado para o sabor selecionado com os filtros atuais.")
                else:
                    # Agregar: por cliente, quantos pedidos e qual o faturamento total desse(s) sabor(es)
                    df_clientes_sabor = (
                        df_sabor
                        .groupby("cliente", as_index=False)
                        .agg(
                            qtd_pedidos=("descricao", "count"),   # número de registros daquele sabor
                            faturamento_total=("valor_net", "sum")
                        )
                    )

                    # Centralizar os botões de rádio para ordenação
                    st.markdown("<h7 style='text-align: left; color: #E0E0E0;'>Ordenar por:</h7>", unsafe_allow_html=True)

                    # Cria 3 colunas: uma vazia à esquerda, uma para o rádio, uma vazia à direita
                    col1, col2, col3 = st.columns([1, 2, 1]) # Ajuste os números para controlar o espaçamento

                    with col2: # Coloca o st.radio na coluna do meio
                        criterio_ordem = st.radio(
                            "", # Deixa o label vazio aqui, pois já colocamos um título centralizado acima
                            options=["Faturamento Total", "Quantidade de Pedidos"],
                            horizontal=True,
                            key="criterio_ordem_sabor" # Adicione uma key para evitar avisos do Streamlit
                        )

                    # Define qual coluna será usada no eixo Y e no label
                    if criterio_ordem == "Faturamento Total":
                        df_clientes_sabor = df_clientes_sabor.sort_values(
                            "faturamento_total", ascending=False
                        )
                        y_col = "faturamento_total"
                        y_label = "Faturamento total do sabor (R$)"
                    else:
                        df_clientes_sabor = df_clientes_sabor.sort_values(
                            "qtd_pedidos", ascending=False
                        )
                        y_col = "qtd_pedidos"
                        y_label = "Quantidade de pedidos do sabor"

                    # Limite de clientes no gráfico
                    max_clientes = st.slider(
                        "Quantidade de clientes a exibir:",
                        min_value=5,
                        max_value=50,
                        value=min(10, len(df_clientes_sabor)),
                        key="slider_clientes_sabor",
                    )

                    df_top_clientes_sabor = df_clientes_sabor.head(max_clientes).copy()

                    # 👉 ABREVIAR NOME DOS CLIENTES PARA O EIXO X
                    def abreviar_nome(nome, max_chars=22):
                        nome = str(nome)
                        return (nome[: max_chars - 3] + "...") if len(nome) > max_chars else nome

                    df_top_clientes_sabor["cliente_abrev"] = df_top_clientes_sabor["cliente"].apply(
                        abreviar_nome
                    )

                    # Formatações auxiliares para tooltip
                    df_top_clientes_sabor["faturamento_fmt"] = df_top_clientes_sabor["faturamento_total"].apply(
                        tooltip_fmt_br
                    )
                    df_top_clientes_sabor["qtd_pedidos_fmt"] = df_top_clientes_sabor["qtd_pedidos"].astype(int)
                    
                    # Texto que será exibido nas barras, conforme o critério
                    if y_col == "faturamento_total":
                        df_top_clientes_sabor["y_text"] = df_top_clientes_sabor["faturamento_total"].apply(
                            lambda v: tooltip_fmt_br(v)
                        )
                    else:
                        df_top_clientes_sabor["y_text"] = df_top_clientes_sabor["qtd_pedidos"].astype(int).astype(str)

                    fig_sabor_clientes = go.Figure()
                    fig_sabor_clientes.add_trace(
                        go.Bar(
                            x=df_top_clientes_sabor["cliente_abrev"],   # <<< abreviado
                            y=df_top_clientes_sabor[y_col],
                            marker=dict(
                                color="#6C5B7B",
                                line=dict(width=0),
                                opacity=0.96,
                            ),
                            customdata=list(
                                zip(
                                    df_top_clientes_sabor["cliente"],          # 0: nome completo
                                    df_top_clientes_sabor["qtd_pedidos"],      # 1
                                    df_top_clientes_sabor["faturamento_fmt"],  # 2
                                )
                            ),
                            hovertemplate=(
                                "<b>Cliente:</b> %{customdata[0]}<br>"
                                "<b>Qtd de pedidos do sabor:</b> %{customdata[1]}<br>"
                                "<b>Faturamento total do sabor:</b> %{customdata[2]}"
                                "<extra></extra>"
                            ),
                            name="Clientes do sabor",
                            
                            # 🔹 RÓTULO NAS BARRAS
                            text=df_top_clientes_sabor["y_text"],
                            textposition="auto",    # Plotly decide se é dentro ou acima
                            textangle=0,  # 👈 AGORA NO LUGAR CERTO: DIRETAMENTE NO go.Bar
                            textfont=dict(
                                color="#ADD8E6",
                                size=16,
                            ),
                        )
                    )

                    fig_sabor_clientes.update_layout(
                    title={
                        "text": f"Clientes por sabor: {titulo_sabor_abrev}",
                        "y": 0.93,
                        "x": 0.5,
                        "xanchor": "center",
                        "yanchor": "top",
                        "font": {
                            "size": 18,
                            "color": "#ADD8E6",
                            "family": "Segoe UI, sans-serif",
                        },
                    },

                    font=dict(
                        family="Segoe UI, sans-serif",
                        size=16,                        # tamanho padrão para textos do gráfico
                        color="#E0E0E0",
                    ),
                    plot_bgcolor="#22232B",
                    paper_bgcolor="#22232B",
                    xaxis=dict(
                        title="Cliente",
                        title_font=dict(size=18, color="#ADD8E6"),
                        tickfont=dict(size=11, color="#E0E0E0"),   # menor para caber mais nomes abreviados
                        gridcolor="rgba(160, 160, 160, 0.15)",
                        showgrid=False,
                        tickangle=-30,
                    ),
                    yaxis=dict(
                        title=y_label,                  # "Qtd de pedidos..." ou "Faturamento..." (definido antes)
                        title_font=dict(size=18, color="#ADD8E6"),
                        tickfont=dict(size=14, color="#E0E0E0"),
                        gridcolor="rgba(160, 160, 160, 0.12)",
                        showgrid=True,
                        zeroline=False,
                        automargin=True,               # ajuda a não deixar o título do eixo invadir o gráfico
                    ),
                    margin=dict(
                        l=60,   # um pouco maior para caber bem o título do eixo Y
                        r=40,
                        t=80,   # espaço extra em cima para o título principal
                        b=140,  # espaço para os nomes de clientes no eixo X
                    ),
                    hoverlabel=dict(
                        font_size=18,
                        font_family="Segoe UI, sans-serif",
                        bgcolor="#6C5B7B",
                        font_color="#E0E0E0",
                    ),
                )

                    st.plotly_chart(fig_sabor_clientes, use_container_width=True)

                    # ===== TABELA DETALHADA =====
                    st.markdown("#### Detalhamento por cliente")

                    df_tabela = df_clientes_sabor.copy()
                    df_tabela["Faturamento Total (R$)"] = df_tabela["faturamento_total"].apply(tooltip_fmt_br)
                    df_tabela = df_tabela.rename(
                        columns={
                            "cliente": "Cliente",
                            "qtd_pedidos": "Qtd de pedidos do sabor",
                        }
                    )[["Cliente", "Qtd de pedidos do sabor", "Faturamento Total (R$)"]]

                    st.dataframe(df_tabela, use_container_width=True)
            else:
                st.info(
                    "Colunas necessárias ('descricao', 'cliente', 'valor_net') não foram encontradas no arquivo."
                )
        else:
            st.warning("⚠️ Faça o upload de um arquivo e aplique os filtros para visualizar esta página.")

st.markdown("---")
st.markdown("Desenvolvido com Streamlit.")
