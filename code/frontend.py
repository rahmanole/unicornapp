import streamlit as st
import pandas as pd
import helper

st.set_page_config(
    page_title="Stock Screener",
    page_icon=":tada:",
)

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
price = st.number_input("Minimum Price",1.0,1000.0,value = 5.0,step=0.05)
vol = st.number_input("Minimum volume",1.0,10.0,value = 1.0,step=0.5)
mkt_cap = st.number_input("Minimum Maket Cap",50.0,1000.0,value = 50.0,step=10.0)

# vol = st.slider("Select minimum volume",1.0,10.0,0.5)
# mkt_cap = st.slider("Select minimum market cap",50,500,10)
st.session_state.price = round(price,2)
st.session_state.vol = vol
st.session_state.mkt_cap = mkt_cap
rank = st.selectbox("Select Rank Type",rank_type,key="rank_type")
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

if "price" in st.session_state and "vol" in st.session_state and "mkt_cap" in st.session_state:
    with st.spinner('Wait for it...'):
        if isinstance(response,pd.DataFrame):
            st.dataframe(response,hide_index=True)
        else:
            st.write("Could not load the data")

    
    
