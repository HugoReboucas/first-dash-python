# importando as bibliotecas necessárias
import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st
import pycountry

# Configurando o título e o layout da página
st.set_page_config(
    page_title="Dashbord de Salários na Área de Dados",
    page_icon="💼",
    layout="wide",
)

# criando o dataframe "df" e lendo ele atráves do arquivo csv do github
df = pd.read_csv("https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv")

#trocando o nome das colunas para português
df.rename(columns={
    'work_year': 'ano',
    'experience_level': 'senioridade',
    'employment_type': 'tipo_contrato',
    'job_title': 'cargo',
    'salary': 'salario',
    'salary_currency': 'moeda',
    'salary_in_usd': 'usd',
    'employee_residence': 'residencia',
    'remote_ratio': 'remoto',
    'company_location': 'empresa',
    'company_size': 'tamanho_empresa'
}, inplace=True)

df['senioridade'].replace({
    'SE': 'Senior',
    'MI': 'Pleno',
    'EN': 'Júnior',
    'EX': 'Executivo'
}, inplace=True)

df['tipo_contrato'].replace({
    'FT': 'Tempo Integral',
    'PT': 'Tempo Parcial',
    'FL': 'Freela',
    'CT': 'tipo_contrato'
}, inplace=True)

df['tamanho_empresa'].replace({
    'S': 'Pequena',
    'M': 'Média',
    'L': 'Grande',
}, inplace=True)

df['remoto'].replace({
    0: 'Presencial',
    50: 'Hibrido',
    100: 'Remoto',
}, inplace=True)

# barra lateral
st.sidebar.header("Filtros")

# Filtro de Ano
anos_disponiveis = sorted([int(a) for a in df['ano'].dropna().unique()])
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

#filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['tipo_contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

#filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# filtrando o dataframe com base nos filtros selecionados
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['tipo_contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# conteúdo principal
st.title("💼 Dashbord de Salários na Área de Dados")
st.markdown("Este dashboard apresenta uma análise dos salários na área de dados com base em diferentes filtros.")

# Métricas principais (KPI)

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['cargo'].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", total_registros)
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# Análises Visuais com Plotly

st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title='Top 10 Cargos com Maior Salário Médio',
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title='Distribuição de Salarios anuais',
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)
    
with col_graf3:
        if not df_filtrado.empty:
            remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
            remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
            grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
            )
            grafico_remoto.update_traces(textinfo='percent+label')
            grafico_remoto.update_layout(title_x=0.1)
            st.plotly_chart(grafico_remoto, use_container_width=True)
        else:
            st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

def iso2_to_iso3(iso2):
    try:
        return pycountry.countries.get(alpha_2=iso2).alpha_3
    except:
        return None

with col_graf4:
    if not df_filtrado.empty:
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist']
        # Use 'residencia' se não houver 'residencia'
        media_ds_pais = df_ds.groupby('residencia')['usd'].mean().reset_index()
         # Converter ISO-2 para ISO-3
        media_ds_pais['iso3'] = media_ds_pais['residencia'].apply(iso2_to_iso3)
        media_ds_pais = media_ds_pais.dropna(subset=['iso3'])
        grafico_pais = px.choropleth(
            media_ds_pais,
            locations='iso3',
            locationmode='ISO-3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário Médio de Data Scientists por País',
            labels={'usd': 'Salário médio (USD)', 'iso3': 'País'}
        )
        grafico_pais.update_layout(title_x=0.1)
        st.plotly_chart(grafico_pais, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")


# Tabela de Dados Detalhados
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)

