# Andrew's Merge Sort Lab — Streamlit

## Run locally
From this folder:

```
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

Open the local URL printed by Streamlit.

## Publish a shareable Streamlit link
1. Upload this folder's files to a GitHub repository you own, retaining the filenames.
2. Sign in at https://share.streamlit.io and select Create app.
3. Select your repository, branch, and `streamlit_app.py` as the entrypoint.
4. Request `andrewsmergesortlab` in the App URL field, if available.
5. Deploy. Share the actual URL returned after successful deployment.

The desired URL is https://andrewsmergesortlab.streamlit.app — it is not reserved or live merely because it is written here.
Official guide: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Implementation
`algorithm.py` implements stable recursive Merge Sort and captures independent event snapshots. `streamlit_app.py` displays them using native Streamlit widgets, per-session state, a recursion tree, and timed fragment playback. Users can load custom inputs, generate random arrays, seek, play/pause, and navigate backward/forward.

The algorithm runs in O(n log n) time and O(n) auxiliary space plus recursion. Storing simulator history adds memory overhead. Inputs are limited to 16 integers for readable visualizations.
