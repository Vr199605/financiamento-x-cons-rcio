import streamlit as st
import pandas as pd
import numpy as np

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Simulador Institucional | InvestSmartXP",
    page_icon="💎",
    layout="wide"
)

st.title("💎 Simulador Institucional – Consórcio x Financiamento")
st.caption("Modelo educacional, comparativo e estratégico")

# =========================
# INPUTS PRINCIPAIS
# =========================
st.subheader("📥 Dados da Simulação")

col1, col2, col3 = st.columns(3)

with col1:
    valor_bem = st.number_input("Valor do Bem (R$)", min_value=50000.0, step=5000.0)

with col2:
    prazo = st.selectbox("Prazo (meses)", [120, 150, 180, 200])

with col3:
    taxa_adm = st.number_input("Taxa de Administração (%)", value=20.0)

lance_percentual = st.number_input(
    "🎯 Lance em Percentual (%)",
    min_value=0.0,
    max_value=100.0,
    step=0.5
)

perfil = st.selectbox(
    "Perfil do Cliente",
    ["Conservador", "Moderado", "Agressivo"]
)

st.divider()

# =========================
# CONSÓRCIO
# =========================
st.subheader("📊 Simulação de Consórcio")

valor_total_consorcio = valor_bem * (1 + taxa_adm / 100)
parcela_consorcio = valor_total_consorcio / prazo
valor_lance = valor_bem * (lance_percentual / 100)

# =========================
# CURVA DE CONTEMPLAÇÃO
# =========================
st.subheader("📊 Curva de Contemplação por Grupo")

meses = np.arange(1, prazo + 1)

base_chance = {
    "Conservador": 0.15,
    "Moderado": 0.25,
    "Agressivo": 0.35
}[perfil]

chance_contemplacao = np.clip(
    base_chance + (lance_percentual / 100) * np.log(meses + 1),
    0,
    0.95
)

df_curva = pd.DataFrame({
    "Mês": meses,
    "Chance de Contemplação (%)": chance_contemplacao * 100
})

st.line_chart(df_curva.set_index("Mês"))

# =========================
# RECOMENDAÇÃO AUTOMÁTICA
# =========================
st.subheader("🎯 Recomendação Automática de Lance Ideal")

if perfil == "Conservador":
    lance_ideal = 25
elif perfil == "Moderado":
    lance_ideal = 35
else:
    lance_ideal = 45

chance_atual = chance_contemplacao[11] * 100  # mês 12 como referência

st.metric("Lance Ideal Sugerido (%)", f"{lance_ideal}%")
st.metric("Chance Estimada até o 12º mês", f"{chance_atual:.1f}%")

# =========================
# FINANCIAMENTO
# =========================
st.subheader("🏦 Simulação de Financiamento")

colf1, colf2 = st.columns(2)

with colf1:
    taxa_juros = st.number_input("Taxa de Juros Mensal (%)", value=1.2)

with colf2:
    prazo_fin = st.selectbox("Prazo do Financiamento (meses)", [120, 180, 240, 360])

juros = taxa_juros / 100

parcela_fin = valor_bem * (
    (juros * (1 + juros) ** prazo_fin) /
    ((1 + juros) ** prazo_fin - 1)
)

total_financiamento = parcela_fin * prazo_fin

# =========================
# COMPARATIVO FINAL
# =========================
st.divider()
st.subheader("📈 Comparativo Final")

colc1, colc2, colc3 = st.columns(3)

with colc1:
    st.metric("Parcela Consórcio", f"R$ {parcela_consorcio:,.2f}")

with colc2:
    st.metric("Parcela Financiamento", f"R$ {parcela_fin:,.2f}")

with colc3:
    economia = total_financiamento - valor_total_consorcio
    st.metric("Economia com Consórcio", f"R$ {economia:,.2f}")

# =========================
# SCORE DE VANTAGEM
# =========================
st.subheader("📊 Score de Vantagem do Consórcio")

score = 0

if economia > 0:
    score += 40

if lance_percentual >= lance_ideal:
    score += 30

if parcela_consorcio < parcela_fin:
    score += 30

st.progress(score / 100)

st.write(f"**Score Final:** {score}/100")

if score >= 70:
    st.success("✅ Consórcio altamente vantajoso para este perfil.")
elif score >= 40:
    st.warning("⚠️ Consórcio pode ser vantajoso, dependendo da estratégia.")
else:
    st.error("❌ Financiamento pode ser mais adequado neste cenário.")

st.caption("Simulador educacional – InvestSmartXP")









