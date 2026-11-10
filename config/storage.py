from collections.abc import Mapping
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured


LOCAL_MEDIA_STORAGE = {
    "BACKEND": "django.core.files.storage.FileSystemStorage",
}

R2_REQUIRED_ENVIRONMENT_VARIABLES = (
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
    "R2_BUCKET_NAME",
    "R2_ENDPOINT_URL",
    "R2_PUBLIC_HOSTNAME",
)


def _validate_r2_endpoint(endpoint_url: str) -> str:
    try:
        parsed = urlsplit(endpoint_url)
        port = parsed.port
    except ValueError as error:
        raise ImproperlyConfigured(
            "R2_ENDPOINT_URL must be a valid Cloudflare R2 HTTPS endpoint."
        ) from error

    hostname = parsed.hostname or ""
    if (
        parsed.scheme != "https"
        or not hostname.endswith(".r2.cloudflarestorage.com")
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
    ):
        raise ImproperlyConfigured(
            "R2_ENDPOINT_URL must be a valid Cloudflare R2 HTTPS endpoint."
        )

    return endpoint_url.rstrip("/")


def _validate_public_hostname(hostname: str) -> str:
    labels = hostname.split(".")
    if (
        "://" in hostname
        or any(character.isspace() for character in hostname)
        or any(character in hostname for character in "/?#:")
        or hostname.startswith(".")
        or hostname.endswith(".")
        or ".." in hostname
        or len(labels) < 2
        or any(
            len(label) > 63
            or label.startswith("-")
            or label.endswith("-")
            or not all(
                character.isalnum() or character == "-"
                for character in label
            )
            for label in labels
        )
    ):
        raise ImproperlyConfigured(
            "R2_PUBLIC_HOSTNAME must be a hostname without a scheme or path."
        )

    return hostname


def build_media_storage(
    *,
    use_r2: bool,
    environ: Mapping[str, str],
) -> dict[str, object]:
    if not use_r2:
        return LOCAL_MEDIA_STORAGE.copy()

    values = {
        name: environ.get(name, "").strip()
        for name in R2_REQUIRED_ENVIRONMENT_VARIABLES
    }
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise ImproperlyConfigured(
            "R2_ENABLED=true requires these environment variables: "
            + ", ".join(missing)
        )

    endpoint_url = _validate_r2_endpoint(values["R2_ENDPOINT_URL"])
    public_hostname = _validate_public_hostname(
        values["R2_PUBLIC_HOSTNAME"]
    )

    return {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": values["R2_ACCESS_KEY_ID"],
            "secret_key": values["R2_SECRET_ACCESS_KEY"],
            "bucket_name": values["R2_BUCKET_NAME"],
            "endpoint_url": endpoint_url,
            "region_name": "auto",
            "signature_version": "s3v4",
            "default_acl": None,
            "file_overwrite": False,
            "querystring_auth": False,
            "custom_domain": public_hostname,
            "url_protocol": "https:",
            "verify": True,
            "object_parameters": {
                "CacheControl": "public, max-age=31536000, immutable",
                "StorageClass": "STANDARD",
            },
        },
    }
