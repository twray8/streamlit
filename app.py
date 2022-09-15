import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import date, datetime


#SQL CONNECTIONS

current_year = datetime.now().year
current_month = datetime.now().month
month1 = 4
month2 = 8

paramet = {'year':current_year, 'month1':current_month, 'month2':month2}


df = pd.read_excel('sql_gen.xlsx')
rolling_ec = pd.read_excel('Rolling Ec.xlsx')
rolling_pan = pd.read_excel('Rolling Pan.xlsx')
lol = pd.read_excel('incidencias.xlsx')


## DATA PRE PROCESSING

rolling_ec['cumulative_clients'] = rolling_ec.clients.cumsum()
rolling_pan['cumulative_clients'] = rolling_pan.clients.cumsum()

def get_late_orders(data:pd.DataFrame):
    for idx, row in data.iterrows():
        if data.loc[idx, 'result']> 15:
            data.loc[idx, 'tarde'] = True
        else:
            data.loc[idx, 'tarde'] = False
    return data

def get_rescheduled_orders(data:pd.DataFrame):
    for idx, row in data.iterrows():
        if data.loc[idx, 'original_delivery_to'] == 0:
            data.loc[idx, 'reagendada'] = False
        else:
            data.loc[idx, 'reagendada'] = True
    return data

def get_rep(data:pd.DataFrame):
    data = data.apply(lambda x: x/x.sum())
    return data

lol = lol.fillna(0)
lol['result'] = (lol.delivered_date - lol.delivery_to).astype('timedelta64[m]')
lol = get_rescheduled_orders(get_late_orders(lol))

tarde = pd.DataFrame(lol.groupby('tarde')['order_id'].nunique())
tarde = get_rep(tarde)
tarde.order_id = tarde.order_id * 100
tarde = tarde.iloc[1, 0]
tarde = "{:.2f}".format(tarde)


reagendada = pd.DataFrame(lol.groupby('reagendada')['order_id'].nunique())
reagendada = get_rep(reagendada)
reagendada.order_id = reagendada.order_id * 100
reagendada = reagendada.iloc[1, 0]
reagendada = "{:.2f}".format(reagendada)




#pd.read_excel('/Users/tomaswray/Documents/python/python/output/top Marcas Tipti.xlsx')
#streamlit run /Users/tomaswray/Documents/apps/dash/app.py

#PAGE CONFIG

st.set_page_config(page_title="Prueba Dashboard", page_icon=":gun:", layout="wide", )
st.sidebar.header("Filtre aqui")

country = st.sidebar.multiselect("Seleccione Pais", options=df['pais'].unique(), default= 'Ecuador')
city = st.sidebar.multiselect("Seleccione Ciudad", options=df['ciudad'].unique(), default= df[df.ciudad != 'Ciudad de Panamá'].ciudad.unique())

df_selection = df.query("ciudad == @city & pais == @country")

dia = st.sidebar.multiselect("Seleccione Fecha Ecu", options = rolling_ec['dia'].unique(), default= rolling_ec['dia'].max())

day = st.sidebar.multiselect('Seleccione Fecha Pan', options = rolling_pan['dia'].unique(), default= rolling_pan['dia'].max())

ec_selction = rolling_ec.query("dia == @dia")
pan_selection = rolling_pan.query("dia == @day")


## Title

st.title(':bar_chart:  Sales Dashboard ')

st.markdown("##")


## KPIS

total_sales = int(df_selection.gmv.sum())
total_orders = df_selection.orders.sum()
aov = df_selection['gmv'].sum() / df_selection['orders'].sum()
aov = "{:.2f}".format(aov)
#arpu = arpu.astype(int)


left_column ,center_column , right_column,  column_5, column_6 = st.columns(5)

with left_column:
    st.subheader(":money_with_wings: Ventas Totales")
    st.subheader(f"$ {total_sales:,}")

with center_column:
    st.subheader(":dollar: AOV")
    st.subheader(f"$ {aov}")

with right_column:
    st.subheader(":triangular_flag_on_post: Ordenes")
    st.subheader(f"{total_orders:,}")

with column_5:
    st.subheader('Tarde')
    st.subheader(f"{tarde} %")

with column_6:
    st.subheader('Reagendamiento')
    st.subheader(f"{reagendada} %")

st.markdown("---")

## GRFICOS



daily_total_sales = df_selection.groupby(['day'])['gmv'].sum().reset_index()

line_graph = px.line(daily_total_sales, x='day', y='gmv', title='GMV OVER TIME', template="plotly_white")


daily_total_orders = df_selection.groupby(['day'])['orders'].sum().reset_index()
daily_total_gmv = df_selection.groupby(['day'])['gmv'].sum().reset_index()
daily_aov = pd.merge(daily_total_orders, daily_total_gmv, on='day')
daily_aov['aov'] = daily_aov.gmv / daily_aov.orders

aov_line = px.line(daily_aov, x='day', y='aov', title='AOV OVER TIME')


left_column, right_column = st.columns(2)
left_column.plotly_chart(line_graph)
right_column.plotly_chart(aov_line)

st.markdown('##')

st.title('KPIS PARA ROLLING')

left_column,  right_column = st.columns(2)
with left_column:
    st.subheader('Ecuador 🇪🇨')
    st.write(ec_selction)

with right_column:
    st.subheader('Panamá 🇵🇦')
    st.write(pan_selection)



##          VISUAL CONFIG

hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

