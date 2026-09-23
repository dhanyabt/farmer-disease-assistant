"""HACKMINT farmer-facing Streamlit application."""

import streamlit as st

from api_client import (
    ApiClientError,
    analyze_crop,
)

from ui_components import render_diagnosis


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="HACKMINT",
    page_icon="🌿",
    layout="centered",
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.title("HACKMINT")

st.caption(
    "AI-Powered Crop Disease Assistance"
)

st.write(
    "Upload a crop image and describe the symptoms. "
    "HACKMINT combines image analysis, symptom context "
    "and location-aware reporting."
)


# ---------------------------------------------------------
# FARMER INPUT FORM
# ---------------------------------------------------------

with st.form("farmer_input"):

    st.header("🌱 Farmer Input")

    image = st.file_uploader(
        "Upload a crop or leaf image",
        type=[
            "jpg",
            "jpeg",
            "png",
        ],
        help=(
            "Use a clear, well-lit image "
            "of the affected area."
        ),
    )

    crop_name = st.text_input(
        "Crop name",
        placeholder="Example: Tomato",
    )

    plant_part = st.selectbox(
        "Affected plant part",
        [
            "Leaf",
            "Stem",
            "Fruit",
            "Root",
            "Other",
        ],
    )

    symptoms = st.text_area(
        "Symptoms / description",
        placeholder=(
            "Example: Brown spots and "
            "yellowing on older leaves."
        ),
        height=120,
    )

    st.subheader("📍 Farmer Location")

    location = st.text_input(
        "Village / Area",
        placeholder=(
            "Example: Coimbatore, Tamil Nadu"
        ),
    )

    submitted = st.form_submit_button(
        "Analyze Crop",
        type="primary",
    )


# ---------------------------------------------------------
# IMAGE PREVIEW
# ---------------------------------------------------------

if image is not None:

    st.subheader("🖼️ Image Preview")

    st.image(
        image,
        caption=image.name,
        use_container_width=True,
    )


# ---------------------------------------------------------
# ANALYSIS
# ---------------------------------------------------------

if submitted:

    if image is None:

        st.error(
            "Please upload a crop image "
            "before analyzing."
        )

    elif not crop_name.strip():

        st.error(
            "Please enter the crop name."
        )

    elif not symptoms.strip():

        st.error(
            "Please describe the symptoms "
            "you observe."
        )

    elif not location.strip():

        st.error(
            "Please enter the farmer's location."
        )

    else:

        with st.spinner(
            "Connecting image and symptom analysis..."
        ):

            try:

                result = analyze_crop(
                    image=image,
                    crop_name=crop_name.strip(),
                    plant_part=plant_part,
                    symptoms=symptoms.strip(),
                    location=location.strip(),
                )

            except ApiClientError as exc:

                st.error(str(exc))

            else:

                st.session_state[
                    "last_result"
                ] = result

                st.session_state[
                    "last_location"
                ] = location.strip()

                st.session_state[
                    "last_crop"
                ] = crop_name.strip()

                st.session_state[
                    "last_plant_part"
                ] = plant_part

                st.session_state[
                    "last_symptoms"
                ] = symptoms.strip()


# ---------------------------------------------------------
# DIAGNOSIS REPORT
# ---------------------------------------------------------

if "last_result" in st.session_state:

    st.divider()

    st.header(
        "📋 HACKMINT Diagnosis Report"
    )

    st.subheader(
        "Farmer Report"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.write(
            f"**Crop:** "
            f"{st.session_state.get('last_crop', 'Unknown')}"
        )

        st.write(
            f"**Affected part:** "
            f"{st.session_state.get('last_plant_part', 'Unknown')}"
        )

    with col2:

        st.write(
            f"**Location:** "
            f"{st.session_state.get('last_location', 'Unknown')}"
        )

    st.write(
        f"**Symptoms:** "
        f"{st.session_state.get('last_symptoms', 'Not provided')}"
    )

    st.subheader(
        "🤖 AI Analysis"
    )

    render_diagnosis(
        st,
        st.session_state["last_result"],
    )