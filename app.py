import streamlit as st
from PIL import Image
import google.generativeai as genai
from google import genai as image_genai
from google.genai import types

import pandas as pd


client = image_genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

genai.configure(api_key=st.secrets["GEMINI_API_KEY"]) # type: ignore
model = genai.GenerativeModel(model_name="gemini-2.5-flash") # type: ignore
image_model = genai.GenerativeModel(model_name="gemini-2.5-flash-image") # type: ignore

if "data" not in st.session_state:
    st.session_state.data = []

if "image" not in st.session_state:
    st.session_state.image = Image

if "polluted_image" not in st.session_state:
    st.session_state.polluted_image = Image

if "non_polluted_image" not in st.session_state:
    st.session_state.non_polluted_image = Image

if "asked_ai" not in st.session_state:
    st.session_state.asked_ai = False

st.title("Land pollution Predictor")

st.text("Upload a satellite image from google maps or another platform of a location on the map to analyze its current pollution state and predict future pollution levels.")

file = st.file_uploader("Upload image of map", type=["png", "jpeg", "jpg"])

if file:
    sat_image = Image.open(file)
    st.session_state.image = sat_image
    st.image(sat_image)

if st.button("Analyze image"):
    if file:    
        sat_image = Image.open(file)
        with st.spinner("Analyzing image"):
            response = model.generate_content([
                """Analyze the satellite image and return the following:
                [
                {"current_map_state": "the current state of the satellite image place"},

                {"polluted_percentages_after_10_years": [
                
                    {"oxygen":
                    {"value": value after 10 years, 
                    "delta": delta from the last 10 years. can be in minus, 
                    "dataframe": example:{"2025": 10, "2026": 12}}, 
                    
                    {"CO2": 
                    {"value": (value after 10 years, should increase), 
                    "delta": delta from the last 10 years. can be in minus, 
                    "dataframe": example:{"2025": 10, "2026": 12}} }, 

                    {"greenery": 
                    {"value": value after 10 years, 
                    "delta": delta from the last 10 years. can be in minus, 
                    "dataframe": example:{"2025": 10, "2026": 12}} }]},

                {"advice": "advice for the user"},

                {"non_polluted_percentages_after_10_years": [
                
                    {"oxygen":
                    {"value": value after 10 years, 
                    "delta": delta from the last 10 years. can be in minus, 
                    "dataframe": example:{"2025": 10, "2026": 12}}, 
                    
                    {"CO2": 
                    {"value": (value after 10 years, should increase), 
                    "delta": delta from the last 10 years. can be in minus, 
                    "dataframe": example:{"2025": 10, "2026": 12}} }, 

                    {"greenery": 
                    {"value": value after 10 years, 
                    "delta": delta from the last 10 years. can be in minus, 
                    "dataframe": example:{"2025": 10, "2026": 12}} }]},
                
                ]

                the current map state should return the state of the land shown in the uploaded image. it should be simple and describe the pollution and the greenery of the land and the possible causes.
                the dataframes_for_polluted should return the dataframes for the future 10 years of pollution in that placethat show for example oxygen precentages and CO2 and greenery
                the advice should be information on how to reduce pollution on that area
                the dataframes_for_non_polluted should return the dataframes for the future 10 years if you listened for the advice given above that show for example oxygen precentages and CO2 and greenery
                The values should be returned in JSON format only
                """, sat_image
                
            ])
        raw = response.text

            
        import re, json
        match = re.search(r"\[.*\]", raw, flags=re.DOTALL)
        if match:
            json_str = match.group(0)
            st.session_state.data = json.loads(json_str)
            #st.success(str(st.session_state.data))
        else:
            st.error("Model did not return valid JSON.")
            st.write(raw)        
    else:
        st.error("No file found")

if st.session_state.data:
    dictionary = st.session_state.data
    st.header("Current Map State")
    st.write(dictionary[0]["current_map_state"])
    st.header("Polluted Charts")
    st.markdown("*Predicted pollution levels after 10 years if pollution continues to increase:*")

    poll_ox_percentages = dictionary[1]["polluted_percentages_after_10_years"][0]["oxygen"]["value"]
    delta_poll_ox_percentages = dictionary[1]["polluted_percentages_after_10_years"][0]["oxygen"]["delta"]
    poll_ox_df = pd.DataFrame.from_dict(dictionary[1]["polluted_percentages_after_10_years"][0]["oxygen"]["dataframe"], orient='index', columns=['Oxygen Percentage'])

    poll_co2_percentages = dictionary[1]["polluted_percentages_after_10_years"][1]["CO2"]["value"]
    delta_poll_co2_percentages = dictionary[1]["polluted_percentages_after_10_years"][1]["CO2"]["delta"]
    poll_co2_df = pd.DataFrame.from_dict(dictionary[1]["polluted_percentages_after_10_years"][1]["CO2"]["dataframe"], orient='index', columns=['CO2 Percentage'])

    poll_green_percentages = dictionary[1]["polluted_percentages_after_10_years"][2]["greenery"]["value"]
    delta_poll_green_percentages = dictionary[1]["polluted_percentages_after_10_years"][2]["greenery"]["delta"]
    poll_green_df = pd.DataFrame.from_dict(dictionary[1]["polluted_percentages_after_10_years"][2]["greenery"]["dataframe"], orient='index', columns=['Green land Percentage'])


    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Oxygen after 10 years", str(poll_ox_percentages) + "%")
        st.badge("Change: " + str(delta_poll_ox_percentages) + "%", color="red")
        st.line_chart(poll_ox_df, use_container_width=True)
    with c2:
        st.metric("CO2 after 10 years", str(poll_co2_percentages) + "%")
        st.badge("Change: " + str(delta_poll_co2_percentages) + "%", color="red")
        st.line_chart(poll_co2_df, use_container_width=True)
    with c3:
        st.metric("Green land after 10 years", str(poll_green_percentages) + "%")
        st.badge("Change: " + str(delta_poll_green_percentages) + "%", color="red")
        st.line_chart(poll_green_df, use_container_width=True)

    st.header("Advice")
    st.success(dictionary[2]["advice"])

    non_poll_ox_percentages = dictionary[3]["non_polluted_percentages_after_10_years"][0]["oxygen"]["value"]
    delta_non_poll_ox_percentages = dictionary[3]["non_polluted_percentages_after_10_years"][0]["oxygen"]["delta"]
    non_poll_ox_df = pd.DataFrame.from_dict(dictionary[3]["non_polluted_percentages_after_10_years"][0]["oxygen"]["dataframe"], orient='index', columns=['Oxygen Percentage'])

    non_poll_co2_percentages = dictionary[3]["non_polluted_percentages_after_10_years"][1]["CO2"]["value"]
    delta_non_poll_co2_percentages = dictionary[3]["non_polluted_percentages_after_10_years"][1]["CO2"]["delta"]
    non_poll_co2_df = pd.DataFrame.from_dict(dictionary[3]["non_polluted_percentages_after_10_years"][1]["CO2"]["dataframe"], orient='index', columns=['CO2 Percentage'])

    non_poll_green_percentages = dictionary[3]["non_polluted_percentages_after_10_years"][2]["greenery"]["value"]
    delta_non_poll_green_percentages = dictionary[3]["non_polluted_percentages_after_10_years"][2]["greenery"]["delta"]
    non_poll_green_df = pd.DataFrame.from_dict(dictionary[3]["non_polluted_percentages_after_10_years"][2]["greenery"]["dataframe"], orient='index', columns=['Green land Percentage'])

    st.header("Non Polluted Charts")
    st.markdown("*Predicted pollution levels after 10 years if you follow the advice:*")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Oxygen after 10 years", str(non_poll_ox_percentages) + "%")
        st.badge("Change: " + str(delta_non_poll_ox_percentages) + "%", color="green")
        st.line_chart(non_poll_ox_df, use_container_width=True)
    with c2:
        st.metric("CO2 after 10 years", str(non_poll_co2_percentages) + "%")
        st.badge("Change: " + str(delta_non_poll_co2_percentages) + "%", color="green")
        st.line_chart(non_poll_co2_df, use_container_width=True)
    with c3:
        st.metric("Green Land after 10 years", str(non_poll_green_percentages) + "%")
        st.badge("Change: " + str(delta_non_poll_green_percentages) + "%", color="green")
        st.line_chart(non_poll_green_df, use_container_width=True)
  
if st.session_state.data:
    if st.session_state.asked_ai == False:
        if st.button("Ask questions about land pollution"):
            st.session_state.asked_ai = True

if st.session_state.asked_ai:
    st.title("Any Questions about Land Pollution? Ask me!")


    if "model" not in st.session_state:
        st.session_state.model = "gemini-2.5-flash"  
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    if prompt := st.chat_input("Ask me something"):
        st.session_state.messages.append({"role": "user", "content": "use this data to answer the user about land pollution: " + str(st.session_state.data) + prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        model = genai.GenerativeModel(st.session_state.model) # type: ignore
        chat = model.start_chat(history=[
            {"role": msg["role"], "parts": [msg["content"]]} for msg in st.session_state.messages
        ])
        response = chat.send_message(prompt)

        reply = response.text
        with st.chat_message("assistant"):
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})

