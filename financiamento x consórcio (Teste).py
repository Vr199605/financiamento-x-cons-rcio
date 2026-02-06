import streamlit as st
import pandas as pd

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
# FUNÇÕES
# =========================

def probabilidade_contemplacao(lance_pct):
    if lance_pct < 10:
        return "Muito Baixa", 10
    elif lance_pct < 20:
        return "Baixa", 25
    elif lance_pct < 30:
        return "Média", 50
    elif lance_pct < 40:
        return "Alta", 75
    else:
        return "Muito Alta", 90


def ranking_lance(lance_pct):
    if lance_pct < 15:
        return "🔴 Pouco competitivo"
    elif lance_pct < 30:
        return "🟡 Competitivo"
    elif lance_pct < 45:
        return "🟢 Muito competitivo"
    else:
        return "🔥 Lance agressivo"


def calcular_consorcio(
    valor_credito,
    prazo,
    taxa_adm,
    fundo_reserva,
    lance_pct,
    prazo_contemplacao
):
    taxa_total = (taxa_adm + fundo_reserva) / 100
    valor_plano = valor_credito * (1 + taxa_total)
    parcela = valor_plano / prazo

    lance = valor_credito * (lance_pct / 100)

    prob_texto, prob_num = probabilidade_contemplacao(lance_pct)
    ranking = ranking_lance(lance_pct)

    credito_liquido_embutido = valor_credito - lance

    return {
        "Parcela": parcela,
        "Valor Plano": valor_plano,
        "Lance": lance,
        "Lance (%)": lance_pct,
        "Probabilidade Texto": prob_texto,
        "Probabilidade Num": prob_num,
        "Ranking": ranking,
        "Prazo Contemplação": prazo_contemplacao,
        "Crédito Líquido Embutido": credito_liquido_embutido
    }


def financiamento_simples(valor_financiado, prazo, taxa_mensal, modelo, amortizacao):
    dados = []
    saldo = valor_financiado

    if modelo == "Price":
        juros_total = saldo * taxa_mensal * prazo
        parcela_base = (saldo + juros_total) / prazo

        for m in range(1, prazo + 1):
            juros = saldo * taxa_mensal
            amort = parcela_base - juros + amortizacao
            saldo -= amort
            dados.append([m, parcela_base + amortizacao, juros, amort, max(saldo, 0)])

    else:  # SAC
        amort_base = saldo / prazo
        for m in range(1, prazo + 1):
            juros = saldo * taxa_mensal
            parcela = amort_base + juros + amortizacao
            saldo -= (amort_base + amortizacao)
            dados.append([m, parcela, juros, amort_base + amortizacao, max(saldo, 0)])

    return pd.DataFrame(dados, columns=[
        "Mês", "Parcela (R$)", "Juros (R$)", "Amortização (R$)", "Saldo Devedor (R$)"
    ])

# =========================
# INTERFACE
# =========================

st.title("💎 Intelligence Banking – Simulador Profissional")

tab_c, tab_f = st.tabs(["🤝 Consórcio", "🏦 Financiamento"])

# =========================
# CONSÓRCIO
# =========================
with tab_c:
    st.header("Simulador de Consórcio")

    c1, c2 = st.columns([1, 2])

    with c1:
        valor_credito = st.number_input(
            "Valor do Crédito (R$)",
            50000.0, 3000000.0, 300000.0, step=5000.0
        )

        prazo_c = st.number_input("Prazo Total (meses)", 60, 240, 180)
        taxa_adm = st.number_input("Taxa de Administração (%)", 5.0, 30.0, 15.0)
        fundo_reserva = st.number_input("Fundo de Reserva (%)", 0.0, 5.0, 2.0)

        lance_pct = st.number_input(
            "Lance (%)",
            min_value=0.0,
            max_value=100.0,
            value=30.0,
            step=0.1
        )

        prazo_contemplacao = st.number_input(
            "Prazo estimado de contemplação (meses)",
            1, prazo_c, 12
        )

    res = calcular_consorcio(
        valor_credito,
        prazo_c,
        taxa_adm,
        fundo_reserva,
        lance_pct,
        prazo_contemplacao
    )

    with c2:
        st.subheader("📌 Pré-Contemplação")
        st.markdown(f"""
        <div class="card">
        • Parcela mensal: <b>R$ {res['Parcela']:,.2f}</b><br>
        • Total pago até contemplação: <b>R$ {res['Parcela'] * res['Prazo Contemplação']:,.2f}</b>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("🚀 Pós-Contemplação")
        st.markdown(f"""
        <div class="card">
        • Crédito contratado: <b>R$ {valor_credito:,.2f}</b><br>
        • Lance ofertado: <b>R$ {res['Lance']:,.2f}</b><br>
        • Lance equivalente: <b>{res['Lance (%)']:.2f}%</b><br>
        • Crédito líquido (lance embutido): <b>R$ {res['Crédito Líquido Embutido']:,.2f}</b>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("📊 Inteligência de Lance")
        st.metric(
            "Probabilidade de Contemplação",
            res["Probabilidade Texto"],
            f"{res['Probabilidade Num']}%"
        )
        st.metric("Ranking do Lance", res["Ranking"])

# =========================
# FINANCIAMENTO
# =========================
with tab_f:
    st.header("Simulador de Financiamento")

    f1, f2 = st.columns([1, 2])

    with f1:
        valor_bem = st.number_input("Valor do Bem (R$)", 100000.0, 5000000.0, 500000.0)
        entrada = st.number_input("Entrada (R$)", 0.0, valor_bem * 0.8, valor_bem * 0.2)
        valor_financiado = valor_bem - entrada

        if valor_financiado > valor_bem * 0.8:
            st.error("⚠️ Financiamento limitado a 80% do valor do bem.")
            st.stop()

        prazo_f = st.number_input("Prazo (meses)", 12, 420, 240)
        taxa_mensal = st.number_input("Taxa de Juros Mensal (%)", 0.5, 3.0, 1.2) / 100
        amortizacao = st.number_input("Amortização Extra Mensal (R$)", 0.0, 50000.0, 0.0)
        modelo = st.selectbox("Sistema de Amortização", ["Price", "SAC"])

    df_fin = financiamento_simples(
        valor_financiado, prazo_f, taxa_mensal, modelo, amortizacao
    )

    with f2:
        st.subheader("📊 Resumo do Financiamento")
        st.metric("Valor Financiado", f"R$ {valor_financiado:,.2f}")
        st.metric("Parcela Inicial", f"R$ {df_fin.iloc[0]['Parcela (R$)']:,.2f}")
        st.metric("Total Pago", f"R$ {df_fin['Parcela (R$)'].sum():,.2f}")

        st.dataframe(df_fin, use_container_width=True)

st.markdown(
    '<div class="footer">Desenvolvido por Victor • Intelligence Banking 2026</div>',
    unsafe_allow_html=True
)






