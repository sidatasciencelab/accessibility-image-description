import streamlit as st
import streamlit.components.v1 as components

import csv
import requests
from cs50 import SQL
from PIL import Image
import time
import concurrent.futures
import os
import pandas as pd
import glob
import numpy as np

from st_aggrid import AgGrid, JsCode, ColumnsAutoSizeMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

def remove_images():

    '''function that removes images from local storage when the page increments'''
    
    files = glob.glob('images/*')
    for f in files:
        os.remove(f)

def save_image_from_url(url, img_no, output_folder):

    '''downloads images from web into local storage'''
    
    image = requests.get(url)
    output_path = os.path.join(
        output_folder, 'img_' + str(img_no) + ".png"
    )
    with open(output_path, "wb") as f:
        f.write(image.content)


def load(df, output_folder):
    
    '''uses multithreading to get images from web for current page quickly '''
    
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=5
    ) as executor:
        future_to_url = {
            executor.submit(save_image_from_url, row['src'], row['img_no'], output_folder): row['src']
            for _, row in df.iterrows()
        }
        for future in concurrent.futures.as_completed(
            future_to_url
        ):
            url = future_to_url[future]
            try:
                future.result()
            except Exception as exc:
                print(
                    "%r generated an exception: %s" % (url, exc)
                )



def on_select():
    
    #resets the interface when a different website is selected
    
    st.session_state.reset = 1
    
    
db = SQL("sqlite:///si_imgs.db")

def alt_update():

    user_input = st.session_state.input
    
    db.execute('''UPDATE imgs
                SET approved_alt = %r
                WHERE img_no = %s''' % (user_input, im_select))

    df = st.session_state.img_data

    

    df.loc[df.img_no == im_select, 'approved_alt'] = user_input

    st.session_state.img_data = df

def update_imgs():

    df = pd.DataFrame.from_records(db.execute('''SELECT * FROM imgs
    WHERE `approved_alt` IS NULL
    AND `site_url` = %s
    AND (`src` LIKE '%.png%' OR `src` LIKE '%.jpg%')
    LIMIT 10''', (site_url)))

    df = df[['img_no', 'src', 'alt', 'model_alts', 'site_url', 'approved_alt']]

    st.session_state.img_data = df

    

# dataframe we'll use to produce the current page

if 'selection' not in st.session_state:
    st.session_state.selection = "Natural History Museum"

museum_dict = {"Natural History Museum": 'https://naturalhistory.si.edu',
               "Green Book": 'https://negromotoristgreenbook.si.edu',
               "Museum of Asian Art": 'https://asia.si.edu'
               }

site_url = museum_dict[st.session_state.selection]




if 'img_data' not in st.session_state:
    df = pd.DataFrame.from_records(db.execute('''SELECT * FROM imgs
    WHERE `approved_alt` IS NULL
    AND `site_url` = %s
    AND (`src` LIKE '%.png%' OR `src` LIKE '%.jpg%')
    LIMIT 10''', (site_url)))

    df = df[['img_no', 'src', 'alt', 'model_alts', 'site_url', 'approved_alt']]

    st.session_state.img_data = df


if 'reset' not in st.session_state:
    st.session_state.reset = 0
    
    remove_images()
    load(st.session_state.img_data, 'images/')
    time.sleep(3)

# clears page of images + reloads
if st.session_state.reset:
    remove_images()

    load(st.session_state.img_data, 'images/')
    st.session_state.reset = 0
    time.sleep(5)

# this script moves the focus to the top of the page on submit

js = '''
<script>
    var body = window.parent.document.querySelector(".main");
    console.log(body);
    body.scrollTo({top: 0, behavior: 'smooth'});
</script>
'''

st.set_page_config(layout="wide")


st.title("Model-Generated Alternative Text")

st.header("Approve, revise, or reject the following image descriptions generated by BLIP-2")

st.selectbox(
    "Choose the website whose images you would like to work on",
    ("Natural History Museum", "Green Book", "Museum of Asian Art"),
    key="selection",
    on_change=on_select)


thumbnail_renderer = JsCode("""
    class ThumbnailRenderer {
    init(params) {
    this.eGui = document.createElement('img');
    this.eGui.setAttribute('src', params.value);
    this.eGui.setAttribute('width', '100');
    this.eGui.setAttribute('height', 'auto');
    }
    getGui() {
    return this.eGui;
    }
    }
""")


options_builder = GridOptionsBuilder.from_dataframe(st.session_state.img_data)
options_builder.configure_column('src', cellRenderer = thumbnail_renderer)
options_builder.configure_column('img_no', hide="True")
options_builder.configure_selection(selection_mode="single", use_checkbox=False)
grid_options = options_builder.build()

grid = AgGrid(st.session_state.img_data, 
                gridOptions = grid_options,
                allow_unsafe_jscode=True,
                height=350, width=500, theme='streamlit',
                columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)



if grid['selected_rows']:

    row_select = grid['selected_rows'][0]
    im_select = row_select['img_no']

    for i in range(2):
        st.write("")

    col1, col2 = st.columns(2)

    with col1:
        src = row_select['src']
        im = Image.open(requests.get(src, stream=True).raw)
        st.image(im)

    with col2:
        model_alt = grid['selected_rows'][0]['model_alts']

        if model_alt[0] == "[":
            model_alt = model_alt[2:-2]
        current_alt = grid['selected_rows'][0]['alt']

        width, height = im.size

        text = "Model alt text: " + model_alt
        curr_alt_text = "Current alt text: " + current_alt

        #st.write(curr_alt_text)

        st.markdown("<font size = '5'>{curr_alt}</font>".format(curr_alt=curr_alt_text), unsafe_allow_html=True)

        for i in range(7):
            st.write('')


        st.markdown("<font size = '5'>{model_alt}</font>".format(model_alt=text), unsafe_allow_html=True)

        for i in range(6):
            st.write('')

        user_input = st.text_input("Enter approved alt-text here", key="input", on_change=alt_update)


    
    
else:
    st.write("No row selected")

st.button("Update Images", on_click=update_imgs)
