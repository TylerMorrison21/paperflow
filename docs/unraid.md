# Unraid Deployment

PaperFlow can run on Unraid as a single container because the FastAPI backend also serves the local Web UI.

## Recommended Scope

The stock image is meant for:

- `PyMuPDF Local` as the free local parser
- `Marker API (Datalab.to)` if you want higher-quality cloud parsing with your own API key

The following remain advanced and are not bundled in the stock image:

- `PaddleOCR-VL-0.9B`
- `Enterprise Marker Self-Hosted`

Those need extra native or model dependencies and are better handled with a custom image.

## Easiest Path: Unraid Template

This repo now includes an Unraid Community Apps template at `unraid/paperflow.xml`.

Use these values in Unraid:

- Repository: `ghcr.io/tylermorrison21/paperflow:latest`
- WebUI: `http://[IP]:[PORT:8000]/`
- Container Port: `8000`
- AppData path: map `/data` to `/mnt/user/appdata/paperflow`
- `DATA_DIR=/data/jobs`

If you want Marker API available by default, also set:

- `DATALAB_API_KEY=your_datalab_api_key`

Then open:

```text
http://UNRAID-IP:8000/
```

## Compose Manager Path

If you prefer Unraid Compose Manager, use:

```yaml
services:
  paperflow:
    image: ghcr.io/tylermorrison21/paperflow:latest
    container_name: paperflow
    ports:
      - "8000:8000"
    environment:
      DATA_DIR: /data/jobs
      CORS_ORIGINS: "*"
      DATALAB_API_KEY: ""
    volumes:
      - /mnt/user/appdata/paperflow:/data
    restart: unless-stopped
```

## Notes

- Persistent job output, batch state, and usage tracking live under `/data/jobs`
- The built-in UI and API are on the same port
- If you want PaddleOCR-VL or self-hosted Marker inside Unraid, start from the included `Dockerfile` and build a custom image with those dependencies added
