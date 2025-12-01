import streamlit as st
import google.generativeai as genai
import base64
from io import BytesIO
from PIL import Image


st.set_page_config(page_title="Eco Waste Advisor", layout="centered")

st.title("Eco Waste Advisor")
st.write("Take a photo of your waste and get eco-friendly disposal recommendations")

genai.configure(api_key=st.secrets["GEMINI_API_KEY"]) # type: ignore
model = genai.GenerativeModel("gemini-2.5-flash") # type: ignore

camera_image = st.camera_input("Take a photo of your waste")

if camera_image is not None:
    st.image(camera_image, caption="Captured image", use_column_width=True)
    
    image_data = camera_image.read()
    
    if st.button("Get Disposal Recommendations"):
        with st.spinner("Analyzing your waste..."):
            response = model.generate_content([
                "Please analyze this image of waste/items and provide eco-friendly and carbon-free disposal recommendations. Include: 1) What items you see, 2) Best recycling/disposal methods, 3) Environmental impact considerations. Keep it concise and actionable and keep it simple and short.",
                {"mime_type": "image/jpeg", "data": image_data}
            ])
            
            st.success("Recommendations:")
            st.write(response.text)
else:
    st.info("Use the camera input above to capture an image of waste or items you want to dispose of responsibly.")
