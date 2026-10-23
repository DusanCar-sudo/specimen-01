#!/usr/bin/env python3
"""One-run OAuth loopback flow for the Dule Milo YouTube channel.
Consent opens in browser -> user picks DULE MILO account -> redirect hits
localhost:8765 -> code exchanged -> channel verified -> video description set.
"""
import json, sys, time, threading, webbrowser, urllib.parse, urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKEN_FILE = '/home/dusan/.aura/google_youtube_token.json'
CLIENT_FILE = '/home/dusan/Downloads/client_secret_722885211053-bhf60csvhahhj0d142gi204s6nds7ieu.apps.googleusercontent.com.json'
PORT = 8765
VIDEO_ID = 'Edm8SLmIy48'
REDIRECT = f'http://localhost:{PORT}'
SCOPES = ' '.join([
    'https://www.googleapis.com/auth/youtube.force-ssl',
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly',
])
DESCRIPTION = (
    "Archimedes - the verification layer. An 84-second explainer: every answer "
    "passes a verifier gate before it ships.\n\n"
    "0.6 ms reflex - gate inequality (threshold q* = 0.18) - pass 82% / reject 18% "
    "- every rejection returns to the ledger and loops back into the verifier.\n\n"
    "#AI #Verification"
)

client = json.load(open(CLIENT_FILE))['installed']
state = {'code': None, 'error': None}

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        state['code'] = (q.get('code') or [None])[0]
        state['error'] = (q.get('error') or [None])[0]
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        ok = bool(state['code'])
        self.wfile.write(b'<html><body style="font-family:sans-serif;background:#0b0e10;color:#f2ecdc;display:grid;place-items:center;height:100vh">'
                         + (b'<h1>Got it. You can close this tab.</h1>' if ok else b'<h1>Consent failed: ' + (state['error'] or b'?').encode() + b'</h1>')
                         + b'</body></html>')
        threading.Thread(target=self.server.shutdown, daemon=True).start()
    def log_message(self, *a): pass

srv = HTTPServer(('127.0.0.1', PORT), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()

auth = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode({
    'client_id': client['client_id'], 'redirect_uri': REDIRECT,
    'response_type': 'code', 'scope': SCOPES, 'access_type': 'offline',
    'prompt': 'consent', 'include_granted_scopes': 'true',
})
print('AUTH_URL:', auth, flush=True)
webbrowser.open(auth)
print(f'waiting for consent redirect on {REDIRECT} ...', flush=True)

deadline = time.time() + 600
while time.time() < deadline and not (state['code'] or state['error']):
    time.sleep(0.5)
if not state['code']:
    print('FAILED: no code received.', state['error'] or 'timeout', flush=True); sys.exit(1)

data = urllib.parse.urlencode({
    'code': state['code'], 'client_id': client['client_id'],
    'client_secret': client['client_secret'], 'redirect_uri': REDIRECT,
    'grant_type': 'authorization_code'}).encode()
try:
    tok = json.load(urllib.request.urlopen(urllib.request.Request(
        'https://oauth2.googleapis.com/token', data=data), timeout=30))
except Exception as e:
    print('TOKEN EXCHANGE ERR:', e, getattr(e, 'read', lambda: b'')().decode()[:400], flush=True); sys.exit(1)

import shutil; shutil.copy(TOKEN_FILE, TOKEN_FILE + '.bak-aidiaries')
tok.update({'client_id': client['client_id'], 'client_secret': client['client_secret'],
            'scope': SCOPES,
            'expiry': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(time.time() + tok.get('expires_in', 3600)))})
json.dump(tok, open(TOKEN_FILE, 'w'))
print('token saved', flush=True)

H_ = {'Authorization': 'Bearer ' + tok['access_token'], 'Content-Type': 'application/json'}
def api(url, body=None, method=None):
    req = urllib.request.Request(url, headers=H_,
                                 data=json.dumps(body).encode() if body else None,
                                 method=method or ('POST' if body else 'GET'))
    return json.load(urllib.request.urlopen(req, timeout=60))

ch = api('https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true')
names = [c['snippet']['title'] for c in ch.get('items', [])]
print('CHANNEL:', names, flush=True)
if not any('Dule Milo' in n for n in names):
    print('WRONG CHANNEL - aborting update', flush=True); sys.exit(2)

vid = api(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={VIDEO_ID}')['items'][0]
sn = vid['snippet']
print('BEFORE:', repr(sn.get('description'))[:120], flush=True)
sn['description'] = DESCRIPTION
try:
    api('https://www.googleapis.com/youtube/v3/videos?part=snippet', {'id': VIDEO_ID, 'snippet': sn}, 'PUT')
    after = api(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={VIDEO_ID}')['items'][0]['snippet']
    print('AFTER:', repr(after.get('description'))[:160], flush=True)
    print('DESCRIPTION SET OK', flush=True)
except Exception as e:
    print('UPDATE ERR:', e, getattr(e, 'read', lambda: b'')().decode()[:400], flush=True)
