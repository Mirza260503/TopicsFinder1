import streamlit as st
import requests
from datetime import datetime, timedelta

# Secure API Key Storage (Add in Streamlit Secrets)
API_KEY = st.secrets["YOUTUBE_API_KEY"]

# YouTube API URLs
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# Streamlit App Title
st.title("YouTube Viral Topics Tool")

# Input Field
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# List of Keywords
keywords = [
    "Trending Stories", "Interesting Stories", "Fictional Stories", "Daily Stories", "New Stories",
    "Unique Stories", "Hidden Stories", "Untold Tales", "Mysterious Stories", "Untold Narratives",
    "Inspirational Stories", "Life Stories", "Millionaire Stories", "Secrets Revealed",
    "Fascinating Stories", "Hidden Truths", "Behind the Scenes", "Obscure Stories", "Mystery Channel",
    "Human Experiences", "Trump Stories", "Trump Story", "Barron Trump", "Barron Trump Stories",
    "Shocking Courtroom Battle", "Shocking Revelations", "Entertainment Industry Scandal",
    "Late-Night TV Controversy", "Shocking Legal Outcomes", "Media Accountability"
]

# Fetch Data Button
if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in keywords:
            st.write(f"🔍 Searching for: **{keyword}**")

            # YouTube Search API Request
            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }
            search_response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)

            if search_response.status_code != 200:
                st.warning(f"⚠️ Failed to fetch results for {keyword}. API Error: {search_response.json()}")
                continue

            search_data = search_response.json()
            if "items" not in search_data or not search_data["items"]:
                st.warning(f"❌ No videos found for: {keyword}")
                continue

            # Extract Video & Channel IDs
            video_ids = [video["id"].get("videoId", "") for video in search_data["items"] if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"].get("channelId", "") for video in search_data["items"] if "snippet" in video and "channelId" in video["snippet"]]

            if not video_ids or not channel_ids:
                st.warning(f"⚠️ No valid video/channel data for: {keyword}")
                continue

            # YouTube Video Statistics API Request
            stats_params = {"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
            stats_response = requests.get(YOUTUBE_VIDEO_URL, params=stats_params)
            stats_data = stats_response.json()

            if "items" not in stats_data or not stats_data["items"]:
                st.warning(f"⚠️ Failed to fetch video statistics for {keyword}")
                continue

            # YouTube Channel Statistics API Request
            channel_params = {"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params=channel_params)
            channel_data = channel_response.json()

            if "items" not in channel_data or not channel_data["items"]:
                st.warning(f"⚠️ Failed to fetch channel statistics for {keyword}")
                continue

            # Process Results
            for video, stat, channel in zip(search_data["items"], stats_data["items"], channel_data["items"]):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "No description available.")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                if subs < 53000:  # Filter small channels
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })

        # Display Results
        if all_results:
            st.success(f"✅ Found {len(all_results)} trending videos!")
            for result in all_results:
                st.markdown(
                    f"**🎥 Title:** {result['Title']}  \n"
                    f"📜 **Description:** {result['Description']}  \n"
                    f"🔗 **URL:** [Watch Video]({result['URL']})  \n"
                    f"👀 **Views:** {result['Views']}  \n"
                    f"👤 **Subscribers:** {result['Subscribers']}"
                )
                st.write("---")
        else:
            st.warning("⚠️ No trending videos found for small channels.")

    except Exception as e:
        st.error(f"🚨 Error: {e}")
