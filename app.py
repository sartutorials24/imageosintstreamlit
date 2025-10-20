import streamlit as st
from PIL import Image
import pytesseract
import exifread
import base64
import io

st.set_page_config(page_title="SARPATH Image Intelligence", page_icon="🧠", layout="wide")

st.markdown("""
# 🧠 SARPATH Image Intelligence Tool
Upload an image to analyze its EXIF metadata, GPS location, OCR text, and get reverse image search links.
""")

uploaded_file = st.file_uploader("📸 Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    # Save temporarily
    temp_bytes = io.BytesIO()
    image.save(temp_bytes, format=image.format or "JPEG")
    temp_bytes.seek(0)
    
    # === EXIF Extraction ===
    st.subheader("📷 EXIF Metadata")
    temp_bytes.seek(0)
    tags = exifread.process_file(temp_bytes, details=False)
    
    if tags:
        st.json({k: str(v) for k, v in tags.items()})
    else:
        st.warning("No EXIF metadata found in this image.")
    
    # === GPS Extraction ===
    def convert_to_degrees(value):
        try:
            d = float(value.values[0].num) / float(value.values[0].den)
            m = float(value.values[1].num) / float(value.values[1].den)
            s = float(value.values[2].num) / float(value.values[2].den)
            return d + (m / 60.0) + (s / 3600.0)
        except Exception:
            return None
    
    lat = lon = None
    if "GPS GPSLatitude" in tags and "GPS GPSLongitude" in tags:
        lat = convert_to_degrees(tags["GPS GPSLatitude"])
        lon = convert_to_degrees(tags["GPS GPSLongitude"])
        if "GPS GPSLatitudeRef" in tags and str(tags["GPS GPSLatitudeRef"]) != "N":
            lat = -lat
        if "GPS GPSLongitudeRef" in tags and str(tags["GPS GPSLongitudeRef"]) != "E":
            lon = -lon

    if lat and lon:
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        st.success(f"✅ GPS Coordinates Found: {lat}, {lon}")
        st.markdown(f"[🌍 View on Google Maps]({maps_link})")
    else:
        st.error("❌ No GPS data found in this image.")
    
    # === OCR Extraction ===
    st.subheader("🧠 OCR (Text Extraction)")
    try:
        ocr_text = pytesseract.image_to_string(image)
        if ocr_text.strip():
            st.text_area("Extracted Text", ocr_text, height=200)
        else:
            st.warning("No text detected in the image.")
    except Exception as e:
        st.error(f"OCR Error: {e}")

    # === Reverse Image Search ===
    st.subheader("🌐 Reverse Image Search")
    # Encode image to base64
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    img_data_uri = f"data:image/jpeg;base64,{img_str}"

    st.markdown("Click below to search this image on popular reverse image engines:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"[🧭 Google Images](https://lens.google.com/uploadbyurl?url={img_data_uri})", unsafe_allow_html=True)
    with col2:
        st.markdown(f"[🔎 TinEye](https://tineye.com/)", unsafe_allow_html=True)
    with col3:
        st.markdown(f"[🪞 Bing Images](https://www.bing.com/images/trending)", unsafe_allow_html=True)
    
    st.success("✅ Analysis Complete!")
else:
    st.info("👆 Upload an image to begin analysis.")
