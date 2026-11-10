from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase
from storages.backends.s3 import S3Storage

from config.storage import build_media_storage


R2_ENVIRONMENT = {
    "R2_ACCESS_KEY_ID": "test-access-key",
    "R2_SECRET_ACCESS_KEY": "test-secret-key",
    "R2_BUCKET_NAME": "portfolio-media",
    "R2_ENDPOINT_URL": (
        "https://account-id.eu.r2.cloudflarestorage.com"
    ),
    "R2_PUBLIC_HOSTNAME": "media.example.com",
}


class MediaStorageConfigurationTests(SimpleTestCase):
    def test_local_storage_is_the_default_without_r2(self):
        storage = build_media_storage(use_r2=False, environ={})

        self.assertEqual(
            storage,
            {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        )

    def test_r2_requires_every_configuration_value(self):
        environment = R2_ENVIRONMENT.copy()
        del environment["R2_SECRET_ACCESS_KEY"]

        with self.assertRaisesMessage(
            ImproperlyConfigured,
            "R2_SECRET_ACCESS_KEY",
        ) as context:
            build_media_storage(use_r2=True, environ=environment)

        self.assertNotIn("test-access-key", str(context.exception))

    def test_r2_storage_uses_public_standard_objects(self):
        storage = build_media_storage(
            use_r2=True,
            environ=R2_ENVIRONMENT,
        )
        options = storage["OPTIONS"]

        self.assertEqual(storage["BACKEND"], "storages.backends.s3.S3Storage")
        self.assertEqual(options["region_name"], "auto")
        self.assertEqual(options["signature_version"], "s3v4")
        self.assertIsNone(options["default_acl"])
        self.assertFalse(options["querystring_auth"])
        self.assertFalse(options["file_overwrite"])
        self.assertEqual(options["custom_domain"], "media.example.com")
        self.assertEqual(
            options["object_parameters"]["StorageClass"],
            "STANDARD",
        )

    def test_installed_backend_builds_public_url_without_network(self):
        configuration = build_media_storage(
            use_r2=True,
            environ=R2_ENVIRONMENT,
        )
        storage = S3Storage(**configuration["OPTIONS"])

        self.assertEqual(
            storage.url("projects/dashboard.webp"),
            "https://media.example.com/projects/dashboard.webp",
        )

    def test_r2_rejects_non_cloudflare_or_insecure_endpoints(self):
        invalid_endpoints = (
            "http://account-id.r2.cloudflarestorage.com",
            "https://storage.example.com",
            "https://account-id.r2.cloudflarestorage.com/path",
            "https://account-id.r2.cloudflarestorage.com?debug=true",
        )

        for endpoint_url in invalid_endpoints:
            with self.subTest(endpoint_url=endpoint_url):
                environment = R2_ENVIRONMENT | {
                    "R2_ENDPOINT_URL": endpoint_url,
                }
                with self.assertRaises(ImproperlyConfigured):
                    build_media_storage(use_r2=True, environ=environment)

    def test_r2_rejects_public_hostname_with_scheme_or_path(self):
        for hostname in (
            "https://media.example.com",
            "media.example.com/images",
            "media.example.com/",
        ):
            with self.subTest(hostname=hostname):
                environment = R2_ENVIRONMENT | {
                    "R2_PUBLIC_HOSTNAME": hostname,
                }
                with self.assertRaises(ImproperlyConfigured):
                    build_media_storage(use_r2=True, environ=environment)
