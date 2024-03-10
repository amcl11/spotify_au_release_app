python add_ga.py

mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"new.music.playlist.tracker@gmail.com\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS=false\n\
port = $PORT\n\
[theme]\n\
backgroundColor=\"#0E1117\"\n\
primaryColor=\"#1db954\"\n\
textColor=\"#FAFAFA\"\n\
secondaryBackgroundColor=\"#262730\"\n\
font=\"sans serif\"\n\
" > ~/.streamlit/config.toml