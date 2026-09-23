"""HACKMINT farmer-facing Streamlit application."""

import streamlit as st

from api_client import ApiClientError, analyze_crop
from ui_components import render_diagnosis


st.set_page_config(page_title="HACKMINT", page_icon="🌿", layout="centered")
st.title("HACKMINT")
st.caption("AI-Powered Crop Disease Assistance")
st.write(
    "Upload a crop image and describe what you see. HACKMINT combines image "
    "analysis with symptom context to suggest the next best action."
)

with st.form("farmer_input"):
    st.header("Farmer input")
    image = st.file_uploader(
        "Upload a crop or leaf image",
        type=["jpg", "jpeg", "png"],
        help="Use a clear, well-lit image of the affected area.",
    )
    crop_name = st.text_input("Crop name", placeholder="Tomato")
    plant_part = st.selectbox(
        "Affected plant part", ["Leaf", "Stem", "Fruit", "Root", "Other"]
    )
    symptoms = st.text_area(
        "Symptoms / description",
        placeholder="Brown spots and yellowing on older leaves.",
        height=120,
    )
    submitted = st.form_submit_button("Analyze Crop", type="primary")

if image is not None:
    st.subheader("Image preview")
    st.image(image, caption=image.name, use_container_width=True)

if submitted:
    if image is None:
        st.error("Please upload a crop image before analyzing.")
    elif not crop_name.strip():
        st.error("Please enter the crop name.")
    elif not symptoms.strip():
        st.error("Please describe the symptoms you observe.")
    else:
        with st.spinner("Connecting image and symptom analysis..."):
            try:
                result = analyze_crop(
                    image=image,
                    crop_name=crop_name.strip(),
                    plant_part=plant_part,
                    symptoms=symptoms.strip(),
                )
            except ApiClientError as exc:
                st.error(str(exc))
            else:
                st.session_state["last_result"] = result

if "last_result" in st.session_state:
    render_diagnosis(st, st.session_state["last_result"])
