import streamlit as st
import google.generativeai as genai
import base64
from io import BytesIO
from PIL import Image


if "response" not in st.session_state:
    st.session_state.response = None

st.set_page_config(page_title="Eco Waste Advisor", layout="centered")

st.title("Food Ecofriendly Advisor")
st.write("Take a photo of your food and get eco-friendly recommendations")

genai.configure(api_key="AIzaSyC_a87tIh1bF2jCKOnXbiHjcrK9jjstpCk") # type: ignore
model = genai.GenerativeModel("gemini-2.5-flash") # type: ignore

camera_image = st.camera_input("Take a photo of your food", )

if camera_image is not None:
    st.image(camera_image, caption="Captured image", use_container_width=True)
    
    image_data = camera_image.read()
    
    if st.button("Get food Recommendations"):
        with st.spinner("Analyzing your food..."):
            response = model.generate_content([
                """Please analyze this image of food.
                return it in this valid JSON format ONLY:
                {"Impact": (only return "high" or "medium" or "low" or "Invalid Image"), "Recommendations": "some recommendations in a bullet list format if there are any, if not then just return no recommendations"}
                """,
                {"mime_type": "image/jpeg", "data": image_data}
            ])

            raw = response.text

            import re, json
            match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
            if match:
                json_str = match.group(0)
                st.session_state.response = json.loads(json_str)
            else:
                st.error("Model did not return valid JSON.")
                st.write(raw)  
            
else:
    st.info("Use the camera input above to capture an image of food or items to help the environment.")

if st.session_state.response:
    response = st.session_state.response
    if response["Impact"] == "Invalid Image":
        st.error("The image provided is invalid. Please try again with a different image.")
    elif response["Impact"] == "high":
        st.error(f"Environmental Impact: ☢️ {response['Impact'].upper()} ☢️")
    elif response["Impact"] == "medium":
        st.warning(f"Environmental Impact: ⚠️ {response['Impact'].upper()} ⚠️")
    else:
        st.success(f"Environmental Impact: ✅ {response['Impact'].upper()} ✅")
    
    st.markdown("### Recommendations:")
    recommendations = response["Recommendations"].strip().split("\n")
