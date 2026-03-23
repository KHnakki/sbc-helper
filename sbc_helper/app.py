import streamlit as st
import pandas as pd

st.set_page_config(page_title="SBC Helper", layout="wide")
st.title("⚽ SBC Helper")

with st.expander("📖 Ohjeet", expanded=False):
    st.markdown("""
    1. **Lataa Data:** Hae Web Appista (Club / SBC Storage) CSV-tiedosto esim. FC Enhancerilla.
    2. **Tiedoston siirto:** Raahaa `.csv`-tiedostot alla olevaan laatikkoon.
    3. **Älykäs Ratkaisija:** Valitse tarvittavat tiimit. Algoritmi etsii automaattisesti klubisi varastolle **parhaan ja halvimman** reseptin!
    """)

uploaded_files = st.file_uploader("Lataa CSV-tiedostot", type="csv", accept_multiple_files=True)

if uploaded_files:
    dataframes = []
    for file in uploaded_files:
        temp_df = pd.read_csv(file)
        temp_df['Sijainti'] = 'SBC Storage' if 'storage' in file.name.lower() else 'Klubi'
        dataframes.append(temp_df)
    df = pd.concat(dataframes, ignore_index=True)

    def maarita_laatu(row):
        rarity, rating = row['Rarity'], row['Rating']
        if rarity == 'Team of the Week': return 'TOTW'
        elif rarity not in ['Common', 'Rare']: return 'Special'
        return 'Gold' if rating >= 75 else ('Silver' if rating >= 65 else 'Bronze')
    df['Quality'] = df.apply(maarita_laatu, axis=1)
    df['Card Type'] = df['Rarity'].apply(lambda x: x if x in ['Common', 'Rare'] else '-')

    # --- YLÄOSAN YHTEENVETO ---
    st.header("📊 Pika-katsaus")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Klubissa yhteensä", len(df[df['Sijainti'] == 'Klubi']))
    col2.metric("SBC Storagessa", len(df[df['Sijainti'] == 'SBC Storage']))
    col3.metric("Gold (Kaikki)", len(df[df['Quality'] == 'Gold']))
    col4.metric("Special", len(df[df['Quality'].isin(['Special', 'TOTW'])]))

    # --- ÄLYKÄS RATKAISIJA (PIILOTETTU EXPANDERIN TAAKSE) ---
    st.divider()
    st.header("SBC-Ratkaisija")
    
    with st.expander("🔽 Avaa Älykäs Ratkaisija tästä", expanded=False):
        st.write("Valitse tarvittavat squadit. Algoritmi valitsee automaattisesti sen reseptin, joka maksimoi omien korttiesi käytön ja säästää parhaat korttisi.")

        # Laajennettu ja OPTIMOITU reseptikirjasto (Vain kannattavat vaihtoehdot!)
        resepti_kirjasto = {
            "84": [
                {"nimi": "Yksi 86 (Halvin)", "vaatimukset": {86: 1, 84: 1, 83: 9}},
                {"nimi": "Kaksi 85 (Vaihtoehto)", "vaatimukset": {85: 2, 84: 2, 83: 7}},
                {"nimi": "Yksi 87 (Super-korkea carry)", "vaatimukset": {87: 1, 83: 10}},
                {"nimi": "Neljä 84 (Tasaisempi)", "vaatimukset": {85: 1, 84: 4, 83: 6}}
            ],
            "85": [
                {"nimi": "Yksi 87 (Halvin)", "vaatimukset": {87: 1, 85: 2, 83: 8}},
                {"nimi": "Kaksi 86 (Vaihtoehto)", "vaatimukset": {86: 2, 85: 3, 84: 6}},
                {"nimi": "Yksi 88 (Super-korkea carry)", "vaatimukset": {88: 1, 84: 10}},
                {"nimi": "Kolme 86 (Säästä 85-kortit)", "vaatimukset": {86: 3, 84: 8}}
            ],
            "86": [
                {"nimi": "Kaksi isoa (Säästä 86-kortit)", "vaatimukset": {88: 1, 87: 1, 84: 9}},
                {"nimi": "Futbin suosikki (Säästä 88-kortit)", "vaatimukset": {87: 4, 86: 1, 84: 6}},
                {"nimi": "Yksi 89 (Super-korkea carry)", "vaatimukset": {89: 1, 85: 10}},
                {"nimi": "Kolme 87 (Säästä 86-kortit)", "vaatimukset": {87: 3, 85: 8}}
            ],
            "87": [
                {"nimi": "Kaksi 89 (Säästä 87-kortit)", "vaatimukset": {89: 2, 88: 1, 84: 8}},
                {"nimi": "Kolme 88 (Säästä 89-kortit)", "vaatimukset": {88: 3, 87: 3, 86: 5}},
                {"nimi": "Yksi 90 (Super-korkea carry)", "vaatimukset": {90: 1, 86: 10}},
                {"nimi": "Viisi 88 (Säästä 89 ja 87)", "vaatimukset": {88: 5, 86: 6}}
            ],
            "88": [
                {"nimi": "Kaksi 90 (Korkeat tähtipelaajat)", "vaatimukset": {90: 2, 89: 1, 85: 8}},
                {"nimi": "Neljä 89 (Tasaisempi profiili)", "vaatimukset": {89: 4, 88: 3, 87: 4}},
                {"nimi": "Yksi 91 (Super-korkea carry)", "vaatimukset": {91: 1, 87: 10}},
                {"nimi": "Kolme 90 (Säästä 89-kortit)", "vaatimukset": {90: 3, 87: 8}}
            ],
            "89": [
                {"nimi": "Kaksi 91 (Korkeat tähtipelaajat)", "vaatimukset": {91: 2, 90: 1, 86: 8}},
                {"nimi": "Neljä 90 (Tasaisempi profiili)", "vaatimukset": {90: 4, 89: 3, 88: 4}},
                {"nimi": "Yksi 92 (Super-korkea carry)", "vaatimukset": {92: 1, 88: 10}},
                {"nimi": "Kolme 91 (Säästä 90-kortit)", "vaatimukset": {91: 3, 88: 8}}
            ]
        }

        # Käyttäjän valinnat
        squad_cols = st.columns(len(resepti_kirjasto))
        valitut_squadit = []
        
        for i, squad in enumerate(resepti_kirjasto.keys()):
            with squad_cols[i]:
                maara = st.number_input(f"{squad} Squad", min_value=0, max_value=10, value=0, step=1)
                for _ in range(maara):
                    valitut_squadit.append(squad)

        st.write("Asetukset:")
        col_set1, col_set2 = st.columns(2)
        with col_set1:
            vain_untr_proj = st.checkbox("Käytä vain Untradeable-pelaajia", value=True)
        with col_set2:
            vain_kulta_proj = st.checkbox("Käytä vain Kultapelaajia (Säästä Special/TOTW)", value=False)

        if valitut_squadit:
            # Suodatetaan sallitut pelaajat
            sallitut_df = df.copy()
            if vain_untr_proj: sallitut_df = sallitut_df[sallitut_df['Untradeable'] == True]
            if vain_kulta_proj: sallitut_df = sallitut_df[sallitut_df['Quality'] == 'Gold']

            varasto = sallitut_df['Rating'].value_counts().to_dict()

            st.write("### 🤖 Algoritmin tulokset:")
            valitut_squadit.sort(reverse=True)

            for squad in valitut_squadit:
                paras_resepti = None
                pienin_puuttuu = 999
                pienin_maksimi_rating = 999
                
                for resepti in resepti_kirjasto[squad]:
                    puuttuu_yhteensa = 0
                    max_rating = max(resepti['vaatimukset'].keys())
                    
                    for r, tarve in resepti['vaatimukset'].items():
                        loytyy = varasto.get(r, 0)
                        if loytyy < tarve:
                            puuttuu_yhteensa += (tarve - loytyy)
                    
                    if puuttuu_yhteensa < pienin_puuttuu:
                        paras_resepti = resepti
                        pienin_puuttuu = puuttuu_yhteensa
                        pienin_maksimi_rating = max_rating
                    elif puuttuu_yhteensa == pienin_puuttuu and max_rating < pienin_maksimi_rating:
                        paras_resepti = resepti
                        pienin_maksimi_rating = max_rating

                with st.container():
                    st.info(f"**{squad} Squad** ➔ Valittu strategia: **{paras_resepti['nimi']}**")
                    
                    resepti_cols = st.columns(len(paras_resepti['vaatimukset']))
                    i = 0
                    for r_vaatimus, kpl_tarve in sorted(paras_resepti['vaatimukset'].items(), reverse=True):
                        loytyy_varastosta = varasto.get(r_vaatimus, 0)
                        kaytetaan = min(loytyy_varastosta, kpl_tarve)
                        puuttuu_nyt = kpl_tarve - kaytetaan
                        
                        varasto[r_vaatimus] = loytyy_varastosta - kaytetaan
                        
                        with resepti_cols[i]:
                            if puuttuu_nyt == 0:
                                st.success(f"**{r_vaatimus} Rating** (Tarve: {kpl_tarve}) ✅")
                            else:
                                st.error(f"**{r_vaatimus} Rating** (Tarve: {kpl_tarve}) ❌ Puuttuu: {puuttuu_nyt}")
                        i += 1

    # --- PERUSVARASTON LISTAUS (Pysyy samana) ---
    st.divider()
    st.header("🔍 Tarkka varaston haku")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1: valittu_laatu = st.selectbox("1. Valitse kortin laatu:", ["Kaikki", "Gold", "Silver", "Bronze", "TOTW", "Special"])
    with filter_col2: valittu_harvinaisuus = st.selectbox("2. Valitse harvinaisuus:", ["Kaikki", "Common", "Rare"])
    with filter_col3: vain_untradeable_lista = st.checkbox("Näytä listassa vain Untradeable", value=True)

    min_r = int(df['Rating'].min())
    max_r = int(df['Rating'].max())
    
    rating_col1, rating_col2, tyhja = st.columns([1, 1, 2])
    with rating_col1: valittu_min = st.number_input("Minimi:", min_value=min_r, max_value=max_r, value=min_r, step=1)
    with rating_col2: valittu_max = st.number_input("Maksimi:", min_value=min_r, max_value=max_r, value=max_r, step=1)
        
    sdf = df[(df['Rating'] >= valittu_min) & (df['Rating'] <= valittu_max)].copy()
    if valittu_laatu != "Kaikki": sdf = sdf[sdf['Quality'] == valittu_laatu]
    if valittu_harvinaisuus != "Kaikki": sdf = sdf[sdf['Card Type'] == valittu_harvinaisuus]
    if vain_untradeable_lista: sdf = sdf[sdf['Untradeable'] == True]

    tulos_col1, tulos_col2 = st.columns([1, 2])
    with tulos_col1:
        st.write("**Määrät ratingin mukaan:**")
        rating_jakauma = sdf['Rating'].value_counts().reset_index()
        rating_jakauma.columns = ['Rating', 'Kpl']
        rating_jakauma = rating_jakauma.sort_values(by='Rating', ascending=False)
        
        rating_jakauma['Rating'] = rating_jakauma['Rating'].astype(str)
        yhteensa_kpl = rating_jakauma['Kpl'].sum()
        total_rivi = pd.DataFrame([{'Rating': 'Yhteensä', 'Kpl': yhteensa_kpl}])
        rating_jakauma = pd.concat([rating_jakauma, total_rivi], ignore_index=True)
        
        st.dataframe(rating_jakauma, hide_index=True, use_container_width=True)
        
    with tulos_col2:
        st.write("**Pelaajalista:**")
        st.dataframe(
            sdf[['Name', 'Rating', 'Quality', 'Card Type', 'Untradeable', 'Sijainti']].sort_values(by=['Rating', 'Name'], ascending=[False, True]),
            use_container_width=True, hide_index=True
        )

else:
    st.info("Odotetaan tiedostoa. Raahaa CSV-tiedosto yllä olevaan laatikkoon aloittaaksesi!")
