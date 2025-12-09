import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta

# --- 1. CONFIGURATION & STYLE ---
st.set_page_config(page_title="Reporting Social Media", page_icon="📊", layout="wide")

st.markdown("""
<style>
    @media print {
        [data-testid="stSidebar"], section[data-testid="stSidebar"],
        header, footer, #MainMenu {display: none !important;}
        .block-container {padding-top: 1rem !important; padding-bottom: 1rem !important;}
    }
</style>
""", unsafe_allow_html=True)

couleurs_reseaux = {
    "LinkedIn": "#0077B5",
    "Instagram": "#E1306C",
    "Facebook": "#1877F2",
    "X": "#000000"
}

# --- 2. CHARGEMENT DES DONNÉES ---
# 👇👇👇 COLLE TON LIEN CSV ICI 👇👇👇
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpxQxY8LwNpziX-neBxgl3QNBIXFVLvP0xPRYYTXr9IYeC-u707qXfH2iOqP87p8wPtf_xIA3tqOx1/pub?output=csv"

try:
    mes_colonnes = ['Date', 'Reseau', 'Impressions', 'Portee', 'Engagements', 'Reactions', 'Interactions', 'Nouveaux Abonnes']
    
    df = pd.read_csv(
        sheet_url, 
        header=0, 
        names=mes_colonnes, 
        usecols=range(8), 
        on_bad_lines='skip'
    )
    
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date'])
    df = df.fillna(0)

except Exception as e:
    st.error(f"⚠️ Erreur de chargement : {e}")
    st.stop()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🎛️ Pilotage")
    st.header("📅 Période")
    start_date = st.date_input("Du", date(2025, 9, 1))
    end_date = st.date_input("Au", date(2025, 11, 30))
    
    st.header("📱 Réseaux")
    if 'Reseau' in df.columns:
        all_reseaux = df['Reseau'].unique()
        choix_reseaux = st.multiselect("Filtrer :", all_reseaux, default=all_reseaux)
    else:
        st.stop()

# --- 4. CALCULS ---
mask_current = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date) & (df['Reseau'].isin(choix_reseaux))
df_filtered = df.loc[mask_current].sort_values(by='Date')

# Calcul Période Précédente
duree = (end_date - start_date).days
prev_start = start_date - timedelta(days=duree + 1)
prev_end = start_date - timedelta(days=1)
mask_prev = (df['Date'].dt.date >= prev_start) & (df['Date'].dt.date <= prev_end) & (df['Reseau'].isin(choix_reseaux))
df_prev = df.loc[mask_prev]

st.title("📊 Météo Social Media")
st.markdown(f"**Période du {start_date.strftime('%d/%m/%Y')} au {end_date.strftime('%d/%m/%Y')}**")
st.caption(f"Comparaison avec la période précédente ({prev_start.strftime('%d/%m')} - {prev_end.strftime('%d/%m')})")
st.markdown("---")

if not df_filtered.empty:
    def calcul_kpi(colonne):
        valeur_actuelle = df_filtered[colonne].sum()
        valeur_precedente = df_prev[colonne].sum()
        delta = 0
        if valeur_precedente > 0:
            delta = ((valeur_actuelle - valeur_precedente) / valeur_precedente) * 100
        return int(valeur_actuelle), delta

    imp, d_imp = calcul_kpi('Impressions')
    por, d_por = calcul_kpi('Portee')
    eng, d_eng = calcul_kpi('Engagements')
    abo, d_abo = calcul_kpi('Nouveaux Abonnes')
    
    taux_actuel = (eng / imp * 100) if imp > 0 else 0
    taux_prev = (df_prev['Engagements'].sum() / df_prev['Impressions'].sum() * 100) if df_prev['Impressions'].sum() > 0 else 0
    d_taux = taux_actuel - taux_prev

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👁️ Impressions", f"{imp:,}".replace(",", " "), f"{d_imp:.1f}%")
    c2.metric("📢 Portée", f"{por:,}".replace(",", " "), f"{d_por:.1f}%")
    c3.metric("❤️ Engagements", f"{eng:,}".replace(",", " "), f"{d_eng:.1f}%")
    c4.metric("➕ Nouveaux Abonnés", f"{abo:,}".replace(",", " "), f"{d_abo:.1f}%")
    c5.metric("📈 Taux d'Engag.", f"{taux_actuel:.2f} %", f"{d_taux:.2f} pts")

    st.markdown("###")

    # --- 5. GRAPHIQUES ---
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("📈 Croissance Cumulée (Abonnés)")
        df_cumul = df_filtered.copy()
        df_cumul['Cumul'] = df_cumul.groupby('Reseau')['Nouveaux Abonnes'].cumsum()
        fig_abo = px.area(df_cumul, x='Date', y='Cumul', color='Reseau', color_discrete_map=couleurs_reseaux)
        st.plotly_chart(fig_abo, use_container_width=True)

    with g2:
        st.subheader("📊 Activité Quotidienne (Impressions)")
        fig_evol = px.line(df_filtered, x='Date', y='Impressions', color='Reseau', color_discrete_map=couleurs_reseaux)
        st.plotly_chart(fig_evol, use_container_width=True)
    
    b1, b2 = st.columns(2)
    with b1:
         st.subheader("Répartition des Impressions")
         fig_pie = px.pie(df_filtered, values='Impressions', names='Reseau', color='Reseau', color_discrete_map=couleurs_reseaux, hole=0.5)
         st.plotly_chart(fig_pie, use_container_width=True)
    with b2:
        st.subheader("Engagement Total")
        fig_bar = px.bar(df_filtered, x='Reseau', y='Engagements', color='Reseau', text_auto='.2s', color_discrete_map=couleurs_reseaux)
        st.plotly_chart(fig_bar, use_container_width=True)

    # --- 6. TABLEAUX DE DONNÉES ---
    st.markdown("---")
    st.subheader("📑 Données détaillées")

    # PRÉPARATION DES DONNÉES DÉTAILLÉES (Avec Taux %)
    df_detail = df_filtered.copy()
    # Calcul
    df_detail["Taux d'engagement"] = 0.0
    mask_nz = df_detail['Impressions'] > 0
    df_detail.loc[mask_nz, "Taux d'engagement"] = (df_detail.loc[mask_nz, 'Engagements'] / df_detail.loc[mask_nz, 'Impressions']) * 100
    # Formatage
    df_detail["Taux d'engagement"] = df_detail["Taux d'engagement"].apply(lambda x: f"{x:.2f} %")

    # Onglet 1 : Données Brutes (Jour par Jour)
    with st.expander("🔎 Voir les données brutes (Jour par Jour)"):
        st.dataframe(df_detail, use_container_width=True)

    # Onglet 2 : Données Mensuelles (Récap)
    with st.expander("🗓️ Voir le cumul par Mois (Récapitulatif)"):
        df_mois = df_filtered.copy()
        df_mois['Mois'] = df_mois['Date'].dt.strftime('%Y-%m')
        
        # Somme
        df_groupe = df_mois.groupby(['Mois', 'Reseau'])[['Impressions', 'Portee', 'Engagements', 'Nouveaux Abonnes', 'Interactions']].sum().reset_index()
        
        # Calcul Taux
        df_groupe["Taux d'engagement"] = 0.0
        mask_non_zero = df_groupe['Impressions'] > 0
        df_groupe.loc[mask_non_zero, "Taux d'engagement"] = (df_groupe.loc[mask_non_zero, 'Engagements'] / df_groupe.loc[mask_non_zero, 'Impressions']) * 100
        # Formatage
        df_groupe["Taux d'engagement"] = df_groupe["Taux d'engagement"].apply(lambda x: f"{x:.2f} %")

        st.dataframe(df_groupe, use_container_width=True)

else:
    st.warning("Aucune donnée pour cette sélection.")