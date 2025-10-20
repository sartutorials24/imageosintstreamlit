import streamlit as st
from PIL import Image
import pytesseract
import exifread
import io
import base64
import json

st.set_page_config(page_title="SARPATH Image Extractor", page_icon="🧠", layout="wide")

st.markdown("""
<style>
body {
    background-color: #0b1220;
    color: #e6eef8;
}
h1, h2, h3 {
    color: #60a5fa;
}
.stButton>button {
    background-color: #10b981;
    color: white;
    border-radius: 8px;
    border: none;
    padding: 10px 16px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 SARPATH Image Extractor")
st.write("Upload an image to extract metadata, GPS coordinates, OCR text, and access reverse image search links.")

uploaded_file = st.file_uploader("📸 Upload an image", type=["jpg", "jpeg", "png", "webp", "tiff"])

if uploaded_file is not None:
    # Load image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Save temp file for processing
    temp_bytes = io.BytesIO(uploaded_file.getvalue())

    # Extract EXIF using exifread
    tags = exifread.process_file(temp_bytes, details=False)
    exif_data = {tag: str(value) for tag, value in tags.items()}

    st.subheader("📷 EXIF Metadata")
    if exif_data:
        st.json(exif_data)
    else:
        st.info("No EXIF metadata found.")

    # GPS extraction
    def convert_to_degress(value):
        d = float(value.values[0].num) / float(value.values[0].den)
        m = float(value.values[1].num) / float(value.values[1].den)
        s = float(value.values[2].num) / float(value.values[2].den)
        return d + (m / 60.0) + (s / 3600.0)

    lat = lon = None
    try:
        gps_latitude = tags.get('GPS GPSLatitude')
        gps_latitude_ref = tags.get('GPS GPSLatitudeRef')
        gps_longitude = tags.get('GPS GPSLongitude')
        gps_longitude_ref = tags.get('GPS GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = convert_to_degress(gps_latitude)
            if gps_latitude_ref.values != 'N':
                lat = -lat
            lon = convert_to_degress(gps_longitude)
            if gps_longitude_ref.values != 'E':
                lon = -lon
    except Exception:
        pass

    if lat and lon:
        st.subheader("🌍 GPS Coordinates Found")
        st.write(f"**Latitude:** {lat}")
        st.write(f"**Longitude:** {lon}")
        st.markdown(f"[🌐 View on Google Maps](https://www.google.com/maps?q={lat},{lon})")
    else:
        st.warning("No GPS coordinates found in EXIF data.")

    # OCR text extraction
    st.subheader("📝 OCR (Text Extraction)")
    try:
        ocr_text = pytesseract.image_to_string(image)
        if ocr_text.strip():
            st.text_area("Extracted Text", ocr_text, height=200)
        else:
            st.info("No readable text detected in this image.")
    except Exception as e:
        st.error(f"OCR failed: {e}")

    # Generate reverse image search URLs using base64 inline encoding
    img_bytes = uploaded_file.getvalue()
    b64_img = base64.b64encode(img_bytes).decode('utf-8')
    data_url = f"data:image/jpeg;base64,{b64_img}"

    st.subheader("🔎 Reverse Image Search")
    st.markdown("""
    To use reverse image search, please **download the file** and upload it manually to these engines:
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.link_button("Google Images", "https://images.google.com/")
    with col2:
        st.link_button("TinEye", "https://tineye.com/")
    with col3:
        st.link_button("Bing Visual Search", "https://www.bing.com/visualsearch")
    with col4:
        st.link_button("SauceNAO", "https://saucenao.com/")

    st.download_button("💾 Download Uploaded Image", data=uploaded_file.getvalue(),
                       file_name=uploaded_file.name, mime=uploaded_file.type)

    st.success("✅ Analysis Complete!")
else:
    st.info("Please upload an image to begin.")
