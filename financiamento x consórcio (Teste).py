import streamlit as st
import pandas as pd
import numpy as np

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="Intelligence Banking Pro",
    page_icon="💎",
    layout="wide"
)

st.markdown("""
<style>
.main { background-color: #f8f9fa; }
.card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    margin-bottom: 15px;
}
.footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    text-align: center;
    color: gray;
    padding: 8px;
}
h1, h2, h3 { color: #1e3a8a; }
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES – CONSÓRCIO
# =========================
def probabilidade_contemplacao(lance_pct):
    if lance_pct < 10: return "Muito Baixa", 10
    if lance_pct < 20: return "Baixa", 25
    if lance_pct < 30: return "Média", 50
    if lance_pct < 40: return "Alta", 75
    return "Muito Alta", 90

def ranking_lance(lance_pct):
    if lance_pct < 15: return "🔴 Pouco competitivo"
    if lance_pct < 30: return "🟡 Competitivo"
    if lance_pct < 45: return "🟢 Muito competitivo"
    return "🔥 Lance agressivo"

def lance_ideal_por_prazo(prazo):
    if prazo <= 6: return 40
    if prazo <= 12: return 30
    if prazo <= 24: return 20
    return 10

def calcular_consorcio(valor, prazo, taxa_adm, fundo, lance_pct, prazo_cont):
    taxa_total = (taxa_adm + fundo) / 100
    plano = valor * (1 + taxa_total)
    parcela = plano / prazo
    lance = valor * (lance_pct / 100)
    prob_txt, prob_num = probabilidade_contemplacao(lance_pct)

    return {
        "parcela": parcela,
        "total": plano + lance,
        "lance": lance,
        "credito_liquido": valor - lance,
        "prob": prob_txt,
        "prob_num": prob_num,
        "ranking": ranking_lance(lance_pct),
        "pago_ate_cont": parcela * prazo_cont
    }

# =========================
# FUNÇÕES – FINANCIAMENTO
# =========================
def financiamento_detalhado(valor, taxa, prazo, modelo):
    saldo = valor
    saldos = []
    parcelas = []

    if modelo == "SAC":
        amort = valor / prazo
        for _ in range(prazo):
            juros = saldo * taxa
            parcela = amort + juros
            saldo -= amort
            parcelas.append(parcela)
            saldos.append(max(saldo, 0))
    else:
        parcela_fixa = valor * (taxa * (1 + taxa)**prazo) / ((1 + taxa)**prazo - 1)
        for _ in range(prazo):
            juros = saldo * taxa
            amort = parcela_fixa - juros
            saldo -= amort
            parcelas.append(parcela_fixa)
            saldos.append(max(saldo, 0))

    return parcelas, saldos, sum(parcelas)

# =========================
# INTERFACE
# =========================
st.title("💎 Intelligence Banking – Simulador Profissional")

tab_c, tab_f, tab_comp = st.tabs([
    "🤝 Consórcio",
    "🏦 Financiamento",
    "🔄 Estratégia Comparativa"
])

# =========================
# CONSÓRCIO
# =========================
with tab_c:
    c1, c2 = st.columns([1, 2])

    with c1:
        valor = st.number_input("Valor do Crédito", 100000.0, 3000000.0, 300000.0)
        prazo_c = st.number_input("Prazo", 60, 240, 180)
        taxa_adm = st.number_input("Taxa Administração (%)", 5.0, 30.0, 15.0)
        fundo = st.number_input("Fundo Reserva (%)", 0.0, 5.0, 2.0)
        lance_pct = st.number_input("Lance (%)", 0.0, 100.0, 30.0)
        prazo_cont = st.number_input("Prazo desejado contemplação", 1, prazo_c, 12)

    cons = calcular_consorcio(valor, prazo_c, taxa_adm, fundo, lance_pct, prazo_cont)

    with c2:
        st.markdown(f"""
        <div class="card">
        Parcela: <b>R$ {cons['parcela']:,.2f}</b><br>
        Total estimado: <b>R$ {cons['total']:,.2f}</b><br>
        Crédito líquido: <b>R$ {cons['credito_liquido']:,.2f}</b>
        </div>
        """, unsafe_allow_html=True)

        st.metric("Probabilidade", cons["prob"], f"{cons['prob_num']}%")
        st.metric("Ranking do Lance", cons["ranking"])

# =========================
# FINANCIAMENTO
# =========================
with tab_f:
    f1, f2 = st.columns([1, 2])

    with f1:
        valor_bem = st.number_input("Valor do Bem", 100000.0, 5000000.0, 500000.0)
        entrada = st.number_input("Entrada", 0.0, valor_bem * 0.8, valor_bem * 0.2)
        prazo_f = st.number_input("Prazo (meses)", 12, 420, 240)
        taxa = st.number_input("Taxa mensal (%)", 0.5, 3.0, 1.2) / 100
        modelo = st.selectbox("Sistema", ["Price", "SAC"])

    valor_fin = valor_bem - entrada
    parcelas, saldos, total_pago = financiamento_detalhado(valor_fin, taxa, prazo_f, modelo)

    with f2:
        aba1, aba2 = st.tabs(["📉 Saldo Devedor", "📊 Resumo"])

        with aba1:
            df = pd.DataFrame({"Mês": range(1, prazo_f+1), "Saldo": saldos})
            st.line_chart(df.set_index("Mês"))

        with aba2:
            st.markdown(f"""
            <div class="card">
            Valor financiado: <b>R$ {valor_fin:,.2f}</b><br>
            Parcela inicial: <b>R$ {parcelas[0]:,.2f}</b><br>
            Parcela final: <b>R$ {parcelas[-1]:,.2f}</b><br>
            Total pago: <b>R$ {total_pago:,.2f}</b>
            </div>
            """, unsafe_allow_html=True)

# =========================
# COMPARAÇÃO + RECOMENDAÇÃO
# =========================
with tab_comp:
    score_cons = 0
    score_fin = 0

    if cons["total"] < total_pago: score_cons += 2
    else: score_fin += 2

    if cons["parcela"] < parcelas[0]: score_cons += 1
    else: score_fin += 1

    if prazo_cont <= 24: score_cons += 1
    else: score_fin += 1

    df = pd.DataFrame({
        "Modalidade": ["Consórcio", "Financiamento"],
        "Parcela Inicial": [cons["parcela"], parcelas[0]],
        "Custo Total": [cons["total"], total_pago]
    })

    st.dataframe(df, use_container_width=True)

    if score_cons > score_fin:
        st.success("🎯 Melhor estratégia: **CONSÓRCIO**")
    else:
        st.warning("🎯 Melhor estratégia: **FINANCIAMENTO**")

    st.caption(f"Score Consórcio: {score_cons} | Score Financiamento: {score_fin}")

st.markdown(
    '<div class="footer">Desenvolvido por Victor • Intelligence Banking 2026</div>',
    unsafe_allow_html=True
)















