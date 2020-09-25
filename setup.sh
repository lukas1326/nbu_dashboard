mkdir -p ~/.streamlit/
echo "\
[general]\n\
email = \"aprilium@live.com\"\n\
" > ~/.streamlit/crederntials.toml
echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = $PORT\n\
