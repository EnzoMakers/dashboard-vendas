import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def calcular_margem_percentual(valor_net, custo_total):
    """
    Calcula margem percentual usando a fórmula: (1 - Custo Total/Valor NET) * 100
    """
    if valor_net == 0 or pd.isna(valor_net) or pd.isna(custo_total) or custo_total == 0:
        return 0
    
    # ✅ FÓRMULA EXATA: 1 - (Custo Total / Valor NET Total)
    margem = (1 - (custo_total / valor_net)) * 100
    return margem  # Sem limitação artificial de min/max

# ============ CSS E VISUAL PREMIUM HEADER E UPLOAD ============

st.set_page_config(
    page_title="DashBoard de Faturamento - TPMB",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@keyframes pulse {
  from { filter: brightness(1.0);}
  to   { filter: brightness(1.25) drop-shadow(0 0 8px #99D0FA55);}
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
""", unsafe_allow_html=True)

# Header visual central premium
st.markdown("""
<div style="text-align:center; margin-bottom: 0.2em;">
  <span style="font-size:4.2em; vertical-align:-0.18em; animation: pulse 1.8s infinite alternate;">📊</span>
</div>
<h1 style="text-align:center; color:#fff; font-size:3.2em; font-weight:900; margin-bottom:0;">
  DashBoard de Faturamento <span style="color:#ADD8E6">- TPMB</span>
</h1>
<div style="text-align:center; color:#bfcfe6; font-size:1.26em; font-weight:500; margin-bottom:1.4em;">
  Este dashboard interativo permite analisar dados de faturamento, margem e custos.<br>
  Faça o upload do seu arquivo <b>CSV</b> ou <b>Excel</b> e explore as métricas e gráficos!
</div>
""", unsafe_allow_html=True)

# ======= BLOCO VISUAL DE UPLOAD MULTIARQUIVO + SELEÇÃO =======

uploaded_files = st.file_uploader(
    "Arraste e solte um ou mais arquivos (CSV/Excel)",
    type=["csv", "xlsx"],
    accept_multiple_files=True,
    key="custom_uploader"  # key única, usada só aqui!
)

file_selected = None
if uploaded_files:
    file_names = [f.name for f in uploaded_files]
    selected_name = st.selectbox(
        "Selecione o arquivo que deseja analisar:",
        file_names,
        index=0
    )
    # Vincula o arquivo selecionado
    file_selected = next((f for f in uploaded_files if f.name == selected_name), None)

# =========== FEEDBACK VISUAL PREMIUM: ARQUIVO EM ANÁLISE ===========
if file_selected is not None:
    st.markdown(f"""
        <div style="margin: 1.2em auto 2.2em auto; max-width:560px; padding:16px 32px;
                    background: linear-gradient(98deg, #2e5137 70%, #3AD28A 100%);
                    border-radius: 14px; box-shadow:0 1px 7px -2px #3AD28A55; color:#fff;
                    font-size:1.12em; display:flex; align-items:center; justify-content:center;">
          <span style="font-size:2em; margin-right:10px; animation: bounceIn 1.3s;">✅</span>
          <span><b>Arquivo <span style='color:#D0FFCE'>{file_selected.name}</span> carregado para análise!</b></span>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="margin: 1.2em auto 2.2em auto; max-width:650px; padding:20px 38px;
                    background: linear-gradient(94deg, #1e3449 70%, #29415a 100%);
                    border-radius: 13px; box-shadow:0 1px 6px -2px #99D0FA22;
                    color:#ADD8E6; font-size:1.15em; font-weight: 500;
                    display:flex; align-items:center; justify-content:center;">
          <span style="font-size:1.6em; margin-right:14px;">ℹ️</span>
          <span>Aguardando o upload de um arquivo CSV ou Excel para começar a análise...</span>
        </div>
    """, unsafe_allow_html=True)

# =========== CARREGAMENTO E PRÉ-PROCESSAMENTO DO ARQUIVO ESCOLHIDO ===========
df = None
if file_selected is not None:
    try:
        file_extension = file_selected.name.split('.')[-1]
        if file_extension == 'csv':
            df = pd.read_csv(file_selected, sep=';', decimal=',', encoding='latin1')
        elif file_extension == 'xlsx':
            df = pd.read_excel(file_selected)
        else:
            st.error("Formato de arquivo não suportado. Por favor, faça o upload de um arquivo CSV ou Excel.")
            st.stop()
        # (aqui segue o restante do seu pipeline: normalização, renomeação de colunas, filtros, etc.)
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}. Por favor, verifique o formato e o conteúdo do arquivo.")
        st.stop()

# ============ LAYOUT VISUAL INTEGRADO ============

def apply_integrated_layout(fig, title=""):
    fig.update_layout(
        title={
            'text': title,
            'y':0.93,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 30, 'color': '#ADD8E6', 'family': 'Segoe UI, sans-serif'}
        },
        font=dict(family='Segoe UI, sans-serif', size=18, color='#E0E0E0'),
        plot_bgcolor='#22232B',
        paper_bgcolor='#22232B',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=18, color='#ADD8E6')
        ),
        margin=dict(l=40, r=40, t=70, b=40),
        xaxis=dict(
            title_font=dict(size=20, color='#ADD8E6', family='Segoe UI, sans-serif'),
            tickfont=dict(size=16, color='#E0E0E0'),
            gridcolor='rgba(160, 160, 160, 0.15)',
            showgrid=True,
            zeroline=False,
            tickangle=-25
        ),
        yaxis=dict(
            title_font=dict(size=20, color='#ADD8E6', family='Segoe UI, sans-serif'),
            tickfont=dict(size=16, color='#E0E0E0'),
            gridcolor='rgba(160, 160, 160, 0.12)',
            showgrid=True,
            zeroline=False
        ),
        width=1400,
        height=500
    )
    fig.update_traces(
        marker=dict(
            color='#6C5B7B',
            line=dict(width=0),
            opacity=0.96
        ),
        hoverlabel=dict(font_size=18, font_family="Segoe UI, sans-serif", bgcolor='#6C5B7B', font_color='#E0E0E0'),
        textfont=dict(color='#ADD8E6', size=16)
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
        return float(percentage_str.replace('%', '').replace('.', '').replace(',', '.'))
    except ValueError:
        return np.nan

# =========== CSS PREMIUM ===========

st.set_page_config(
    page_title="DashBoard de Faturamento - TPMB",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        margin-bottom: 22px;  /* Espaçamento regular entre os cards */
        transition: box-shadow 0.25s;
    }
    .kpi-metric-box:last-child {
        margin-bottom: 0 !important;  /* Remove espaço extra do último card */
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
    </style>
    """,
    unsafe_allow_html=True
)

# =========== CARREGAMENTO E PRÉ-PROCESSAMENTO DO ARQUIVO ESCOLHIDO ===========

df = None
filtered_df = None
if file_selected is not None:
    try:
        file_extension = file_selected.name.split('.')[-1]
        if file_extension == 'csv':
            df = pd.read_csv(file_selected, sep=';', decimal=',', encoding='latin1')          
        elif file_extension == 'xlsx':
            df = pd.read_excel(file_selected)
        else:
            st.error("Formato de arquivo não suportado. Por favor, faça o upload de um arquivo CSV ou Excel.")
            st.stop()
        
        # =========== CORREÇÃO PARA O PROBLEMA DO ARQUIVO ===========

        # 🔧 CORREÇÃO: Remove linhas que começam com "PDF:"
        if len(df.columns) > 0 and not df.empty:
            # Remove a primeira linha se for header incorreto
            first_col = df.columns[0]
            if 'PDF:' in str(first_col) or df.iloc[0, 0] == 'PDF:':
                df = df.iloc[1:].reset_index(drop=True)
        
        # 🔧 CORREÇÃO: Limpa linhas vazias ou problemáticas
        df = df.dropna(how='all')  # Remove linhas completamente vazias
        
        # 🔧 CORREÇÃO: Garante que todas as colunas sejam tratadas como string inicialmente
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).replace('nan', '')

        # PLUGUE AQUI O CÓDIGO DE DEBUG:
        for col in ['data', 'valor_bruto', 'custo_total', 'valor_net', 'margem_em_valor', 'margem_em_porcentagem', 'qtd', 'quantidade']:
            if col in df.columns:
                if 'data' in col:
                    # Para datas
                    problemas = df[pd.to_datetime(df[col], errors='coerce').isna() & df[col].notna()]
                else:
                    # Para números
                    problemas = df[pd.to_numeric(df[col], errors='coerce').isna() & df[col].notna()]
                if not problemas.empty:
                    st.write(f"Linhas problemáticas na coluna '{col}':")
                    st.write(problemas)

        # ======= PATCH: Conversão robusta de campos numéricos =========
        numeric_columns = [
            'valor_bruto',
            'custo_total',
            'margem_em_valor',
            'margem_em_porcentagem',
            'valor_net',
            'qtd',
            'custo_unitario'
        ]
        for col in numeric_columns:
            if col in df.columns:
                df[col] = (df[col].astype(str)\
                    .str.replace('%', '', regex=False)\
                    .str.replace('.', '', regex=False)\
                    .str.replace(',', '.', regex=False)\
                    .str.replace(' ', '')\
                    .replace('', np.nan)
                    )
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Normalização dos nomes das colunas (igual seu padrão)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('ç', 'c').str.replace('ã', 'a')\
            .str.replace('á', 'a').str.replace('é', 'e').str.replace('í', 'i').str.replace('ó', 'o').str.replace('ú', 'u')\
            .str.replace('â', 'a').str.replace('ê', 'e').str.replace('ô', 'o').str.replace('ü', 'u').str.replace('[^a-z0-9_]', '', regex=True)
        
        if 'representante' in df.columns:
            df = df[~df['representante'].astype(str).str.contains('total', case=False, na=False)]
        if 'cliente' in df.columns:
            df = df[~df['cliente'].astype(str).str.contains('total', case=False, na=False)]
        
        colunas_numericas = [
        'valor_bruto', 'custo_total', 'valor_net',
        'margem_em_valor', 'margem_em_porcentagem', 'qtd', 'quantidade'
        ] 
        for col in colunas_numericas:
            if col in df.columns:
                df = df[pd.to_numeric(df[col], errors='coerce').notnull()]
                df[col] = pd.to_numeric(df[col], errors='coerce')

        if 'valor_bruto' in df.columns:
            df = df[df['valor_bruto'].notnull()]

        column_mapping = {
            'data_venda': 'data', 'data_do_pedido': 'data', 'data_da_venda': 'data',
            'valor_bruto_da_venda': 'valor_bruto', 'valor_bruto': 'valor_bruto',
            'custo_total_da_venda': 'custo_total', 'custo_total': 'custo_total',
            'margem_em_valor': 'margem_em_valor', 'margem_em_porcentagem': 'margem_em_porcentagem',
            'representante_de_vendas': 'representante', 'nome_do_representante': 'representante',
            'nome_do_cliente': 'cliente', 'produto': 'descricao', 'descricao_do_produto': 'descricao'
        }
        df = df.rename(columns=column_mapping)
        
         # 3. ELIMINA LINHAS DE TOTAIS (não só em 'representante', mas em todas relevantes)
        for col in ['representante', 'cliente', 'descricao']:
            if col in df.columns:
                df = df[~df[col].astype(str).str.lower().str.contains('total|geral|totais', na=False)]

        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
            df.dropna(subset=['data'], inplace=True)

        # Mapeia percentuais
        if 'margem_em_porcentagem' in df.columns:
        # Corrige para garantir tipo float
           df['margem_em_porcentagem'] = pd.to_numeric(df['margem_em_porcentagem'], errors='coerce')
        # Se ainda tiver string, tenta converter
           if df['margem_em_porcentagem'].isnull().any():
                 df['margem_em_porcentagem'] = df['margem_em_porcentagem'].fillna(
                   df['margem_em_porcentagem'].astype(str).apply(parse_percentage_string)
                )
        # Somente faz ajuste se for realmente float
           try:
               if (df['margem_em_porcentagem'].dropna().astype(float) < 2).all() and (df['valor_bruto'].mean() > 1000):
                   df['margem_em_porcentagem'] *= 100
           except Exception as err:
                st.warning(f"Erro ao ajustar margem_em_porcentagem: {err}")
        else:
            if 'margem_em_valor' in df.columns and 'valor_bruto' in df.columns:
                df['margem_em_porcentagem'] = (df['margem_em_valor'] / df['valor_bruto'] * 100).replace([np.inf, -np.inf], np.nan).fillna(0)
            else:
                df['margem_em_porcentagem'] = 0

        required_cols = ['valor_bruto', 'custo_total', 'margem_em_valor', 'margem_em_porcentagem']
        for col in required_cols:
            if col not in df.columns:
                df[col] = 0

        # SIDEBAR DE FILTROS (igual seu padrão!)
        st.sidebar.markdown('<p class="subheader-font">Filtros de Dados</p>', unsafe_allow_html=True)
        # Filtro por Data
        if 'data' in df.columns and not df['data'].empty:
            min_date = df['data'].min().to_pydatetime().date()
            max_date = df['data'].max().to_pydatetime().date()
            date_range = st.sidebar.date_input("Selecione o período:", value=(min_date, max_date), min_value=min_date, max_value=max_date)
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_df = df[(df['data'].dt.date >= start_date) & (df['data'].dt.date <= end_date)]
            else:
                filtered_df = df.copy()
        else:
            filtered_df = df.copy()
            st.sidebar.info("Coluna 'data' não encontrada ou vazia para aplicar filtro de data.")

        # ✅ NOVO FILTRO: TP MOV
        if 'tp_mov' in filtered_df.columns and not filtered_df['tp_mov'].empty:
            all_tp_mov = sorted(filtered_df['tp_mov'].unique().tolist())
            selected_tp_mov = st.sidebar.multiselect(
               "Selecione o Tipo de Movimento:",
               options=all_tp_mov,
               default=all_tp_mov
            )
            if selected_tp_mov:
               filtered_df = filtered_df[filtered_df['tp_mov'].isin(selected_tp_mov)]
        else:
            st.sidebar.info("Coluna 'tp_mov' não encontrada ou vazia para aplicar filtro.")

        # Filtro por Representante (multi)
        if 'representante' in filtered_df.columns and not filtered_df['representante'].empty:
            all_representantes = sorted(filtered_df['representante'].unique().tolist())
            selected_representantes = st.sidebar.multiselect(
                "Selecione o(s) Representante(s):",
                options=all_representantes,
                default=all_representantes
            )
            if selected_representantes:
                filtered_df = filtered_df[filtered_df['representante'].isin(selected_representantes)]
        else:
            st.sidebar.info("Coluna 'representante' não encontrada ou vazia para aplicar filtro.")

        # Filtro por Cliente (multi)
        if 'cliente' in filtered_df.columns and not filtered_df['cliente'].empty:
            all_clientes = sorted(filtered_df['cliente'].unique().tolist())
            selected_clientes = st.sidebar.multiselect(
                "Selecione o(s) Cliente(s):",
                options=all_clientes,
                default=all_clientes
            )
            if selected_clientes:
                filtered_df = filtered_df[filtered_df['cliente'].isin(selected_clientes)]
        else:
            st.sidebar.info("Coluna 'cliente' não encontrada ou vazia para aplicar filtro.")

        # Filtro por Produto (multi)
        if 'descricao' in filtered_df.columns and not filtered_df['descricao'].empty:
            all_produtos = sorted(filtered_df['descricao'].unique().tolist())
            selected_produtos = st.sidebar.multiselect(
                "Selecione o(s) Produto(s):",
                options=all_produtos,
                default=all_produtos
            )
            if selected_produtos:
                filtered_df = filtered_df[filtered_df['descricao'].isin(selected_produtos)]
        else:
            st.sidebar.info("Coluna 'descricao' não encontrada ou vazia para aplicar filtro.")

        st.divider()
    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}. Por favor, verifique o formato e o conteúdo do arquivo.")
        st.stop()


    #=========== EXIBIÇÃO DA TABELA ===========

if file_selected is not None and 'filtered_df' in locals() and not filtered_df.empty:
    st.markdown('<p class="subheader-font">Dados Filtrados</p>', unsafe_allow_html=True)
    df_display = filtered_df.copy()
    # Dicionário de nomes amigáveis para todas as colunas (incluindo as novas)
    display_column_names = {
        'tp_mov': 'TP Mov',
        'nf': 'NF',
        'data': 'Data da Venda',
        'cliente': 'Cliente',
        'segmentacao': 'Segmentação',
        'representante': 'Representante',
        'cod_produto': 'Cód. Produto',
        'descricao': 'Descrição do Produto',
        'valor_bruto': 'Faturamento Bruto',
        'valor_net': 'Valor Net',
        'qtd': 'Quantidade',
        'custo_unitario': 'Custo Unitário',
        'custo_total': 'Custo Total',
        'margem_em_valor': 'Margem em Valor',
        'margem_em_porcentagem': 'Margem (%)'
    }
    # Renomeia apenas colunas existentes no DataFrame
    df_display = df_display.rename(columns={k: v for k, v in display_column_names.items() if k in df_display.columns})

    # Alinha Quantidade para inteiro à direita
    if 'Quantidade' in df_display.columns:
        df_display['Quantidade'] = (
            df_display['Quantidade']
            .fillna(0)
            .astype(float)
            .round(0)
            .astype(int)
        )

    format_dict = {
        'Faturamento Bruto': lambda x: format_currency_br(x) if pd.notna(x) else "R$ 0,00",
        'Valor Net': lambda x: format_currency_br(x) if pd.notna(x) else "R$ 0,00",
        'Custo Total': lambda x: format_currency_br(x) if pd.notna(x) else "R$ 0,00",
        'Custo Unitário': lambda x: format_currency_br(x) if pd.notna(x) else "R$ 0,00",
        'Margem em Valor': lambda x: format_currency_br(x) if pd.notna(x) else "R$ 0,00",
        'Margem (%)': lambda x: format_percentage_br(x) if pd.notna(x) else "0,00%"
    }
    final_format_dict = {col: fmt for col, fmt in format_dict.items() if col in df_display.columns}

    # Ajustes NF e Data
    if 'NF' in df_display.columns:
        try:
            df_display['NF'] = df_display['NF'].astype(float).astype(pd.Int64Dtype()).astype(str)
        except:
            pass
    if 'Data da Venda' in df_display.columns:
        try:
            df_display['Data da Venda'] = pd.to_datetime(df_display['Data da Venda'], errors='coerce').dt.strftime('%d/%m/%Y')
        except:
            pass
    # EXIBIÇÃO COM ALINHAMENTO: Números sempre à direita
    styler = df_display.style.format(final_format_dict)
    if 'Quantidade' in df_display.columns:
        styler = styler.set_properties(subset=['Quantidade'], **{'text-align': 'right'})
    st.dataframe(styler, use_container_width=True)
    st.divider()

    # =========== MÉTRICAS CHAVE VISUAL PREMIUM ===========

if file_selected is not None and filtered_df is not None:
    st.markdown('<p class="subheader-font">Métricas Chave</p>', unsafe_allow_html=True)

    total_valor_bruto = filtered_df['valor_bruto'].sum() if 'valor_bruto' in filtered_df.columns else 0
    total_custo_total = filtered_df['custo_total'].sum() if 'custo_total' in filtered_df.columns else 0
    total_valor_net = filtered_df['valor_net'].sum() if 'valor_net' in filtered_df.columns else 0
    total_margem_valor = filtered_df['margem_em_valor'].sum() if 'margem_em_valor' in filtered_df.columns else 0

    # NOVO CÁLCULO DA MARGEM MÉDIA (%) – cálculo correto, conforme book de melhores práticas
    if total_valor_net > 0:
        nova_margem_media = (total_valor_net - total_custo_total) / total_valor_net * 100
    else:
        nova_margem_media = 0

    st.markdown(f"""
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
        <div class="kpi-label">Margem Média (%)</div>
        <div class="kpi-icon">💹</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

# =========== GRÁFICOS COM TOOLTIPS FORMATADOS BR ===========

if file_selected is not None and filtered_df is not None:
    st.markdown('<p class="subheader-font">Análise Gráfica</p>', unsafe_allow_html=True)
    # Margem por Representante
    st.markdown("#### Margem por Representante")
    if 'representante' in filtered_df.columns and 'margem_em_valor' in filtered_df.columns and 'valor_net' in filtered_df.columns and 'custo_total' in filtered_df.columns:
        df_rep_margem = filtered_df.groupby('representante').agg(
           valor_net=('valor_net', 'sum'),
           custo_total=('custo_total', 'sum'),
           margem_em_valor=('margem_em_valor', 'sum')
        ).reset_index()
    
        # ✅ NOVA FÓRMULA DA MARGEM %
        df_rep_margem['margem_em_porcentagem'] = df_rep_margem.apply(
            lambda row: calcular_margem_percentual(row['valor_net'], row['custo_total']), axis=1
        )
    
        df_rep_margem = df_rep_margem.sort_values('margem_em_valor', ascending=False)
    
        # ✅ FORMATAÇÃO DOS NOVOS CAMPOS
        df_rep_margem['valor_net_fmt'] = df_rep_margem['valor_net'].apply(tooltip_fmt_br)
        df_rep_margem['custo_total_fmt'] = df_rep_margem['custo_total'].apply(tooltip_fmt_br)
        df_rep_margem['margem_valor_fmt'] = df_rep_margem['margem_em_valor'].apply(tooltip_fmt_br)
        df_rep_margem['margem_perc_fmt'] = df_rep_margem['margem_em_porcentagem'].apply(lambda x: f"{x:.2f}%")

    
        fig_rep_margem = px.bar(
            df_rep_margem,
            x='representante',
            y='margem_em_valor',
            text_auto='.2s',
            labels={'margem_em_valor': 'Margem em Valor (R$)', 'representante': 'Representante'},
            custom_data=['valor_net_fmt', 'custo_total_fmt', 'margem_valor_fmt', 'margem_perc_fmt']
        )
    
        # ✅ NOVO TEMPLATE DO TOOLTIP
        fig_rep_margem.update_traces(
            hovertemplate=
            "<b>Representante:</b> %{x}<br>" +
            "<b>Valor NET Total (R$):</b> %{customdata[0]}<br>" +
            "<b>Custo Total (R$):</b> %{customdata[1]}<br>" +
            "<b>Margem em Valor (R$):</b> %{customdata[2]}<br>" +
            "<b>Margem (%):</b> %{customdata[3]}<extra></extra>"
        )
    
        fig_rep_margem = apply_integrated_layout(fig_rep_margem, title='Margem por Representante')
        st.plotly_chart(fig_rep_margem, use_container_width=True)
    else:
        st.info("Colunas necessárias não encontradas para o gráfico de Representantes.")

    # Margem por Cliente (Top 10)
    st.markdown("#### Margem por Cliente")
    if 'cliente' in filtered_df.columns and 'margem_em_valor' in filtered_df.columns and 'valor_net' in filtered_df.columns and 'custo_total' in filtered_df.columns:
        df_cliente_margem = filtered_df.groupby('cliente').agg(
            valor_net=('valor_net', 'sum'),
            custo_total=('custo_total', 'sum'),
            margem_em_valor=('margem_em_valor', 'sum')
        ).reset_index()
    
        # ✅ NOVA FÓRMULA DA MARGEM %
        df_cliente_margem['margem_em_porcentagem'] = df_cliente_margem.apply(
            lambda row: calcular_margem_percentual(row['valor_net'], row['custo_total']), axis=1
        )
    
        df_cliente_margem = df_cliente_margem.sort_values('margem_em_valor', ascending=False).head(10)
    
        # ✅ FORMATAÇÃO DOS NOVOS CAMPOS
        df_cliente_margem['valor_net_fmt'] = df_cliente_margem['valor_net'].apply(tooltip_fmt_br)
        df_cliente_margem['custo_total_fmt'] = df_cliente_margem['custo_total'].apply(tooltip_fmt_br)
        df_cliente_margem['margem_valor_fmt'] = df_cliente_margem['margem_em_valor'].apply(tooltip_fmt_br)
        df_cliente_margem['margem_perc_fmt'] = df_cliente_margem['margem_em_porcentagem'].apply(lambda x: f"{x:.2f}%")
    
        # ✅ TRUNCAR NOMES DOS CLIENTES PARA MELHOR VISUALIZAÇÃO
        df_cliente_margem['cliente_display'] = df_cliente_margem['cliente'].apply(
            lambda x: x[:50] + '...' if len(x) > 50 else x
        )
    
        fig_cliente_margem = px.bar(
            df_cliente_margem,
            x='cliente_display',
            y='margem_em_valor',
            text_auto='.2s',
            labels={
                'margem_em_valor': 'Margem em Valor (R$)', 
                'cliente_display': 'Cliente'
            },
            custom_data=['valor_net_fmt', 'custo_total_fmt', 'margem_valor_fmt', 'margem_perc_fmt']
        )
    
        # ✅ NOVO TEMPLATE DO TOOLTIP
        fig_cliente_margem.update_traces(
            hovertemplate=
            "<b>Cliente:</b> %{x}<br>" +
            "<b>Valor NET Total (R$):</b> %{customdata[0]}<br>" +
            "<b>Custo Total (R$):</b> %{customdata[1]}<br>" +
            "<b>Margem em Valor (R$):</b> %{customdata[2]}<br>" +
            "<b>Margem (%):</b> %{customdata[3]}<extra></extra>"
        )
    
        # ✅ APLICAR LAYOUT PADRÃO (igual aos outros gráficos)
        fig_cliente_margem = apply_integrated_layout(fig_cliente_margem, title='Top 10 Clientes por Margem Total')
    
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

    # Margem Total Mensal
    st.markdown("#### Margem Total Mensal")
    if 'data' in filtered_df.columns and 'margem_em_valor' in filtered_df.columns and 'valor_net' in filtered_df.columns and 'custo_total' in filtered_df.columns:
        # Criar coluna de mês-ano
        filtered_df['mes_ano'] = filtered_df['data'].dt.to_period('M').astype(str)
    
        df_mensal_margem = filtered_df.groupby('mes_ano').agg(
            valor_net=('valor_net', 'sum'),
            custo_total=('custo_total', 'sum'),
            margem_em_valor=('margem_em_valor', 'sum')
        ).reset_index()
    
        # ✅ NOVA FÓRMULA DA MARGEM %
        df_mensal_margem['margem_em_porcentagem'] = df_mensal_margem.apply(
            lambda row: calcular_margem_percentual(row['valor_net'], row['custo_total']), axis=1
        )
    
        # Ordenar por data
        df_mensal_margem = df_mensal_margem.sort_values('mes_ano')
    
        # ✅ FORMATAÇÃO DOS NOVOS CAMPOS
        df_mensal_margem['valor_net_fmt'] = df_mensal_margem['valor_net'].apply(tooltip_fmt_br)
        df_mensal_margem['custo_total_fmt'] = df_mensal_margem['custo_total'].apply(tooltip_fmt_br)
        df_mensal_margem['margem_valor_fmt'] = df_mensal_margem['margem_em_valor'].apply(tooltip_fmt_br)
        df_mensal_margem['margem_perc_fmt'] = df_mensal_margem['margem_em_porcentagem'].apply(lambda x: f"{x:.2f}%")
    
        fig_mensal_margem = px.line(
            df_mensal_margem,
            x='mes_ano',
            y='margem_em_valor',
            markers=True,
            labels={'margem_em_valor': 'Margem em Valor (R$)', 'mes_ano': 'Mês/Ano'},
            custom_data=['valor_net_fmt', 'custo_total_fmt', 'margem_valor_fmt', 'margem_perc_fmt']
        )
    
        # ✅ NOVO TEMPLATE DO TOOLTIP
        fig_mensal_margem.update_traces(
            hovertemplate=
            "<b>Mês/Ano:</b> %{x}<br>" +
            "<b>Valor NET Total (R$):</b> %{customdata[0]}<br>" +
            "<b>Custo Total (R$):</b> %{customdata[1]}<br>" +
            "<b>Margem em Valor (R$):</b> %{customdata[2]}<br>" +
            "<b>Margem (%):</b> %{customdata[3]}<extra></extra>",
            line=dict(width=3),
            marker=dict(size=8)
        )
    
        fig_mensal_margem = apply_integrated_layout(fig_mensal_margem, title='Evolução da Margem Total Mensal')
        fig_mensal_margem.update_xaxes(tickangle=-45)
        st.plotly_chart(fig_mensal_margem, use_container_width=True)
    else:
        st.info("Colunas necessárias não encontradas para o gráfico mensal.")

    # Margem por Produto
    st.markdown("### Margem por Produto")
    if 'descricao' in filtered_df.columns and 'margem_em_valor' in filtered_df.columns and 'valor_bruto' in filtered_df.columns:
        
        # ✨ CSS LIMPO E FUNCIONAL
        st.markdown("""
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
        """, unsafe_allow_html=True)

        # APENAS UM SLIDER SIMPLES
        num_products = st.slider(
            "🎚️ Selecione a Quantidade de Produtos",
            min_value=2,
            max_value=30,
            value=10,
            step=1,
            help="Deslize para escolher quantos produtos mostrar no gráfico"
        )

        df_prod_margem = filtered_df.groupby('descricao').agg(
            valor_net=('valor_net', 'sum'),
            custo_total=('custo_total', 'sum'),
            margem_em_valor=('margem_em_valor', 'sum')
        ).reset_index()

        # ✅ NOVA FÓRMULA DA MARGEM %
        df_prod_margem['margem_em_porcentagem'] = df_prod_margem.apply(
            lambda row: calcular_margem_percentual(row['valor_net'], row['custo_total']), axis=1
        )

        df_prod_margem = df_prod_margem.sort_values('margem_em_valor', ascending=False).head(num_products)

        # ✅ FORMATAÇÃO DOS NOVOS CAMPOS
        df_prod_margem['valor_net_fmt'] = df_prod_margem['valor_net'].apply(tooltip_fmt_br)
        df_prod_margem['custo_total_fmt'] = df_prod_margem['custo_total'].apply(tooltip_fmt_br)
        df_prod_margem['margem_valor_fmt'] = df_prod_margem['margem_em_valor'].apply(tooltip_fmt_br)
        df_prod_margem['margem_perc_fmt'] = df_prod_margem['margem_em_porcentagem'].apply(lambda x: f"{x:.2f}%")

        fig_prod_margem = px.bar(
            df_prod_margem,
            x='descricao',
            y='margem_em_valor',
            text_auto='.2s',
            labels={'margem_em_valor': 'Margem em Valor (R$)', 'descricao': 'Produto'},
            custom_data=['valor_net_fmt', 'custo_total_fmt', 'margem_valor_fmt', 'margem_perc_fmt']
        )

        # ✅ NOVO TEMPLATE DO TOOLTIP
        fig_prod_margem.update_traces(
            hovertemplate=
            "<b>Produto:</b> %{x}<br>" +
            "<b>Valor NET Total (R$):</b> %{customdata[0]}<br>" +
            "<b>Custo Total (R$):</b> %{customdata[1]}<br>" +
            "<b>Margem em Valor (R$):</b> %{customdata[2]}<br>" +
            "<b>Margem (%):</b> %{customdata[3]}<extra></extra>"
        )

        fig_prod_margem = apply_integrated_layout(fig_prod_margem, title=f'Top {num_products} Produtos por Margem Total')
        if num_products > 15:
            fig_prod_margem.update_xaxes(tickangle=-35, rangeslider_visible=True)
        st.plotly_chart(fig_prod_margem, use_container_width=True)
    else:
        st.info("Colunas necessárias não encontradas para o gráfico de Produtos.")

st.markdown("---")
st.markdown("Desenvolvido com Streamlit.")











