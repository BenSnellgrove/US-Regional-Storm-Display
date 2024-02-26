import time

# Establish network connection
exec(open('network.py').read(), globals())
# Wait for connection
time.sleep(10)

# Main script
exec(open('gov_api_reader.py').read(), globals())
