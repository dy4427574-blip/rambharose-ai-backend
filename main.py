
    keys = load_keys()

    if key not in keys:
        raise HTTPException(status_code=403, detail="Invalid key")

    data = keys[key]

    if not data["active"]:
        raise HTTPException(status_code=403, detail="Key disabled")

    if data["used"] >= data["limit"]:
        raise HTTPException(status_code=403, detail="Limit exceeded")

    if datetime.date.today() > datetime.date.fromisoformat(data["expiry"]):
        raise HTTPException(status_code=403, detail="Key expired")

    data["used"] += 1
    save_keys(keys)

    return {
        "prediction": {
            "
