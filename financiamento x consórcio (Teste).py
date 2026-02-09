import streamlit as st
import pandas as pd
from math import pow

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Simulador Institucional | InvestSmartXP",
    page_icon="💎",
    layout="wide"
)

# =========================
# ESTILO VISUAL
# =========================
st.markdown("""
<style>
.main { background-color: #f8f9fa; }
.block-container { padding: 2rem; }
h1, h2, h3 { color: #1f2933; }
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES
# =========================
def financiamento_price(valor, juros_anual, prazo_meses):
    juros_mensal = pow(1 + juros_anual / 100, 1/12) - 1
    parcela = valor * (juros_mensal * pow(1 + juros_mensal, prazo_meses)) / (pow(1 + juros_mensal, prazo_meses) - 1)
    total = parcela * prazo_meses
    return parcela, total

def gerar_txt(conteudo):
    return conteudo.encode("utf-8")

# =========================
# TÍTULO
# =========================
st.title("💎 Simulador Institucional – InvestSmartXP")
st.caption("Ferramenta profissional de apoio à decisão financeira")

# =========================
# ABAS
# =========================
aba = st.tabs(["🏦 Financiamento", "🔁 Consórcio"])

# =========================
# FINANCIAMENTO
# =========================
with aba[0]:
    st.subheader("🏦 Simulação de Financiamento")

    valor = st.number_input("Valor do crédito (R$)", min_value=1000.0, step=1000.0)
    juros_anual = st.number_input("Taxa de juros ANUAL (%)", min_value=1.0, step=0.1)
    prazo = st.number_input("Prazo (meses)", min_value=6, step=6)

    if st.button("Simular Financiamento"):
        parcela, total = financiamento_price(valor, juros_anual, prazo)

        st.metric("Parcela Mensal", f"R$ {parcela:,.2f}")
        st.metric("Valor Total Pago", f"R$ {total:,.2f}")

        texto = f"""
SIMULAÇÃO DE FINANCIAMENTO – INVESTSMARTXP

Valor do crédito: R$ {valor:,.2f}
Taxa de juros anual: {juros_anual:.2f}%
Prazo: {prazo} meses

Parcela mensal: R$ {parcela:,.2f}
Valor total pago: R$ {total:,.2f}
"""

        st.download_button(
            "📄 Baixar Proposta (.txt)",
            gerar_txt(texto),
            file_name="proposta_financiamento.txt"
        )

# =========================
# CONSÓRCIO
# =========================
with aba[1]:
    st.subheader("🔁 Simulação de Consórcio")

    valor_carta = st.number_input("Valor da carta de crédito (R$)", min_value=10000.0, step=5000.0)
    prazo_consorcio = st.number_input("Prazo total (meses)", min_value=12, step=12)
    taxa_admin = st.number_input("Taxa de administração total (%)", min_value=5.0, step=0.1)

    parcelas_pagas = st.number_input(
        "Quantidade de parcelas já pagas (pré-contemplação)",
        min_value=0,
        max_value=int(prazo_consorcio),
        step=1
    )

    if st.button("Simular Consórcio"):
        valor_total = valor_carta * (1 + taxa_admin / 100)
        parcela = valor_total / prazo_consorcio
        saldo_devedor = valor_total - (parcelas_pagas * parcela)

        st.metric("Valor da Parcela", f"R$ {parcela:,.2f}")
        st.metric("Saldo Devedor Atual", f"R$ {saldo_devedor:,.2f}")

        # 📊 Gráfico de saldo devedor
        meses = list(range(parcelas_pagas, prazo_consorcio + 1))
        saldos = [valor_total - (m * parcela) for m in meses]

        df = pd.DataFrame({
            "Mês": meses,
            "Saldo Devedor (R$)": saldos
        })

        st.line_chart(df.set_index("Mês"))

        texto = f"""
SIMULAÇÃO DE CONSÓRCIO – INVESTSMARTXP

Valor da carta: R$ {valor_carta:,.2f}
Prazo total: {prazo_consorcio} meses
Taxa de administração: {taxa_admin:.2f}%

Parcelas pagas: {parcelas_pagas}
Valor da parcela: R$ {parcela:,.2f}
Saldo devedor atual: R$ {saldo_devedor:,.2f}
"""

        st.download_button(
            "📄 Baixar Proposta (.txt)",
            gerar_txt(texto),
            file_name="proposta_consorcio.txt"
        )























