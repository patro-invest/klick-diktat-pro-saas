import requests

def upload_protocol_to_fonds_finanz(api_key: str, agency_id: str, json_data: dict) -> bool:
    try:
        res = requests.post("https://api.fondsfinanz.de/v1/dokumente/upload", json=json_data, headers={"Authorization": f"Bearer {api_key}", "X-Agency-ID": agency_id}, timeout=10)
        return res.status_code in [200, 201]
    except Exception:
        return False