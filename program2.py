# [clone libraries]
import requests
import subprocess

# [pandas, numpy and file handling libraries]
import pandas as pd
import numpy as np
import os
import json

# [SQL libraries]
import mysql.connector
import sqlalchemy
from sqlalchemy import create_engine
import pymysql

# [Dash board libraries]
import streamlit as st
import plotly.express as px
from PIL import Image

#  DASHBOARD  
#  CONNECT SQL SERVER  /   ACCESS DATA BASE   /   EXECUTE SQL QUERIES   /    ACCESS DATA  

conn = pymysql.connect(host='localhost', user='root', password='', db='phonepe_pulse_1')
cursor = conn.cursor()

# STREAMLIT DASHBOARD 

# Comfiguring Streamlit GUI 
st.set_page_config(layout='wide')

# Title
st.header(':red[Phonepe Pulse Data Visualization ]')
st.write(':blue[**(Note)**:-This data between **2018** to **2022** in **INDIA**]')

# Selection option
option = st.radio('**Select your option**',('All India', 'State and UT','Top Ten categories'),horizontal=True)

# All India

if option == 'All India':

    # Select tab
    tab1, tab2 = st.tabs(['Transaction','User'])

    # All India Transaction  
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            in_tr_yr = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022'),key='in_tr_yr')
        with col2:
            in_tr_qtr = st.selectbox('**Select Quarter**', ('1','2','3','4'),key='in_tr_qtr')
        with col3:
            in_tr_tr_typ = st.selectbox('**Select Transaction type**', ('Recharge & bill payments','Peer-to-peer payments',
            'Merchant payments','Financial Services','Others'),key='in_tr_tr_typ')

        # SQL Query

        # Transaction Analysis bar chart query
        cursor.execute(f"SELECT State, Transaction_amount FROM aggregated_transaction WHERE Year = '{in_tr_yr}' AND Quarter = '{in_tr_qtr}' AND Transaction_type = '{in_tr_tr_typ}';")
        in_tr_tab_qry_rslt = cursor.fetchall()
        df_in_tr_tab_qry_rslt = pd.DataFrame(np.array(in_tr_tab_qry_rslt), columns=['State', 'Transaction_amount'])
        df_in_tr_tab_qry_rslt1 = df_in_tr_tab_qry_rslt.set_index(pd.Index(range(1, len(df_in_tr_tab_qry_rslt)+1)))

        # Transaction Analysis table query
        cursor.execute(f"SELECT State, Transaction_count, Transaction_amount FROM aggregated_transaction WHERE Year = '{in_tr_yr}' AND Quarter = '{in_tr_qtr}' AND Transaction_type = '{in_tr_tr_typ}';")
        in_tr_anly_tab_qry_rslt = cursor.fetchall()
        df_in_tr_anly_tab_qry_rslt = pd.DataFrame(np.array(in_tr_anly_tab_qry_rslt), columns=['State','Transaction_count','Transaction_amount'])
        df_in_tr_anly_tab_qry_rslt1 = df_in_tr_anly_tab_qry_rslt.set_index(pd.Index(range(1, len(df_in_tr_anly_tab_qry_rslt)+1)))

        # Total Transaction Amount table query
        cursor.execute(f"SELECT SUM(Transaction_amount), AVG(Transaction_amount) FROM aggregated_transaction WHERE Year = '{in_tr_yr}' AND Quarter = '{in_tr_qtr}' AND Transaction_type = '{in_tr_tr_typ}';")
        in_tr_am_qry_rslt = cursor.fetchall()
        df_in_tr_am_qry_rslt = pd.DataFrame(np.array(in_tr_am_qry_rslt), columns=['Total','Average'])
        df_in_tr_am_qry_rslt1 = df_in_tr_am_qry_rslt.set_index(['Average'])

        # Total Transaction Count table query
        cursor.execute(f"SELECT SUM(Transaction_count), AVG(Transaction_count) FROM aggregated_transaction WHERE Year = '{in_tr_yr}' AND Quarter = '{in_tr_qtr}' AND Transaction_type = '{in_tr_tr_typ}';")
        in_tr_co_qry_rslt = cursor.fetchall()
        df_in_tr_co_qry_rslt = pd.DataFrame(np.array(in_tr_co_qry_rslt), columns=['Total','Average'])
        df_in_tr_co_qry_rslt1 = df_in_tr_co_qry_rslt.set_index(['Average'])

        # --------- / Output  /  -------- #

        # ------    /  Geo visualization dashboard for Transaction /   ---- #
        # Drop a State column from df_in_tr_tab_qry_rslt
        df_in_tr_tab_qry_rslt.drop(columns=['State'], inplace=True)
        # Clone the gio data
        url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url)
        data1 = json.loads(response.content)
        # Extract state names and sort them in alphabetical order
        state_names_tra = [feature['properties']['ST_NM'] for feature in data1['features']]
        state_names_tra.sort()
        # Create a DataFrame with the state names column
        df_state_names_tra = pd.DataFrame({'State': state_names_tra})
        # Combine the Gio State name with df_in_tr_tab_qry_rslt
        df_state_names_tra['Transaction_amount']=df_in_tr_tab_qry_rslt
        # convert dataframe to csv file
        df_state_names_tra.to_csv('State_trans.csv', index=False)
        # Read csv
        df_tra = pd.read_csv('State_trans.csv')
        # Geo plot
        fig_tra = px.choropleth(
            df_tra,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',locations='State',color='Transaction_amount',color_continuous_scale='thermal',title = 'Transaction Analysis')
        fig_tra.update_geos(fitbounds="locations", visible=False)
        fig_tra.update_layout(title_font=dict(size=33),title_font_color='#6739b7', height=800)
        st.plotly_chart(fig_tra,use_container_width=True)

        # ---------   /   All India Transaction Analysis Bar chart  /  ----- #
        df_in_tr_tab_qry_rslt1['State'] = df_in_tr_tab_qry_rslt1['State'].astype(str)
        df_in_tr_tab_qry_rslt1['Transaction_amount'] = df_in_tr_tab_qry_rslt1['Transaction_amount'].astype(float)
        df_in_tr_tab_qry_rslt1_fig = px.bar(df_in_tr_tab_qry_rslt1 , x = 'State', y ='Transaction_amount', color ='Transaction_amount', color_continuous_scale = 'thermal', title = 'Transaction Analysis Chart', height = 700,)
        df_in_tr_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
        st.plotly_chart(df_in_tr_tab_qry_rslt1_fig,use_container_width=True)

        # -------  /  All India Total Transaction calculation Table   /   ----  #
        st.header(':violet[Total calculation]')

        col4, col5 = st.columns(2)
        with col4:
            st.subheader('Transaction Analysis')
            st.dataframe(df_in_tr_anly_tab_qry_rslt1)
        with col5:
            st.subheader('Transaction Amount')
            st.dataframe(df_in_tr_am_qry_rslt1)
            st.subheader('Transaction Count')
            st.dataframe(df_in_tr_co_qry_rslt1)


    # ---------------------------------------       /     All India User        /        ------------------------------------ #
    with tab2:

        col1, col2 = st.columns(2)
        with col1:
            in_us_yr = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022'),key='in_us_yr')
        with col2:
            in_us_qtr = st.selectbox('**Select Quarter**', ('1','2','3','4'),key='in_us_qtr')

        # SQL Query

        # User Analysis Bar chart query
        cursor.execute(f"SELECT State, SUM(User_Count) FROM aggregated_user WHERE Year = '{in_us_yr}' AND Quarter = '{in_us_qtr}' GROUP BY State;")
        in_us_tab_qry_rslt = cursor.fetchall()
        df_in_us_tab_qry_rslt = pd.DataFrame(np.array(in_us_tab_qry_rslt), columns=['State', 'User Count'])
        df_in_us_tab_qry_rslt1 = df_in_us_tab_qry_rslt.set_index(pd.Index(range(1, len(df_in_us_tab_qry_rslt)+1)))

        # Total User Count table query
        cursor.execute(f"SELECT SUM(User_Count), AVG(User_Count) FROM aggregated_user WHERE Year = '{in_us_yr}' AND Quarter = '{in_us_qtr}';")
        in_us_co_qry_rslt = cursor.fetchall()
        df_in_us_co_qry_rslt = pd.DataFrame(np.array(in_us_co_qry_rslt), columns=['Total','Average'])
        df_in_us_co_qry_rslt1 = df_in_us_co_qry_rslt.set_index(['Average'])

        # ---------  /  Output  /  -------- #

        # ------    /  Geo visualization dashboard for User  /   ---- #
        # Drop a State column from df_in_us_tab_qry_rslt
        df_in_us_tab_qry_rslt.drop(columns=['State'], inplace=True)
        # Clone the gio data
        url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(url)
        data2 = json.loads(response.content)
        # Extract state names and sort them in alphabetical order
        state_names_use = [feature['properties']['ST_NM'] for feature in data2['features']]
        state_names_use.sort()
        # Create a DataFrame with the state names column
        df_state_names_use = pd.DataFrame({'State': state_names_use})
        # Combine the Gio State name with df_in_tr_tab_qry_rslt
        df_state_names_use['User Count']=df_in_us_tab_qry_rslt
        # convert dataframe to csv file
        df_state_names_use.to_csv('State_user.csv', index=False)
        # Read csv
        df_use = pd.read_csv('State_user.csv')
        # Geo plot
        fig_use = px.choropleth(
            df_use,
            geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
            featureidkey='properties.ST_NM',locations='State',color='User Count',color_continuous_scale='thermal',title = 'User Analysis')
        fig_use.update_geos(fitbounds="locations", visible=False)
        fig_use.update_layout(title_font=dict(size=33),title_font_color='#6739b7', height=800)
        st.plotly_chart(fig_use,use_container_width=True)

        # ----   /   All India User Analysis Bar chart   /     -------- #
        df_in_us_tab_qry_rslt1['State'] = df_in_us_tab_qry_rslt1['State'].astype(str)
        df_in_us_tab_qry_rslt1['User Count'] = df_in_us_tab_qry_rslt1['User Count'].astype(int)
        df_in_us_tab_qry_rslt1_fig = px.bar(df_in_us_tab_qry_rslt1 , x = 'State', y ='User Count', color ='User Count', color_continuous_scale = 'thermal', title = 'User Analysis Chart', height = 700,)
        df_in_us_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
        st.plotly_chart(df_in_us_tab_qry_rslt1_fig,use_container_width=True)

        # -----   /   All India Total User calculation Table   /   ----- #
        st.header(':violet[Total calculation]')

        col3, col4 = st.columns(2)
        with col3:
            st.subheader('User Analysis')
            st.dataframe(df_in_us_tab_qry_rslt1)
        with col4:
            st.subheader('User Count')
            st.dataframe(df_in_us_co_qry_rslt1)



# ==============================================          /     State and UT      /             ============================================== #
elif option =='State and UT':

    # Select tab
    tab3, tab4 = st.tabs(['Transaction','User'])

    # ---------------------------------       /     State and UT Transaction        /        ------------------------------- # 
    with tab3:

        col1, col2,col3 = st.columns(3)
        with col1:
            st_tr_st = st.selectbox('**Select State and UT**',('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh','assam', 'bihar', 
            'chandigarh', 'chhattisgarh','dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat', 'haryana', 'himachal-pradesh', 
            'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh','maharashtra', 'manipur', 
            'meghalaya', 'mizoram', 'nagaland','odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim', 'tamil-nadu', 'telangana', 
            'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'),key='st_tr_st')
        with col2:
            st_tr_yr = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022'),key='st_tr_yr')
        with col3:
            st_tr_qtr = st.selectbox('**Select Quarter**', ('1','2','3','4'),key='st_tr_qtr')

        # SQL Query

        # Transaction Analysis bar chart query
        cursor.execute(f"SELECT Transaction_type, Transaction_amount FROM aggregated_transaction WHERE State = '{st_tr_st}' AND Year = '{st_tr_yr}' AND Quarter = '{st_tr_qtr}';")
        st_tr_tab_bar_qry_rslt = cursor.fetchall()
        df_st_tr_tab_bar_qry_rslt = pd.DataFrame(np.array(st_tr_tab_bar_qry_rslt), columns=['Transaction_type', 'Transaction_amount'])
        df_st_tr_tab_bar_qry_rslt1 = df_st_tr_tab_bar_qry_rslt.set_index(pd.Index(range(1, len(df_st_tr_tab_bar_qry_rslt)+1)))

        # Transaction Analysis table query
        cursor.execute(f"SELECT Transaction_type, Transaction_count, Transaction_amount FROM aggregated_transaction WHERE State = '{st_tr_st}' AND Year = '{st_tr_yr}' AND Quarter = '{st_tr_qtr}';")
        st_tr_anly_tab_qry_rslt = cursor.fetchall()
        df_st_tr_anly_tab_qry_rslt = pd.DataFrame(np.array(st_tr_anly_tab_qry_rslt), columns=['Transaction_type','Transaction_count','Transaction_amount'])
        df_st_tr_anly_tab_qry_rslt1 = df_st_tr_anly_tab_qry_rslt.set_index(pd.Index(range(1, len(df_st_tr_anly_tab_qry_rslt)+1)))

        # Total Transaction Amount table query
        cursor.execute(f"SELECT SUM(Transaction_amount), AVG(Transaction_amount) FROM aggregated_transaction WHERE State = '{st_tr_st}' AND Year = '{st_tr_yr}' AND Quarter = '{st_tr_qtr}';")
        st_tr_am_qry_rslt = cursor.fetchall()
        df_st_tr_am_qry_rslt = pd.DataFrame(np.array(st_tr_am_qry_rslt), columns=['Total','Average'])
        df_st_tr_am_qry_rslt1 = df_st_tr_am_qry_rslt.set_index(['Average'])

        # Total Transaction Count table query
        cursor.execute(f"SELECT SUM(Transaction_count), AVG(Transaction_count) FROM aggregated_transaction WHERE State = '{st_tr_st}' AND Year ='{st_tr_yr}' AND Quarter = '{st_tr_qtr}';")
        st_tr_co_qry_rslt = cursor.fetchall()
        df_st_tr_co_qry_rslt = pd.DataFrame(np.array(st_tr_co_qry_rslt), columns=['Total','Average'])
        df_st_tr_co_qry_rslt1 = df_st_tr_co_qry_rslt.set_index(['Average'])

        # ---------  /  Output  /  -------- #

        # -----    /   State and UT Transaction Analysis bar chart   /   ------ #
        df_st_tr_tab_bar_qry_rslt1['Transaction_type'] = df_st_tr_tab_bar_qry_rslt1['Transaction_type'].astype(str)
        df_st_tr_tab_bar_qry_rslt1['Transaction_amount'] = df_st_tr_tab_bar_qry_rslt1['Transaction_amount'].astype(float)
        df_st_tr_tab_bar_qry_rslt1_fig = px.bar(df_st_tr_tab_bar_qry_rslt1 , x = 'Transaction_type', y ='Transaction_amount', color ='Transaction_amount', color_continuous_scale = 'thermal', title = 'Transaction Analysis Chart', height = 500,)
        df_st_tr_tab_bar_qry_rslt1_fig.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
        st.plotly_chart(df_st_tr_tab_bar_qry_rslt1_fig,use_container_width=True)

        # ------  /  State and UT Total Transaction calculation Table  /  ---- #
        st.header(':violet[Total calculation]')

        col4, col5 = st.columns(2)
        with col4:
            st.subheader('Transaction Analysis')
            st.dataframe(df_st_tr_anly_tab_qry_rslt1)
        with col5:
            st.subheader('Transaction Amount')
            st.dataframe(df_st_tr_am_qry_rslt1)
            st.subheader('Transaction Count')
            st.dataframe(df_st_tr_co_qry_rslt1)


    # -----------------------------------------       /     State and UT User        /        ---------------------------------- # 
    with tab4:

        col5, col6 = st.columns(2)
        with col5:
            st_us_st = st.selectbox('**Select State and UT**',('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh','assam', 'bihar', 
            'chandigarh', 'chhattisgarh','dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat', 'haryana', 'himachal-pradesh', 
            'jammu-&-kashmir', 'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep', 'madhya-pradesh','maharashtra', 'manipur', 
            'meghalaya', 'mizoram', 'nagaland','odisha', 'puducherry', 'punjab', 'rajasthan', 'sikkim', 'tamil-nadu', 'telangana', 
            'tripura', 'uttar-pradesh', 'uttarakhand', 'west-bengal'),key='st_us_st')
        with col6:
            st_us_yr = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022'),key='st_us_yr')

        # SQL Query

        # User Analysis Bar chart query
        cursor.execute(f"SELECT Quarter, SUM(User_Count) FROM aggregated_user WHERE State = '{st_us_st}' AND Year = '{st_us_yr}' GROUP BY Quarter;")
        st_us_tab_qry_rslt = cursor.fetchall()
        df_st_us_tab_qry_rslt = pd.DataFrame(np.array(st_us_tab_qry_rslt), columns=['Quarter', 'User Count'])
        df_st_us_tab_qry_rslt1 = df_st_us_tab_qry_rslt.set_index(pd.Index(range(1, len(df_st_us_tab_qry_rslt)+1)))

        # Total User Count table query
        cursor.execute(f"SELECT SUM(User_Count), AVG(User_Count) FROM aggregated_user WHERE State = '{st_us_st}' AND Year = '{st_us_yr}';")
        st_us_co_qry_rslt = cursor.fetchall()
        df_st_us_co_qry_rslt = pd.DataFrame(np.array(st_us_co_qry_rslt), columns=['Total','Average'])
        df_st_us_co_qry_rslt1 = df_st_us_co_qry_rslt.set_index(['Average'])

        # ---------  /  Output  /  -------- #

        # -----   /   All India User Analysis Bar chart   /   ----- #
        df_st_us_tab_qry_rslt1['Quarter'] = df_st_us_tab_qry_rslt1['Quarter'].astype(int)
        df_st_us_tab_qry_rslt1['User Count'] = df_st_us_tab_qry_rslt1['User Count'].astype(int)
        df_st_us_tab_qry_rslt1_fig = px.bar(df_st_us_tab_qry_rslt1 , x = 'Quarter', y ='User Count', color ='User Count', color_continuous_scale = 'thermal', title = 'User Analysis Chart', height = 500,)
        df_st_us_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
        st.plotly_chart(df_st_us_tab_qry_rslt1_fig,use_container_width=True)

        # ------    /   State and UT User Total User calculation Table   /   -----#
        st.header(':violet[Total calculation]')

        col3, col4 = st.columns(2)
        with col3:
            st.subheader('User Analysis')
            st.dataframe(df_st_us_tab_qry_rslt1)
        with col4:
            st.subheader('User Count')
            st.dataframe(df_st_us_co_qry_rslt1)



# ==============================================          /     Top categories       /             =========================================== #
else:

    # Select tab
    tab5, tab6 = st.tabs(['Transaction','User'])

    # ---------------------------------------       /     All India Top Transaction        /        ---------------------------- #
    with tab5:
        top_tr_yr = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022'),key='top_tr_yr')

        # SQL Query

        # Top Transaction Analysis bar chart query
        cursor.execute(f"SELECT State, SUM(Transaction_amount) As Transaction_amount FROM top_transaction WHERE Year = '{top_tr_yr}' GROUP BY State ORDER BY Transaction_amount DESC LIMIT 10;")
        top_tr_tab_qry_rslt = cursor.fetchall()
        df_top_tr_tab_qry_rslt = pd.DataFrame(np.array(top_tr_tab_qry_rslt), columns=['State', 'Top Transaction amount'])
        df_top_tr_tab_qry_rslt1 = df_top_tr_tab_qry_rslt.set_index(pd.Index(range(1, len(df_top_tr_tab_qry_rslt)+1)))

        # Top Transaction Analysis table query
        cursor.execute(f"SELECT State, SUM(Transaction_amount) as Transaction_amount, SUM(Transaction_count) as Transaction_count FROM top_transaction WHERE Year = '{top_tr_yr}' GROUP BY State ORDER BY Transaction_amount DESC LIMIT 10;")
        top_tr_anly_tab_qry_rslt = cursor.fetchall()
        df_top_tr_anly_tab_qry_rslt = pd.DataFrame(np.array(top_tr_anly_tab_qry_rslt), columns=['State', 'Top Transaction amount','Total Transaction count'])
        df_top_tr_anly_tab_qry_rslt1 = df_top_tr_anly_tab_qry_rslt.set_index(pd.Index(range(1, len(df_top_tr_anly_tab_qry_rslt)+1)))

        # ---------  /  Output  /  -------- #

        # -----   /   All India Transaction Analysis Bar chart   /   ----- #
        df_top_tr_tab_qry_rslt1['State'] = df_top_tr_tab_qry_rslt1['State'].astype(str)
        df_top_tr_tab_qry_rslt1['Top Transaction amount'] = df_top_tr_tab_qry_rslt1['Top Transaction amount'].astype(float)
        df_top_tr_tab_qry_rslt1_fig = px.bar(df_top_tr_tab_qry_rslt1 , x = 'State', y ='Top Transaction amount', color ='Top Transaction amount', color_continuous_scale = 'thermal', title = 'Top Transaction Analysis Chart', height = 600,)
        df_top_tr_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
        st.plotly_chart(df_top_tr_tab_qry_rslt1_fig,use_container_width=True)

        # -----   /   All India Total Transaction calculation Table   /   ----- #
        st.header(':violet[Total calculation]')
        st.subheader('Top Transaction Analysis')
        st.dataframe(df_top_tr_anly_tab_qry_rslt1)


    # -------------------------       /     All India Top User        /        ------------------ #
    with tab6:
        top_us_yr = st.selectbox('**Select Year**', ('2018','2019','2020','2021','2022'),key='top_us_yr')

        # SQL Query

        # Top User Analysis bar chart query
        cursor.execute(f"SELECT State, SUM(Registered_User) AS Top_user FROM top_user WHERE Year='{top_us_yr}' GROUP BY State ORDER BY Top_user DESC LIMIT 10;")
        top_us_tab_qry_rslt = cursor.fetchall()
        df_top_us_tab_qry_rslt = pd.DataFrame(np.array(top_us_tab_qry_rslt), columns=['State', 'Total User count'])
        df_top_us_tab_qry_rslt1 = df_top_us_tab_qry_rslt.set_index(pd.Index(range(1, len(df_top_us_tab_qry_rslt)+1)))

        # ---------  /  Output  /  -------- #

        # -----   /   All India User Analysis Bar chart   /   ----- #
        df_top_us_tab_qry_rslt1['State'] = df_top_us_tab_qry_rslt1['State'].astype(str)
        df_top_us_tab_qry_rslt1['Total User count'] = df_top_us_tab_qry_rslt1['Total User count'].astype(float)
        df_top_us_tab_qry_rslt1_fig = px.bar(df_top_us_tab_qry_rslt1 , x = 'State', y ='Total User count', color ='Total User count', color_continuous_scale = 'thermal', title = 'Top User Analysis Chart', height = 600,)
        df_top_us_tab_qry_rslt1_fig.update_layout(title_font=dict(size=33),title_font_color='#6739b7')
        st.plotly_chart(df_top_us_tab_qry_rslt1_fig,use_container_width=True)

        # -----   /   All India Total Transaction calculation Table   /   ----- #
        st.header(':violet[Total calculation]')
        st.subheader('Total User Analysis')
        st.dataframe(df_top_us_tab_qry_rslt1)

# SUNBURST ---- Title
st.header(':red[Over all INDIA State and UnionTerritories Transaction and User DETAILS]')

# Selection option
#option = st.write(':blue[over all State and UnionTerritories]')

# Over All India State and UnionTerritories

#if option == 'over all State and UnionTerritories':

    # Select tab
tab7, tab8 = st.tabs(['State','UnionTerritories'])

# All India State Transaction and User
with tab7:
        
        with tab7:
            st.header(':blue[over all State Transaction and User Details]')
             #--1--aggregated_transaction_state
            st.title(':green[1--aggregated_transaction_state]')
            df1 = pd.read_csv(r'C:\Users\shama\phonepe_pulse.csv\phonepe_pulse_table_aggregated_transaction_state.csv')
            fig1 = px.sunburst(data_frame=df1,path=["Year","Quarter","State","Transaction_type","Transaction_count","Transaction_amount"],hover_data=["Year","Quarter","State","Transaction_type","Transaction_count","Transaction_amount"],maxdepth=3)
            #fig1.update_layout(title_font=dict(size=33),title_font_color='#6739b7', height=800)
            st.plotly_chart(fig1,use_container_width=True)
        
        
            #--3--aggregated_user_state
            st.title(':green[2--aggregated_user_state]')
            df3 = pd.read_csv(r"C:\Users\shama\phonepe_pulse.csv\phonepe_pulse_table_aggregated_user_state.csv")
            fig3 = px.sunburst(data_frame=df3,path=["Year","Quarter","State","Brands","User_Count","User_Percentage"],hover_data=["Year","Quarter","State","Brands","User_Count","User_Percentage"],maxdepth=3)
            #fig3.update_layout(title_font=dict(size=20),title_font_color='#6739b7', height=500)
            st.plotly_chart(fig3,use_container_width=True)

        
            #--5--map_transaction_state
            st.title(':green[3--map_transaction_state]')
            df5 = pd.read_csv(r"C:\Users\shama\phonepe_pulse.csv\phonepe_pulse_table_map_transaction_state.csv")
            fig5 = px.sunburst(data_frame=df5,path=["Year","Quarter","State","District","Transaction_Count","Transaction_Amount"],hover_data=["Year","Quarter","State","District","Transaction_Count","Transaction_Amount"],maxdepth=3)
            st.plotly_chart(fig5,use_container_width=True)
        
        
            #--7--map_user_state
            st.title(':green[4--map_user_state]')
            df7 = pd.read_csv(r"C:\Users\shama\phonepe_pulse.csv\phonepe_pulse_table_map_user_state.csv")
            fig7 = px.sunburst(data_frame=df7,path=["Year","Quarter","State","District","Registered_User"],hover_data=["Year","Quarter","State","District","Registered_User"],maxdepth=3)
            st.plotly_chart(fig7,use_container_width=True)
        
            #--9--top_transaction_state
            st.title(':green[5--top_transaction_state]')
            df9 = pd.read_csv(r"C:\Users\shama\phonepe_pulse.csv\phonepe_pulse_table_top_transaction_state.csv")
            fig9 = px.sunburst(data_frame=df9,path=["Year","Quarter","State","District_Pincode","Transaction_count","Transaction_amount"],hover_data=["Year","Quarter","State","District_Pincode","Transaction_count","Transaction_amount"],maxdepth=3)
            st.plotly_chart(fig9,use_container_width=True)

            #--11--top_user_state
            st.title(':green[6--top_user_state]')
            df11 = pd.read_csv(r"C:\Users\shama\phonepe_pulse.csv\phonepe_pulse_table_top_user_state.csv")
            fig11 = px.sunburst(data_frame=df11,path=["Year","Quarter","State","District_Pincode","Registered_User"],hover_data=["Year","Quarter","State","District_Pincode","Registered_User"],maxdepth=3)
            st.plotly_chart(fig11,use_container_width=True)

        
with tab8:
        
        with tab8:
            st.header(':green[over all UnionTerritories Transaction and User Details]')
             #--2--aggregated_transaction_unionterritories
            st.title(':blue[1--aggregated_transaction_unionterritories]')
            df2 = pd.read_csv(r"C:\Users\shama\phonepe_pulse.csv\phonepe_pulse_table_aggregated_transaction_unionterritories.csv")
            fig2 = px.sunburst(data_frame=df2,path=["Year","Quarter","UnionTerritories","Transaction_type","Transaction_count","Transaction_amount"],hover_data=["Year","Quarter","UnionTerritories","Transaction_type","Transaction_count","Transaction_amount"],maxdepth=3)
            st.plotly_chart(fig2,use_container_width=True)

            #--4--aggregated_user_unionterritories
            st.title(':blue[2--aggregated_user_unionterritories]')
            df4 = pd.read_csv(r"C:\Users\shama\phonepe_pulse.csv\phonepe_pulse_table_aggregated_user_unionterritories.csv")
            fig4 = px.sunburst(data_frame=df4,path=["Year","Quarter","UnionTerritories","Brands","User_Count","User_Percentage"],hover_data=["Year","Quarter","UnionTerritories","Brands","User_Count","User_Percentage"],maxdepth=3)
            st.plotly_chart(fig4,use_container_width=True)

            #--6--map_transaction_unionterritories
            st.title(':blue[3--map_transaction_unionterritories]')
            df6 = pd.read_csv(r"C:\Users\shama\phonepe_pulse.csv\phonepe_pulse_table_map_transaction_unionterritories.csv")
            fig6 = px.sunburst(data_frame=df6,path=["Year","Quarter","UnionTerritories","District","Transaction_Count","Transaction_Amount"],hover_data=["Year","Quarter","UnionTerritories","District","Transaction_Count","Transaction_Amount"],maxdepth=3)
            st.plotly_chart(fig6,use_container_width=True)

            #--8--map_user_unionterritories
            st.title(':blue[4--map_user_unionterritories]')
            df8 = pd.read_csv(r"C:\Users\shama\phonepe_pulse.csv\phonepe_pulse_table_map_user_unionterritories.csv")
            fig8 = px.sunburst(data_frame=df8,path=["Year","Quarter","UnionTerritories","District","Registered_User"],hover_data=["Year","Quarter","UnionTerritories","District","Registered_User"],maxdepth=3)
            st.plotly_chart(fig8,use_container_width=True)

            #--10--top_transaction_unionterritories
            st.title(':blue[5--top_transaction_unionterritories]')
            df10 = pd.read_csv(r"C:\Users\shama\phonepe_pulse.csv\phonepe_pulse_table_top_transaction_unionterritories.csv")
            fig10 = px.sunburst(data_frame=df10,path=["Year","Quarter","UnionTerritories","District_Pincode","Transaction_count","Transaction_amount"],hover_data=["Year","Quarter","UnionTerritories","District_Pincode","Transaction_count","Transaction_amount"],maxdepth=3)
            st.plotly_chart(fig10,use_container_width=True)


            #--12--top_user_unionterritories
            st.title(':blue[6--top_user_unionterritories]')
            df12 = pd.read_csv(r"C:\Users\shama\phonepe_pulse.csv\phonepe_pulse_table_top_user_unionterritories.csv")
            fig12 = px.sunburst(data_frame=df12,path=["Year","Quarter","UnionTerritories","District_Pincode","Registered_User"],hover_data=["Year","Quarter","UnionTerritories","District_Pincode","Registered_User"],maxdepth=3)
            st.plotly_chart(fig12,use_container_width=True)
