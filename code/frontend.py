import streamlit as st
import pandas as pd
import helper
import time

st.set_page_config(
    page_title="Stock Screener",
    page_icon=":tada:",
)

hide_streamlit_style = """
<style>
    /* Hides the Streamlit main menu and the header */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Removes the padding from the main block container at the top */
    .stMainBlockContainer {
        padding-top: 2rem;
    }
    
    /* Hides the "Deploy" button on Streamlit Community Cloud */
    .stDeployButton {
        display: none;
    }

    /* Hides the "Made with Streamlit" footer */
    footer {
        visibility: hidden;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def get_api_res(price,vol,mkt_cap):
    try:
        stocks = helper.get_data(price=float(price),vol=float(vol),mkt_cap=float(mkt_cap))
        df = pd.DataFrame(stocks)
        return df
        #     return df
        # # Make a GET request to the API endpoint using requests.get()
        # response = requests.get(url)
        # # Check if the request was successful (status code 200)
        # if response.status_code == 200:
        #     stocks = response.json()
        #     df = pd.DataFrame(stocks)
        #     return df
    except Exception as e:
        raise(e)

rank_type = helper.get_rank_type()
# @st.fragment
# def load_filters():
rank_types = {"Pre Market":"preMarket","Day":"1d","After Market":"afterMarket"}
vol = st.number_input("Minimum volume (Millions)",0.01,10.0,value = 1.0,step=0.1)
mkt_cap = st.number_input("Minimum Maket Cap (Millions)",1.0,100000000000.0,value = 50.0,step=10.0)
price = st.number_input("Minimum Price",0.01,1000.0,value = 5.0,step=0.05)

# vol = st.slider("Select minimum volume",1.0,10.0,0.5)
# mkt_cap = st.slider("Select minimum market cap",50,500,10)
st.session_state.price = round(price,2)
st.session_state.vol = vol
st.session_state.mkt_cap = mkt_cap
rank = st.selectbox("Market Session",rank_type,key="rank_type")
st.session_state.rank = rank_types[rank]


# load_filters()
col1, col2 = st.columns([1,1])
# with col1:
st.button("Update")
# with col2:

response = helper.filter_stocks(st.session_state.rank,st.session_state.price,st.session_state.vol,st.session_state.mkt_cap)
# sector_names = sorted(list(set(response.sector.values)))
response = response.drop(["index"],axis=1)
# response['sector'] = response['sector'].apply(lambda x: helper.create_acronym(x))
response = response.rename(columns={"disSymbol":"Ticker","changeRatio":"Change (%)","pprice":"Price","volume":"Volume","marketValue":"Market Cap"}) 
response = response.sort_values(by=["Change (%)"],ascending=False).reset_index(drop=True)
# # Collapsible widget using expander
# with st.expander("Show Acronyms"):
#     for name in sector_names:
#         acronym = helper.create_acronym(name)
#         st.write(f"{acronym}: {name}")

@st.fragment(run_every="10s")
def render_fragment():
    if "price" in st.session_state and "vol" in st.session_state and "mkt_cap" in st.session_state:
        with st.spinner('Wait for it...'):
            if isinstance(response,pd.DataFrame):
                st.dataframe(response,hide_index=True,height=33*16)
            else:
                st.write("Could not load the data")
render_fragment()

    
