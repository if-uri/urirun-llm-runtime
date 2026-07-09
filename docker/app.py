from flask import Flask, request, jsonify
import os
from urllib.parse import urlparse

app = Flask(__name__)


def interpret_uri(uri: str) -> dict:
    # very small heuristic interpreter for demo purposes
    p = urlparse(uri)
    scheme = p.scheme
    path = p.path
    if scheme == 'kvm':
        action = 'kvm-exec'
        via = 'rfb/portal'
    elif scheme == 'shell':
        action = 'shell-exec'
        via = 'shell'
    else:
        action = 'unknown'
        via = 'none'
    return {'action': action, 'via': via, 'scheme': scheme, 'path': path}


@app.route('/run', methods=['POST'])
def run_uri():
    data = request.get_json(force=True)
    uri = data.get('uri')
    payload = data.get('payload')
    if not uri:
        return jsonify({'ok': False, 'error': 'missing uri'}), 400
    info = interpret_uri(uri)
    # Demo behaviour: do not actually run anything; return simulated result
    result = {
        'ok': True,
        'uri': uri,
        'payload': payload or {},
        'action': info['action'],
        'via': info['via'],
    }
    return jsonify(result)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'ok': True, 'service': 'urirun-llm-runtime-mock'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8765'))
    app.run(host='0.0.0.0', port=port)
