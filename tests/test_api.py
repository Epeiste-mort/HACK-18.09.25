import io
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_healthz():
    r = client.get('/api/healthz')
    assert r.status_code == 200
    j = r.json()
    assert j['status'] == 'ok'
    assert j['device'] in ('GPU', 'CPU')


def test_version():
    r = client.get('/api/version')
    assert r.status_code == 200
    assert 'version' in r.json()


