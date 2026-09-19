import streamlit as st
import tempfile
import os
import cv2
import pandas as pd

from scene_detector import detect_scenes


# -----------------------------
# Page Configuration
# -----------------------------

st.set_page_config(
    page_title="AI Video Indexing",
    page_icon="🎥",
    layout="wide"
)


# -----------------------------
# Title
# -----------------------------

st.title("🎥 AI-Based Video Indexing and Scene Detection System")

st.write(
    "Upload a video to automatically detect scene changes "
    "and generate a searchable video index."
)


# -----------------------------
# Video Upload
# -----------------------------

uploaded_file = st.file_uploader(
    "📂 Upload your video",
    type=["mp4", "avi", "mov", "mkv"]
)


if uploaded_file is not None:

    st.success("✅ Video uploaded successfully!")

    # Display uploaded video
    st.video(uploaded_file)

    # -----------------------------
    # Analyze Button
    # -----------------------------

    if st.button("🔍 Analyze Video"):

        with st.spinner("Analyzing video..."):

            # Save uploaded video temporarily
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            ) as temp_file:

                temp_file.write(
                    uploaded_file.read()
                )

                video_path = temp_file.name

            # -----------------------------
            # Get Video Information
            # -----------------------------

            cap = cv2.VideoCapture(video_path)

            fps = cap.get(
                cv2.CAP_PROP_FPS
            )

            total_frames = cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )

            if fps > 0:
                duration = total_frames / fps
            else:
                duration = 0

            cap.release()

            # -----------------------------
            # Detect Scenes
            # -----------------------------

            scenes = detect_scenes(
                video_path
            )

        # -----------------------------
        # Video Analysis
        # -----------------------------

        st.subheader("📊 Video Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "⏱️ Video Duration",
                f"{duration:.1f} seconds"
            )

        with col2:
            st.metric(
                "🎬 Scenes Detected",
                len(scenes)
            )

        st.divider()

        # -----------------------------
        # Video Index
        # -----------------------------

        st.subheader("📑 Video Index")

        if len(scenes) == 0:

            st.warning(
                "No major scene changes were detected."
            )

        else:

            csv_data = []

            # -----------------------------
            # Display Scenes
            # -----------------------------

            for i, scene in enumerate(
                scenes,
                start=1
            ):

                timestamp = scene["timestamp"]

                # Convert seconds to MM:SS
                minutes = int(
                    timestamp // 60
                )

                seconds = int(
                    timestamp % 60
                )

                formatted_time = (
                    f"{minutes:02d}:{seconds:02d}"
                )

                # -----------------------------
                # Add CSV Data
                # -----------------------------

                csv_data.append({
                    "Scene": f"Scene {i}",
                    "Timestamp": formatted_time,
                    "Time (seconds)": round(
                        timestamp,
                        2
                    ),
                    "Frame Number": scene["frame"],
                    "Scene Change Score": scene["score"]
                })

                # -----------------------------
                # Scene Display
                # -----------------------------

                col1, col2 = st.columns(
                    [1, 2]
                )

                with col1:

                    if os.path.exists(
                        scene["preview_path"]
                    ):

                        st.image(
                            scene["preview_path"],
                            caption=f"Scene {i}",
                            width=300
                        )

                with col2:

                    st.markdown(
                        f"### 🎬 Scene {i}"
                    )

                    st.write(
                        f"⏱️ **Timestamp:** "
                        f"{formatted_time}"
                    )

                    st.write(
                        f"📌 **Frame Number:** "
                        f"{scene['frame']}"
                    )

                    st.write(
                        f"📈 **Scene Change Score:** "
                        f"{scene['score']}"
                    )

                    st.write(
                        "🖼️ **Preview:** "
                        "Scene change detected"
                    )

                st.divider()

            # -----------------------------
            # Create DataFrame
            # -----------------------------

            df = pd.DataFrame(
                csv_data
            )

            # -----------------------------
            # Scene Index Table
            # -----------------------------

            st.subheader(
                "📋 Scene Index Table"
            )

            st.dataframe(
                df,
                use_container_width=True
            )

            # -----------------------------
            # CSV Download
            # -----------------------------

            csv_file = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                label="⬇️ Download Video Index CSV",
                data=csv_file,
                file_name="video_index.csv",
                mime="text/csv"
            )

        # -----------------------------
        # Remove Temporary Video
        # -----------------------------

        os.remove(video_path)