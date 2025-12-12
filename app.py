import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import re 

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="OSS Analytics", page_icon="🍊", layout="wide", initial_sidebar_state="collapsed")

# PALETTE
ACCENT = "#FF7900"
TEXT_MAIN = "#FFFFFF"
TEXT_SEC = "#A0A0A0"
GRADIENT_END = "#000000"
# Définition des couleurs ici
COLORS = { "LinkedIn": "#0077B5", "Instagram": "#E1306C", "Facebook": "#1877F2", "X": "#FFFFFF" }

# --- 2. CSS & DESIGN ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    .stApp {{
        background: radial-gradient(circle at 50% 0%, #1e293b 0%, {GRADIENT_END} 100%);
        font-family: 'Poppins', sans-serif;
    }}
    
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 95% !important;
    }}
    
    /* Cacher les éléments inutiles */
    [data-testid="stSidebar"] {{display: none;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Masquer le chat et les boutons lors de l'impression PDF */
    @media print {{
        .floating-chat-btn, .chat-window, [data-testid="stForm"], .close-chat-btn, .stButton, button {{
            display: none !important;
        }}
        .block-container {{
            padding: 0 !important;
        }}
    }}

    /* HEADER */
    .glass-header {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 20px 30px;
        margin-bottom: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }}

    /* KPI CARDS */
    .kpi-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 20px;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    .kpi-card:hover {{
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.08);
        border-color: {ACCENT};
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }}
    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, transparent, {ACCENT}, transparent);
        opacity: 0;
        transition: opacity 0.3s;
    }}
    .kpi-card:hover::before {{ opacity: 1; }}

    .kpi-title {{ font-size: 13px; color: {TEXT_SEC}; text-transform: uppercase; letter-spacing: 1px; }}
    .kpi-value {{ font-size: 36px; font-weight: 700; color: {TEXT_MAIN}; margin-top: 5px; text-shadow: 0 2px 10px rgba(0,0,0,0.2); }}
    .kpi-footer {{ display: flex; align-items: center; justify-content: space-between; margin-top: 10px; }}

    .delta-badge {{ padding: 4px 10px; border-radius: 30px; font-size: 12px; font-weight: 600; }}
    .delta-pos {{ background: rgba(16, 185, 129, 0.2); color: #34D399; }}
    .delta-neg {{ background: rgba(239, 68, 68, 0.2); color: #F87171; }}

    /* PODIUM TOP 3 CSS */
    .top3-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }}
    .top3-row:last-child {{ border-bottom: none; }}
    .top3-rank {{ font-weight: 800; color: {ACCENT}; font-size: 18px; margin-right: 15px; width: 25px; }}
    .top3-date {{ color: {TEXT_MAIN}; font-weight: 600; font-size: 14px; }}
    .top3-net {{ color: {TEXT_SEC}; font-size: 12px; margin-left: 5px; font-weight: 400; }}
    .top3-val {{ background: rgba(255,255,255,0.1); padding: 4px 10px; border-radius: 8px; color: {TEXT_MAIN}; font-weight: 700; font-size: 13px; }}

    /* TEXTES */
    h1, h2, h3, h4, h5 {{ color: {TEXT_MAIN} !important; font-weight: 600; }}
    p, label {{ color: {TEXT_SEC} !important; }}
    
    div[data-baseweb="input"] {{
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px !important;
    }}
    
    /* --- CSS BOUTON EXPORT CSV (CONTRASTE BLANC FORCÉ) --- */
    [data-testid="stDownloadButton"] button {{
        background-color: {ACCENT} !important;
        border: 1px solid white !important;
    }}
    /* On cible le texte à l'intérieur du bouton */
    [data-testid="stDownloadButton"] button,
    [data-testid="stDownloadButton"] button * {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }}
    [data-testid="stDownloadButton"] button:hover {{
        background-color: #e65100 !important;
        border-color: #FFFFFF !important;
    }}
    
    /* --- CSS CHATBOT FLOTTANT --- */
    
    /* La fenêtre principale */
    .chat-window {{
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 360px;
        height: 520px;
        background: #0f172a; 
        border: 1px solid {ACCENT};
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
        z-index: 100000;
        display: flex;
        flex-direction: column;
        overflow: hidden;
        animation: slideUp 0.3s ease-out;
    }}
    
    @keyframes slideUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .chat-header {{
        background: linear-gradient(90deg, {ACCENT}, #e65100);
        padding: 15px;
        color: white;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    
    .chat-body {{
        flex: 1;
        overflow-y: auto;
        padding: 15px;
        padding-bottom: 80px; /* Espace pour l'input */
        display: flex;
        flex-direction: column;
        gap: 10px;
    }}
    
    /* Messages */
    .chat-msg {{
        padding: 10px 14px;
        border-radius: 12px;
        font-size: 14px;
        max-width: 85%;
        line-height: 1.4;
    }}
    .bot-msg {{
        background: rgba(255, 255, 255, 0.1);
        color: #eee;
        align-self: flex-start;
        border-bottom-left-radius: 2px;
    }}
    .user-msg {{
        background: {ACCENT};
        color: white;
        align-self: flex-end;
        border-bottom-right-radius: 2px;
    }}
    
    /* Conteneur de l'input (Visual Background) */
    .chat-footer {{
        position: fixed;
        bottom: 100px;
        right: 30px;
        width: 360px;
        height: 70px;
        background: #1e293b;
        border-top: 1px solid rgba(255,255,255,0.1);
        border-radius: 0 0 16px 16px;
        z-index: 100001;
        padding: 10px;
        display: flex;
        align-items: center;
    }}
    
    .chat-footer .stTextInput {{
        width: 100%;
    }}
    .chat-footer input {{
        background: rgba(0,0,0,0.3) !important;
        border: none !important;
        color: white !important;
    }}
    
    /* BOUTON FERMETURE CHAT DANS LE HEADER */
    div.stButton.close-chat-btn {{
        position: fixed;
        bottom: 585px; /* Calculé pour être en haut à droite de la fenêtre */
        right: 45px;
        z-index: 100005;
    }}
    div.stButton.close-chat-btn > button {{
        background: transparent;
        border: none;
        color: white;
        font-size: 18px;
        padding: 0;
        line-height: 1;
        min-height: auto;
    }}
    div.stButton.close-chat-btn > button:hover {{
        color: #ffcccc;
        background: transparent;
    }}

</style>
""", unsafe_allow_html=True)

# --- 3. DATA ---
# 👇👇👇 TON LIEN ICI 👇👇👇
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQpxQxY8LwNpziX-neBxgl3QNBIXFVLvP0xPRYYTXr9IYeC-u707qXfH2iOqP87p8wPtf_xIA3tqOx1/pub?output=csv"

if "TON_LIEN" in sheet_url:
    st.error("🛑 **STOP !** Lien manquant.")
    st.stop()

@st.cache_data(ttl=600)
def load_data():
    try:
        mes_colonnes = ['Date', 'Reseau', 'Impressions', 'Portee', 'Engagements', 'Reactions', 'Interactions', 'Nouveaux Abonnes']
        df = pd.read_csv(sheet_url, header=0, names=mes_colonnes, usecols=range(8), on_bad_lines='skip')
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Date'])
        df = df.fillna(0)
        return df
    except Exception as e:
        return str(e)

df = load_data()
if isinstance(df, str) or df is None:
    st.error(f"⚠️ Erreur: {df}")
    st.stop()

# --- 4. DASHBOARD LOGIC (KPIs, Graphs) ---
c_head1, c_head2 = st.columns([3, 1])
with c_head1:
    st.markdown(f"<h2 style='margin-bottom:20px;'>⚡ Orange Startup Studio <span style='color:{ACCENT}'>Analytics</span></h2>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="glass-header">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 2])
    with c1: start_date = st.date_input("DÉBUT", date(2025, 9, 1))
    with c2: end_date = st.date_input("FIN", date(2025, 11, 30))
    with c3:
        if 'Reseau' in df.columns:
            all = df['Reseau'].unique()
            choix = st.multiselect("RÉSEAUX", all, default=all)
    st.markdown('</div>', unsafe_allow_html=True)

mask_cur = (df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date) & (df['Reseau'].isin(choix))
df_filt = df.loc[mask_cur].sort_values(by='Date')

duree = (end_date - start_date).days
prev_s = start_date - timedelta(days=duree + 1)
prev_e = start_date - timedelta(days=1)
mask_prv = (df['Date'].dt.date >= prev_s) & (df['Date'].dt.date <= prev_e) & (df['Reseau'].isin(choix))
df_prev = df.loc[mask_prv]

if not df_filt.empty:
    def get_kpi(col):
        v = df_filt[col].sum()
        p = df_prev[col].sum()
        d = ((v - p) / p * 100) if p > 0 else 0
        return int(v), d

    imp, d_imp = get_kpi('Impressions')
    por, d_por = get_kpi('Portee')
    eng, d_eng = get_kpi('Engagements')
    abo, d_abo = get_kpi('Nouveaux Abonnes')
    
    taux = (eng / imp * 100) if imp > 0 else 0
    taux_p = (df_prev['Engagements'].sum() / df_prev['Impressions'].sum() * 100) if df_prev['Impressions'].sum() > 0 else 0
    d_taux = taux - taux_p

    def kpi_html(icon, label, val, delta, is_pct=False):
        sign = "+" if delta >= 0 else ""
        cls = "delta-pos" if delta >= 0 else "delta-neg"
        d_val = f"{sign}{delta:.1f}%" if not is_pct else f"{sign}{delta:.2f} pts"
        return f"""<div class="kpi-card"><div class="kpi-title">{label}</div><div class="kpi-value">{val}</div><div class="kpi-footer"><div style="font-size:20px;">{icon}</div><div class="delta-badge {cls}">{d_val}</div></div></div>"""

    cols = st.columns(5)
    with cols[0]: st.markdown(kpi_html("👁️", "Impressions", f"{imp:,}".replace(",", " "), d_imp), unsafe_allow_html=True)
    with cols[1]: st.markdown(kpi_html("📢", "Portée", f"{por:,}".replace(",", " "), d_por), unsafe_allow_html=True)
    with cols[2]: st.markdown(kpi_html("❤️", "Engagements", f"{eng:,}".replace(",", " "), d_eng), unsafe_allow_html=True)
    with cols[3]: st.markdown(kpi_html("👥", "Nouveaux Abonnés", f"{abo:,}".replace(",", " "), d_abo), unsafe_allow_html=True)
    with cols[4]: st.markdown(kpi_html("📈", "Taux d'Engag.", f"{taux:.2f}%", d_taux, is_pct=True), unsafe_allow_html=True)

    st.markdown("###")
    df_top3 = df_filt.nlargest(3, 'Engagements')[['Date', 'Reseau', 'Engagements']]
    
    def make_chart_transparent(fig):
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Poppins", color="#E0E0E0"), margin=dict(l=0, r=0, t=40, b=0), hovermode="x unified")
        fig.update_xaxes(showgrid=False, showline=False)
        fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.05)', zeroline=False)
        return fig

    c_g1, c_g2 = st.columns([2, 1])
    with c_g1:
        st.markdown("##### 📈 Croissance de la Communauté")
        df_cum = df_filt.copy()
        df_cum['Cumul'] = df_cum.groupby('Reseau')['Nouveaux Abonnes'].cumsum()
        fig = px.area(df_cum, x='Date', y='Cumul', color='Reseau', color_discrete_map=COLORS)
        fig.update_traces(line_shape='spline', fill='tozeroy')
        st.plotly_chart(make_chart_transparent(fig), use_container_width=True)

    with c_g2:
        st.markdown("##### 🏆 Top 3 Meilleurs Jours")
        html_top3 = ""
        for index, row in df_top3.iterrows():
            date_fmt = row['Date'].strftime('%d %b')
            html_top3 += f"""<div class="top3-row"><div style="display:flex; align-items:center;"><span class="top3-rank">#{list(df_top3.index).index(index)+1}</span><span class="top3-date">{date_fmt}</span><span class="top3-net">({row['Reseau']})</span></div><div class="top3-val">{int(row['Engagements'])} Eng.</div></div>"""
        st.markdown(f"""<div class="kpi-card" style="height:auto; min-height:300px;">{html_top3}<div style="margin-top:20px; font-size:12px; color:#AAA; text-align:center;">Basé sur le volume d'interactions</div></div>""", unsafe_allow_html=True)

    st.markdown("###")
    c_g3, c_g4 = st.columns([1, 1])
    with c_g3:
        st.markdown("##### 🍩 Répartition")
        fig = px.pie(df_filt, values='Impressions', names='Reseau', color='Reseau', color_discrete_map=COLORS, hole=0.7)
        fig.update_traces(textinfo='percent', textfont_size=14, marker=dict(line=dict(color='#000000', width=2)))
        st.plotly_chart(make_chart_transparent(fig), use_container_width=True)
    with c_g4:
        st.markdown("##### 📊 Impressions")
        fig = px.line(df_filt, x='Date', y='Impressions', color='Reseau', color_discrete_map=COLORS)
        fig.update_traces(line_shape='spline', line_width=4)
        st.plotly_chart(make_chart_transparent(fig), use_container_width=True)

    # --- 10. DATA & EXPORT ---
    st.markdown("###")
    c_data, c_btn = st.columns([4, 1])
    with c_data: st.markdown("##### 📑 Données détaillées")
    with c_btn:
        csv = df_filt.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exporter CSV", data=csv, file_name="reporting_oss.csv", mime="text/csv", type="primary", use_container_width=True)

    tab1, tab2 = st.tabs(["🗓️ Mensuel", "🔎 Journalier"])
    with tab1:
        df_m = df_filt.copy()
        df_m['Mois'] = df_m['Date'].dt.strftime('%Y-%m')
        grp = df_m.groupby(['Mois', 'Reseau'])[['Impressions', 'Portee', 'Engagements', 'Nouveaux Abonnes', 'Interactions']].sum().reset_index()
        grp["Taux"] = grp.apply(lambda x: (x['Engagements']/x['Impressions']*100) if x['Impressions']>0 else 0, axis=1).apply(lambda x: f"{x:.2f} %")
        st.dataframe(grp, use_container_width=True)
    with tab2:
        st.dataframe(df_filt, use_container_width=True)


    # --- 11. CHATBOT FLOTTANT INTÉGRÉ ---

    # Etat du chat
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [{"role": "bot", "msg": "👋 Hello ! Je suis l'Assistant OSS. Posez-moi une question !"}]

    def toggle_chat():
        st.session_state.chat_open = not st.session_state.chat_open

    # Intelligence Artificielle (Simplifiée)
    def agent_oss(question, df_source):
        q = question.lower()
        filter_net = None
        if "linkedin" in q: filter_net = "LinkedIn"
        elif "instagram" in q: filter_net = "Instagram"
        elif "facebook" in q: filter_net = "Facebook"
        elif "x" in q or "twitter" in q: filter_net = "X"
        
        df_chat = df_source[df_source['Reseau'] == filter_net] if filter_net else df_source
        net_name = filter_net if filter_net else "tous les réseaux"
        response = "Je ne suis pas sûr. Essayez 'Impressions', 'Engagements', 'Abonnés' ou 'Meilleur jour'."
        
        if "impression" in q or "vue" in q:
            val = int(df_chat['Impressions'].sum())
            response = f"👀 Total **Impressions** ({net_name}) : **{val:,}**.".replace(",", " ")
        elif "engagement" in q or "reac" in q or "like" in q:
            val = int(df_chat['Engagements'].sum())
            response = f"❤️ Total **Engagements** ({net_name}) : **{val:,}**.".replace(",", " ")
        elif "abonne" in q or "suivi" in q or "follower" in q:
            val = int(df_chat['Nouveaux Abonnes'].sum())
            response = f"👥 Nouveaux **Abonnés** ({net_name}) : **{val:,}**.".replace(",", " ")
        elif "meilleur" in q or "top" in q or "record" in q:
            if not df_chat.empty:
                best = df_chat.loc[df_chat['Engagements'].idxmax()]
                response = f"🏆 Record le **{best['Date'].strftime('%d %b')}** sur **{best['Reseau']}** : **{int(best['Engagements'])} Eng.**"
            else:
                response = "Pas assez de données."
        elif "portée" in q or "reach" in q:
            val = int(df_chat['Portee'].sum())
            response = f"📢 **Portée** (Reach) : **{val:,}**.".replace(",", " ")
        return response

    # --- AFFICHAGE DE LA FENÊTRE DE CHAT (Si ouverte) ---
    if st.session_state.chat_open:
        # BOUTON FERMETURE EXPLICITE (Top Right)
        # On utilise une colonne fictive pour le placer via CSS
        c_close = st.container()
        with c_close:
            st.markdown('<div class="stButton close-chat-btn">', unsafe_allow_html=True)
            if st.button("✖", key="close_chat_x"):
                st.session_state.chat_open = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # 1. Structure HTML de la fenêtre (Header + Messages)
        chat_html = ""
        for chat in st.session_state.chat_history:
            cls = "bot-msg" if chat["role"] == "bot" else "user-msg"
            chat_html += f'<div class="chat-msg {cls}">{chat["msg"]}</div>'
        
        st.markdown(f"""
        <div class="chat-window">
            <div class="chat-header">
                <span>🤖 Assistant OSS</span>
            </div>
            <div class="chat-body">
                {chat_html}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 2. Zone d'Input (Widget Streamlit)
        with st.container():
            st.markdown('<div class="chat-footer">', unsafe_allow_html=True)
            with st.form(key="chat_form", clear_on_submit=True):
                col_in, col_sub = st.columns([5, 1])
                with col_in:
                    user_input = st.text_input("", placeholder="Posez une question...", label_visibility="collapsed")
                with col_sub:
                    submit = st.form_submit_button("➤")
            st.markdown('</div>', unsafe_allow_html=True)

            if submit and user_input:
                st.session_state.chat_history.append({"role": "user", "msg": user_input})
                bot_resp = agent_oss(user_input, df_filt)
                st.session_state.chat_history.append({"role": "bot", "msg": bot_resp})
                st.rerun()

    # --- BOUTON FLOTTANT (FAB) ---
    c_fab = st.container()
    with c_fab:
        st.markdown("""
        <style>
            div.stButton.fab-btn > button {
                position: fixed;
                bottom: 30px;
                right: 30px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #FF7900, #FF4500);
                color: white;
                font-size: 24px;
                border: none;
                box-shadow: 0 4px 20px rgba(255, 121, 0, 0.4);
                z-index: 999999;
                transition: transform 0.2s;
            }
            div.stButton.fab-btn > button:hover {
                transform: scale(1.1);
            }
        </style>
        """, unsafe_allow_html=True)
        
        # Le bouton FAB affiche 💬 quand fermé, et rien quand ouvert (car la fenêtre a sa propre croix)
        # Ou on peut laisser le FAB pour rouvrir si on ferme
        if not st.session_state.chat_open:
            st.markdown('<div class="stButton fab-btn">', unsafe_allow_html=True)
            if st.button("💬", key="open_chat_fab"):
                toggle_chat()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Quand ouvert, on peut aussi afficher le FAB en mode "Fermer" si on veut
            # Mais ici on a mis la croix en haut
            st.markdown('<div class="stButton fab-btn">', unsafe_allow_html=True)
            if st.button("❌", key="close_chat_fab"):
                toggle_chat()
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Sélectionnez une période.")
