# Important Libraries
from msilib.schema import Font
from tkinter import X, font
import pandas as pd  
import numpy as np
import plotly as plot
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime , date , timedelta
from plotly import graph_objs as go
from raceplotly.plots import barplot
from wordcloud import WordCloud
from PIL import Image
import altair as alt
from vega_datasets import data as d
import io


st.set_page_config(page_title="Dashboard",
                    page_icon= ":bar_chart:")



#---------------------------- Hide Streamlit Styles ------------------------------

hide_st_style = '''
                <style>
                #MainMenu {visibility : hidden;}
                footer {visibility : hidden;}
                header (visibility : hidden;)
                </style>
                '''

st.markdown(hide_st_style , unsafe_allow_html= True)


#--------------------------------Header Image ---------------------------------


st.write("# Immigration To Canada")

img = Image.open('images/Immigrants.jpg')
st.image(img,
        use_column_width= True)





st.markdown("""
            ### Introduction
Canada is a developed country that has been perceived as open and friendly to people. This sometimes makes it a prime target for a person seeking new life in a totally new world.

Due to the increase of imigration nowadays we have this dataset to analyze the hidden patterns of Immigrants from all over the world to Canada.

The dataset consists of immigrants records from 150+ coutries to Canada between 1980 to 2013.
""")  


#--- 1.Read CSV File ---
df = pd.read_csv(r"data\canadian_immegration_data.csv",index_col= False)



#--- 2.Processing Data ---
df2 = pd.melt(df , id_vars=["Country" , "Continent" ,"Region","DevName","Total"], var_name = ['Year'] , value_name = "Values")

convert_dtype = {"Year": int}
df2 = df2.astype(convert_dtype)

st.dataframe(df2.head())

#--- 3. Reusable Functions ---

def create_lineChart(dframe , choice_selec , year_selec , col_name):
    mask = (dframe[f'{col_name}'].isin(choice_selec)) & (dframe['Year'].between(*year_selec)) 
    number_of_results = dframe[mask].shape[0]
    st.markdown(f'*Available Results: {number_of_results}*')
    data1 = dframe[mask].groupby([f'{col_name}','Year'])['Values'].sum().reset_index()
    data1.reset_index(drop=True,inplace=True)
    data1.set_index('Year')
    piv_table = pd.pivot_table(data = data1 ,values='Values', index=['Year'], columns=[f'{col_name}'])
    #st.dataframe(piv_table.head())
    st.line_chart(piv_table)



# Creating Pie chart
def create_pie_chart(dframe,title,text):
    label=dframe.index
    value=dframe.values
    name=go.Pie(values=value,labels=label,hole=0.5,textposition="inside",textinfo="label+percent+value", marker = dict(colors=['lightgreen','blue']))
    data=[name]
    layout=dict(title=title,title_x=0.5,annotations=[dict(text=text,x=0.5,y=0.5,showarrow=False,font_size=14)],showlegend = False)
    fig=dict(layout=layout,data=data)
    #plot.offline.iplot(fig)
    return fig

def create_bar_plot(dframe, choice_selec, title , col_name, year_selec):
    mask = (dframe[f'{col_name}'].isin(choice_selec)) & (dframe['Year'].between(*year_selec)) 
    # d = dframe[dframe['Year'].between(*year_selec)]
    data1 = dframe[mask].groupby([f'{col_name}'])['Values'].sum().reset_index().sort_values(by = "Values")
    data1.reset_index(drop=True,inplace=True)
    #data1.set_index('Year')
    data2 = data1.head(10)
    fig_bar = px.bar(data2 ,
                    x = f"{col_name}",
                    y = 'Values',
                    # orientation= 'h',
                    color_continuous_scale= "red",
                    title=f"<b>{title}</b>",
                    #template= 'plotly_white',
                    )

    st.plotly_chart(fig_bar)



#--------------------------- Visualize the Data ----------------------------------


# --- Side bar ---
chart_selection = st.sidebar.selectbox(
    label= "Select Chart Type",
    options= ["Lineplots" ,'Barplots','Pie Chart']
)


Years = df2['Year'].unique().tolist()



year_selection = st.slider('Year:',
                            min_value= min(Years),
                            max_value= max(Years),
                            value= (min(Years),max(Years)))
if chart_selection == "Pie Chart":
# --------------- Pie Chart for Dev Regions--------------------
    dataf = df2[df2['Year'].between(*year_selection)]
    dev_regions=dataf["DevName"].value_counts(sort=True)
    st.plotly_chart(create_pie_chart(dev_regions,"Developed Vs. Developing Regions","Regions"))


# --- filter dataframe based on country
if chart_selection == "Lineplots":
    country_checkbox = st.sidebar.checkbox("Country")
    continent_checkbox = st.sidebar.checkbox("Continent")
    region_checkbox = st.sidebar.checkbox("Region")
    dev_checkbox = st.sidebar.checkbox("Developed/Developing Regions")

    if country_checkbox:
        st.markdown('### Immigration to Canada According to Countries in this Timeline')
        Country = df2['Country'].unique().tolist()
        country_Selection = st.multiselect('Choose Country:',
                                    Country,
                                    default= 'Egypt')
    
        create_lineChart(df2 , country_Selection , year_selection , "Country")

#--- Filter Data Based on Continent
    if continent_checkbox:
        st.markdown('### Immigration to Canada According to Continent(s) in this Timeline')
        Continent = df2['Continent'].unique().tolist()
        continent_selection = st.multiselect('Choose Continent:',
                                    Continent,
                                    default= Continent)
        create_lineChart(df2 , continent_selection , year_selection , "Continent")



    if region_checkbox:
        st.markdown('### Immigration to Canada According to Region(s) in this Timeline')
        Region = df2['Region'].unique().tolist()
        region_selection = st.multiselect('Choose Region:',
                                    Region,
                                    default= 'Northern Africa')
        create_lineChart(df2 , region_selection , year_selection , "Region")

    if dev_checkbox:
        st.markdown('### Immigration to Canada According to Developed/Developing Regions in this Timeline')
        Devname = df2["DevName"].unique().tolist()
        dev_selection = st.multiselect('Choose Developed/Developing Regions:',
                                    Devname,
                                    default= ['Developing regions','Developed regions'])
        create_lineChart(df2 , dev_selection , year_selection , "DevName")

    if country_checkbox == continent_checkbox == region_checkbox == dev_checkbox == False:
        st.markdown('### Top 10 Countries in this Timeline')
        dataf = df2[df2['Year'].between(*year_selection)]
        df3 = dataf.groupby(['Country','Year'])['Values'].sum().reset_index()
        df3.reset_index(drop=True,inplace=True)
        df3.set_index('Year')
        df3.sort_values("Values")
        piv_table = pd.pivot_table(data = df3 ,values='Values', index=['Year'], columns=['Country'])
        #st.dataframe(piv_table.head(10))
        st.line_chart(piv_table.tail(10))



if chart_selection == "Barplots":
    country_checkbox = st.sidebar.checkbox("Country")
    continent_checkbox = st.sidebar.checkbox("Continent")
    region_checkbox = st.sidebar.checkbox("Region")
    dev_checkbox = st.sidebar.checkbox("Developed/Developing Regions")

    if country_checkbox:
        #st.markdown('### Immigration to Canada According to Countries in this Timeline')
        Country = df2['Country'].unique().tolist()
        country_Selection = st.multiselect('Choose Country:',
                                    Country,
                                    default= 'Egypt')
        create_bar_plot(df2,country_Selection,'Immigration to Canada According to Countries in this Timeline','Country',year_selection)

#--- Filter Data Based on Continent
    if continent_checkbox:
        st.markdown('### Immigration to Canada According to Continent(s) in this Timeline')
        Continent = df2['Continent'].unique().tolist()
        continent_selection = st.multiselect('Choose Continent:',
                                    Continent,
                                    default= Continent)
        create_bar_plot(df2,continent_selection,'Immigrantion to Canada Over Time','Continent',year_selection)



    if region_checkbox:
        st.markdown('### Immigration to Canada According to Region(s) in this Timeline')
        Region = df2['Region'].unique().tolist()
        region_selection = st.multiselect('Choose Region:',
                                    Region,
                                    default= 'Northern Africa')
        create_bar_plot(df2,region_selection,'Immigrantion to Canada Over Time','Region',year_selection)

    if dev_checkbox:
        st.markdown('### Immigration to Canada According to Developed/Developing Regions in this Timeline')
        Devname = df2["DevName"].unique().tolist()
        dev_selection = st.multiselect('Choose Developed/Developing Regions:',
                                    Devname,
                                    default= ['Developing regions','Developed regions'])
        create_bar_plot(df2,dev_selection,'Immigrantion to Canada Over Time','DevName',year_selection)

    # create_bar_plot(df2,'Top 10 Countries Contributing to Immigrantion to Canada Over Time','Country',year_selection)
     