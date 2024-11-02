import streamlit as st
import app
import time
import requests
import pandas as pd
import helper


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

@st.fragment
def load_filters():
    
    price = st.number_input("Minimum Price",1.0,1000.0,value = 5.0,step=0.05)
    vol = st.number_input("Minimum volume",1.0,10.0,value = 1.0,step=0.5)
    mkt_cap = st.number_input("Minimum Maket Cap",50.0,1000.0,value = 50.0,step=10.0)
 
    # vol = st.slider("Select minimum volume",1.0,10.0,0.5)
    # mkt_cap = st.slider("Select minimum market cap",50,500,10)
    st.session_state.price = round(price,2)
    st.session_state.vol = vol
    st.session_state.mkt_cap = mkt_cap

load_filters()
st.button("Update")
if "price" in st.session_state and "vol" in st.session_state and "mkt_cap" in st.session_state:
    with st.spinner('Wait for it...'):
        response = helper.filter_stocks(st.session_state.price,st.session_state.vol,st.session_state.mkt_cap)
        if isinstance(response,pd.DataFrame):
            response = response.drop(["index"],axis=1)
            st.table(response)
        else:
            st.write("Could not load the data")

    
    
