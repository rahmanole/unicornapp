import helper
from fastapi import FastAPI
from mangum import Mangum
import uvicorn

app = FastAPI()
handler=Mangum(app)

@app.get('/stocks/{price}/{vol}/{mkt_cap}')
def get_service_response(price,vol,mkt_cap):
    print(f"From url: {price},{vol},{mkt_cap}")
    return helper.get_data(price=float(price),vol=float(vol),mkt_cap=float(mkt_cap))

# @app.get('/stocks/')
# def get_service_response(price,vol,mkt_cap):
#     print(f"recevied values{price,vol,mkt_cap}")
#     return helper.get_data(price=price,vol=vol,mkt_cap=mkt_cap)

# if __name__ == "__main__":
#     helper.get_data()
#     uvicorn.run(app, host="0.0.0.0", port=8000)