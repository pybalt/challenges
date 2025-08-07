#!/bin/bash
set -e

./start_all.sh
./novnc_startup.sh

python http_server.py > /tmp/server_logs.txt 2>&1 &

if [ "${MODE}" = "tool_server" ]; then
    uvicorn computer_use_demo.tool_server:app --host 0.0.0.0 --port 8001 > /tmp/uvicorn.log 2>&1 &
else
    STREAMLIT_SERVER_PORT=8501 python -m streamlit run computer_use_demo/streamlit.py > /tmp/streamlit_stdout.log &
fi

echo "✨ Computer Use Demo is ready!"
echo "➡️  Open http://localhost:8080 in your browser to begin"

# Keep the container running
tail -f /dev/null
