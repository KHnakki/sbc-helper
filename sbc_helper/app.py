import streamlit as st
import pandas as pd

st.set_page_config(page_title="SBC Helper", layout="wide")
st.title("⚽ SBC Helper")
st.write("Etsi ja suodata pelaajia SBC-haasteita varten. SBC Storage ominaisuus ei toimi vielä sillä joudumme odottamaan EA:N päädyssä päivitystä. Joten älä huomioi sitä.")

uploaded_files = st.file_uploader("Pudota Club ja SBC Storage CSV-tiedostot tähän", type="csv", accept_multiple_files=True)

if uploaded_files:
    dataframes = []
    
    for file in uploaded_files:
        temp_df = pd.read_csv(file)
        if 'storage' in file.name.lower():
            temp_df['Sijainti'] = 'SBC Storage'
        else:
            temp_df['Sijainti'] = 'Klubi'
        dataframes.append(temp_df)
        
    df = pd.concat(dataframes, ignore_index=True)
    
    def maarita_laatu(row):
        rarity = row['Rarity']
        rating = row['Rating']
        if rarity == 'Team of the Week': return 'TOTW'
        elif rarity not in ['Common', 'Rare']: return 'Special'
        else:
            if rating >= 75: return 'Gold'
            elif rating >= 65: return 'Silver'
            else: return 'Bronze'
            
    df['Quality'] = df.apply(maarita_laatu, axis=1)
    
    def maarita_tyyppi(rarity):
        return rarity if rarity in ['Common', 'Rare'] else '-'
            
    df['Card Type'] = df['Rarity'].apply(maarita_tyyppi)
    
    # --- YLÄOSAN YHTEENVETO ---
    st.header("📊 Pika-katsaus varastoon")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Klubissa yhteensä", len(df[df['Sijainti'] == 'Klubi']))
    col2.metric("SBC Storagessa", len(df[df['Sijainti'] == 'SBC Storage']))
    col3.metric("Gold (Kaikki)", len(df[df['Quality'] == 'Gold']))
    col4.metric("Special & TOTW", len(df[df['Quality'].isin(['Special', 'TOTW'])]))
    
    st.divider()
    
    # --- INTERAKTIIVISET FILTTERIT ---
    st.header("🔍 SBC Suodatin")
    
    filter_col1, filter_col2, filter_col3 = st.columns(3)
    with filter_col1:
        valittu_laatu = st.selectbox("1. Valitse kortin laatu:", ["Kaikki", "Gold", "Silver", "Bronze", "TOTW", "Special"])
    with filter_col2:
        valittu_harvinaisuus = st.selectbox("2. Valitse harvinaisuus:", ["Kaikki", "Common", "Rare"])
    with filter_col3:
        valittu_sijainti = st.selectbox("3. Valitse sijainti:", ["Kaikki", "Klubi", "SBC Storage"])
        
    filter_col4, filter_col5 = st.columns(2)
    with filter_col4:
        pelipaikat = ["Kaikki"] + sorted(df['Preferred Position'].unique().tolist())
        valittu_pelipaikka = st.selectbox("4. Valitse pelipaikka:", pelipaikat)
        
    with filter_col5:
        st.write("5. Lisäasetukset:")
        vain_untradeable = st.checkbox("Näytä vain Untradeable (Ei-kaupattavat)", value=True)
        huomioi_alt = st.checkbox("Huomioi myös vaihtoehtoiset pelipaikat", value=True)
        
    # UUSI OMINAISUUS: RATING NUMEROSYÖTTÖ
    min_r = int(df['Rating'].min())
    max_r = int(df['Rating'].max())
    
    st.write("6. Valitse Rating-väli (Min - Max):")
    rating_col1, rating_col2, tyhja = st.columns([1, 1, 2]) # Jätetään oikealle tyhjää tilaa, jotta laatikot eivät veny liikaa
    
    with rating_col1:
        valittu_min = st.number_input("Minimi:", min_value=min_r, max_value=max_r, value=min_r, step=1)
    with rating_col2:
        valittu_max = st.number_input("Maksimi:", min_value=min_r, max_value=max_r, value=max_r, step=1)
        
    # Varmistetaan, ettei käyttäjä vahingossa laita minimiä isommaksi kuin maksimia
    if valittu_min > valittu_max:
        st.warning("⚠️ Minimi-rating ei voi olla suurempi kuin maksimi!")
        
    # --- DATAN SUODATUS ---
    suodatettu_df = df.copy()
    
    suodatettu_df = suodatettu_df[(suodatettu_df['Rating'] >= valittu_min) & (suodatettu_df['Rating'] <= valittu_max)]
    
    if valittu_laatu != "Kaikki":
        suodatettu_df = suodatettu_df[suodatettu_df['Quality'] == valittu_laatu]
    if valittu_harvinaisuus != "Kaikki":
        suodatettu_df = suodatettu_df[suodatettu_df['Card Type'] == valittu_harvinaisuus]
    if valittu_sijainti != "Kaikki":
        suodatettu_df = suodatettu_df[suodatettu_df['Sijainti'] == valittu_sijainti]
        
    if valittu_pelipaikka != "Kaikki":
        if huomioi_alt:
            suodatettu_df = suodatettu_df[
                (suodatettu_df['Preferred Position'] == valittu_pelipaikka) |
                (suodatettu_df['Alternate Positions'].astype(str).str.contains(rf'\b{valittu_pelipaikka}\b', regex=True, na=False))
            ]
        else:
            suodatettu_df = suodatettu_df[suodatettu_df['Preferred Position'] == valittu_pelipaikka]
            
    if vain_untradeable:
        suodatettu_df = suodatettu_df[suodatettu_df['Untradeable'] == True]
        
    st.write(f"### Löytyi {len(suodatettu_df)} pelaajaa hakuehdoilla!")
    
    # --- TULOSTEN NÄYTTÄMINEN ---
    tulos_col1, tulos_col2 = st.columns([1, 2])
    
    with tulos_col1:
        st.write("**Määrät ratingin mukaan:**")
        rating_jakauma = suodatettu_df['Rating'].value_counts().reset_index()
        rating_jakauma.columns = ['Rating', 'Kpl']
        rating_jakauma = rating_jakauma.sort_values(by='Rating', ascending=False)
        st.dataframe(rating_jakauma, hide_index=True, use_container_width=True)
        
    with tulos_col2:
        st.write("**Pelaajalista:**")
        suodatettu_df = suodatettu_df.sort_values(by=['Rating', 'Name'], ascending=[False, True])
        st.dataframe(
            suodatettu_df[['Name', 'Rating', 'Sijainti', 'Preferred Position', 'Quality', 'Card Type', 'Untradeable']],
            use_container_width=True,
            hide_index=True
        )
else:
    st.info("Odotetaan tiedostoa. Voit maalata ja raahata yllä olevaan laatikkoon useamman CSV-tiedoston kerralla (esim. club.csv ja sbc_storage.csv)!")