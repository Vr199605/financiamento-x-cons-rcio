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
.stMetric {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
}
.footer {
    position: fixed;
    bottom: 0;
    width: 100%;
    text-align: center;
    color: gray;
    padding: 10px;
}
h1, h2, h3 { color: #1e3a8a; }
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES DE CÁLCULO
# =========================

def calcular_consorcio(
    valor_credito,
    prazo,
    taxa_adm,
    fundo_reserva,
    percentual_lance,
    tipo_lance,
    tipo_abate
):
    taxa_total = (taxa_adm + fundo_reserva) / 100
    valor_lance = valor_credito * (percentual_lance / 100)
    valor_plano = valor_credito * (1 + taxa_total)

    saldo_devedor = valor_plano - valor_lance

    if tipo_abate == "Reduz Parcela":
        parcela = saldo_devedor / prazo
        prazo_final = prazo
    else:
        parcela_base = valor_plano / prazo
        prazo_final = int(saldo_devedor / parcela_base)
        parcela = parcela_base

    custo_percentual = (valor_plano / valor_credito - 1) * 100

    return {
        "Tipo Lance": tipo_lance,
        "Lance (R$)": valor_lance,
        "Crédito (R$)": valor_credito,
        "Total do Plano (R$)": valor_plano,
        "Saldo Pós-Lance (R$)": saldo_devedor,
        "Parcela (R$)": parcela,
        "Prazo Final (meses)": prazo_final,
        "Custo Total (%)": custo_percentual
    }

def fluxo_consorcio(parcela, prazo):
    meses = list(range(1, prazo + 1))
    total_pago = [parcela * m for m in meses]

    return pd.DataFrame({
        "Mês": meses,
        "Parcela (R$)": parcela,
        "Total Pago (R$)": total_pago
    })

def calcular_financiamento(valor, prazo, taxa_anual, seguro_pct):
    taxa_mensal = (1 + taxa_anual/100) ** (1/12) - 1

    parcela = valor * (taxa_mensal * (1 + taxa_mensal)**prazo) / ((1 + taxa_mensal)**prazo - 1)
    total = parcela * prazo
    juros = total - valor
    seguro = valor * (seguro_pct / 100)
    total_geral = total + seguro

    return {
        "Parcela (R$)": parcela,
        "Total Pago (R$)": total_geral,
        "Juros (R$)": juros,
        "Seguro (R$)": seguro,
        "Taxa Mensal (%)": taxa_mensal * 100
    }

# =========================
# INTERFACE PRINCIPAL
# =========================

st.title("💎 Intelligence Banking – Simulador Profissional")
st.markdown("Comparação estratégica entre **Consórcio x Financiamento**, no padrão dos grandes bancos.")

tab_consorcio, tab_financiamento, tab_proposta = st.tabs([
    "🤝 Simulador de Consórcio",
    "🏦 Simulador de Financiamento",
    "📄 Proposta Executiva"
])

# =========================
# ABA CONSÓRCIO
# =========================
with tab_consorcio:
    st.header("Simulação de Consórcio")

    c1, c2 = st.columns([1, 2])

    with c1:
        valor_credito = st.number_input("Valor do Crédito (R$)", 10000.0, 5000000.0, 150000.0, step=5000.0)
        prazo = st.number_input("Prazo (meses)", 12, 240, 180)
        taxa_adm = st.number_input("Taxa de Administração (%)", 5.0, 30.0, 15.0, step=0.1)
        fundo_reserva = st.number_input("Fundo de Reserva (%)", 0.0, 5.0, 2.0, step=0.1)

        tipo_lance = st.selectbox(
            "Tipo de Lance",
            ["Sorteio", "Lance Fixo", "Lance Livre", "Lance Embutido"]
        )

        percentual_lance = st.slider("Percentual de Lance (%)", 0.0, 100.0, 30.0)
        tipo_abate = st.radio("Como o lance será utilizado?", ["Reduz Parcela", "Reduz Prazo"])

    res_c = calcular_consorcio(
        valor_credito,
        prazo,
        taxa_adm,
        fundo_reserva,
        percentual_lance,
        tipo_lance,
        tipo_abate
    )

    with c2:
        st.subheader("📊 Resultado do Consórcio")

        m1, m2, m3 = st.columns(3)
        m1.metric("Parcela", f"R$ {res_c['Parcela (R$)']:,.2f}")
        m2.metric("Lance", f"R$ {res_c['Lance (R$)']:,.2f}")
        m3.metric("Prazo Final", f"{res_c['Prazo Final (meses)']} meses")

        st.info(
            f"O custo total do consórcio representa "
            f"{res_c['Custo Total (%)']:.2f}% acima do valor do bem."
        )

        df_c = pd.DataFrame([res_c])
        st.dataframe(df_c.style.format({
            "Lance (R$)": "R$ {:,.2f}",
            "Crédito (R$)": "R$ {:,.2f}",
            "Total do Plano (R$)": "R$ {:,.2f}",
            "Saldo Pós-Lance (R$)": "R$ {:,.2f}",
            "Parcela (R$)": "R$ {:,.2f}",
            "Custo Total (%)": "{:.2f}%"
        }), use_container_width=True)

        st.subheader("📈 Fluxo Financeiro")
        df_fluxo = fluxo_consorcio(res_c["Parcela (R$)"], res_c["Prazo Final (meses)"])
        st.dataframe(df_fluxo, use_container_width=True)

# =========================
# ABA FINANCIAMENTO
# =========================
with tab_financiamento:
    st.header("Simulação de Financiamento Bancário")

    f1, f2 = st.columns([1, 2])

    with f1:
        valor_bem = st.number_input("Valor do Bem (R$)", value=valor_credito)
        prazo_f = st.number_input("Prazo (meses)", value=prazo)
        taxa_anual = st.number_input("Taxa de Juros Anual (%)", 5.0, 30.0, 12.0, step=0.1)
        seguro_pct = st.number_input("Seguro (% sobre o bem)", 0.0, 5.0, 1.5, step=0.1)

    res_f = calcular_financiamento(valor_bem, prazo_f, taxa_anual, seguro_pct)

    with f2:
        st.subheader("📊 Resultado do Financiamento")

        n1, n2, n3 = st.columns(3)
        n1.metric("Parcela", f"R$ {res_f['Parcela (R$)']:,.2f}")
        n2.metric("Total Pago", f"R$ {res_f['Total Pago (R$)']:,.2f}")
        n3.metric("Juros", f"R$ {res_f['Juros (R$)']:,.2f}", delta_color="inverse")

        st.warning(
            f"No financiamento, o custo em juros e seguros soma "
            f"R$ {(res_f['Total Pago (R$)'] - valor_bem):,.2f}."
        )

# =========================
# ABA PROPOSTA
# =========================
with tab_proposta:
    st.header("📄 Proposta Executiva")

    p1, p2 = st.columns(2)

    with p1:
        cliente = st.text_input("Nome do Cliente")
        administradora = st.selectbox(
            "Administradora",
            ["Porto", "Klubi", "Servopa", "Itaú", "CNP", "Ademicon"]
        )

    with p2:
        consultor = st.text_input("Consultor Responsável")

    economia = res_f["Total Pago (R$)"] - res_c["Total do Plano (R$)"]

    proposta = f"""
==================================================
PROPOSTA ESTRATÉGICA – {administradora.upper()}
==================================================

CLIENTE: {cliente}
CONSULTOR: {consultor}

RESUMO EXECUTIVO
• Economia estimada: R$ {economia:,.2f}
• Menor custo total e maior flexibilidade
• Estratégia personalizada de contemplação

CENÁRIO CONSÓRCIO
• Parcela: R$ {res_c['Parcela (R$)']:,.2f}
• Prazo Final: {res_c['Prazo Final (meses)']} meses
• Custo Total: R$ {res_c['Total do Plano (R$)']:,.2f}
• Lance: R$ {res_c['Lance (R$)']:,.2f}

CENÁRIO FINANCIAMENTO
• Parcela: R$ {res_f['Parcela (R$)']:,.2f}
• Custo Total: R$ {res_f['Total Pago (R$)']:,.2f}

==================================================
Gerado pelo Intelligence Banking • 2026
"""

    st.text_area("Pré-visualização da Proposta", proposta, height=350)

    st.download_button(
        "📥 Exportar Proposta (.TXT)",
        proposta,
        file_name=f"Proposta_{cliente.replace(' ', '_')}.txt",
        mime="text/plain"
    )

st.markdown(
    '<div class="footer">Desenvolvido por Victor • Intelligence Banking 2026</div>',
    unsafe_allow_html=True
)
