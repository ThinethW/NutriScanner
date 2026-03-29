import streamlit as st
import tempfile
from pathlib import Path


def show(scanner):
    st.title("📷 Nutrition Label Scanner")
    st.write("Upload a photo of a nutrition label to analyze its contents")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Upload Image")
        uploaded_file = st.file_uploader(
            "Choose nutrition label image",
            type=["jpg", "jpeg", "png"],
            help="Take a clear photo of the nutrition facts table"
        )

        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    with col2:
        st.subheader("Analysis Results")

        if uploaded_file:
            # Save temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            with st.spinner("🔍 Analyzing nutrition label..."):
                try:
                    result = scanner.scan_and_analyze_package(tmp_path)

                    if result.get('success'):
                        st.success("✅ Analysis Complete!")

                        scan_data = result.get('scan_data', {})

                        # Serving info
                        if 'serving_size' in scan_data:
                            st.info(
                                f"**Serving Size:** {scan_data['serving_size']}{scan_data.get('serving_unit', 'g')}")

                        # Per serving values
                        st.markdown("#### Per Serving:")
                        col_a, col_b = st.columns(2)

                        with col_a:
                            st.metric("Energy", f"{scan_data.get('energy_kcal_per_serving', 0):.1f} kcal")
                            st.metric("Protein", f"{scan_data.get('protein_per_serving_g', 0):.1f}g")
                            st.metric("Carbs", f"{scan_data.get('carbs_per_serving_g', 0):.1f}g")

                        with col_b:
                            st.metric("Fat", f"{scan_data.get('fat_per_serving_g', 0):.1f}g")
                            st.metric("Fiber", f"{scan_data.get('fiber_per_serving_g', 0):.1f}g")
                            st.metric("Sodium", f"{scan_data.get('sodium_per_serving_mg', 0):.1f}mg")

                        # Health scores
                        st.markdown("### Health Scores")
                        health_indexes = result.get('health_indexes', {})

                        for index_name, score in health_indexes.items():
                            if score >= 75:
                                rating = "Excellent 🟢"
                            elif score >= 50:
                                rating = "Good 🟡"
                            else:
                                rating = "Needs Attention 🔴"

                            st.progress(score / 100, text=f"{index_name}: {score:.1f}/100 ({rating})")

                        # Visualizations
                        viz_paths = result.get('visualizations', {})
                        if viz_paths:
                            st.markdown("### Detailed Analysis")
                            for name, path in viz_paths.items():
                                if Path(path).exists():
                                    st.image(path, caption=name.replace('_', ' ').title(), use_container_width=True)

                    else:
                        st.error(f"❌ {result.get('error', 'Analysis failed')}")

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

        else:
            st.info("👆 Upload an image to start")