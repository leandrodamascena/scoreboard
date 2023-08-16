import sys
with open('/tmp/python-sys-path.txt', 'w') as outfile:
    outfile.write(str(sys.path))

from producer import app
from producer.data.players import MOCK_DATA

def test_ingest_players():
    app.ingest_players()
