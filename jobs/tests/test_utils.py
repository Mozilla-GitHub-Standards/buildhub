import pytest

from buildhub.utils import (
    build_record_id, is_release_metadata, is_release_filename,
    guess_mimetype, guess_channel, chunked, localize_nightly_url,
    record_from_url, merge_metadata
)


RECORDS = [
    # Firefox Nightly
    {
        "id": "firefox_nightly_2017-05-15-10-02-38_55-0a1_linux-x86_64_en-us",
        "source": {
            "product": "firefox",
        },
        "target": {
            "version": "55.0a1",
            "platform": "linux-x86_64",
            "locale": "en-US",
            "channel": "nightly"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/firefox/nightly/2017/05/"
            "2017-05-15-10-02-38-mozilla-central/firefox-55.0a1.en-US.linux-x86_64.tar.bz2",
            "mimetype": "application/x-bzip2"
        }
     },

    # Firefox Aurora
    {
        "id": "firefox_aurora_54-0a2_macosx_en-us",
        "source": {
            "product": "firefox",
        },
        "target": {
            "version": "54.0a2",
            "platform": "macosx",
            "locale": "en-US",
            "channel": "aurora"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/firefox/nightly/2017/04/"
            "2017-04-03-00-40-02-mozilla-aurora/firefox-54.0a2.en-US.mac.dmg",
            "mimetype": "application/x-apple-diskimage"
        }
    },

    # Firefox Beta
    {
        "id": "firefox_beta_52-0b6_linux-x86_64_en-us",
        "source": {
            "product": "firefox",
        },
        "target": {
            "version": "52.0b6",
            "platform": "linux-x86_64",
            "locale": "en-US",
            "channel": "beta"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/firefox/releases/52.0b6/linux-x86_64/en-US/"
            "firefox-52.0b6.tar.bz2",
            "mimetype": "application/x-bzip2"
        }
    },

    # Firefox Candidates
    {
        "id": "firefox_50-0rc1_linux-x86_64_fr",
        "source": {
            "product": "firefox",
        },
        "target": {
            "version": "50.0rc1",
            "platform": "linux-x86_64",
            "locale": "fr",
            "channel": "release"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/firefox/candidates/50.0-candidates/build1/"
            "linux-x86_64/fr/firefox-50.0.tar.bz2",
            "mimetype": "application/x-bzip2"
        }
    },

    # Firefox Release
    {
        "id": "firefox_52-0_linux-x86_64_fr",
        "source": {
            "product": "firefox",
        },
        "target": {
            "version": "52.0",
            "platform": "linux-x86_64",
            "locale": "fr",
            "channel": "release"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/firefox/releases/52.0/linux-x86_64/fr/"
            "firefox-52.0.tar.bz2",
            "mimetype": "application/x-bzip2"
        }
    },

    # Firefox ESR
    {
        "id": "firefox_52-0esr_linux-x86_64_en-us",
        "source": {
            "product": "firefox",
        },
        "target": {
            "version": "52.0esr",
            "platform": "linux-x86_64",
            "locale": "en-US",
            "channel": "release"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/firefox/releases/52.0esr/linux-x86_64/en-US/"
            "firefox-52.0esr.tar.bz2",
            "mimetype": "application/x-bzip2"
        }
    },

    # Firefox Win release
    {
        "id": "firefox_beta_16-0b6_win32_bs",
        "source": {
            "product": "firefox",
        },
        "target": {
            "version": "16.0b6",
            "platform": "win32",
            "locale": "bs",
            "channel": "beta"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/firefox/releases/16.0b6/win32/bs/"
            "Firefox Setup 16.0b6.exe",
            "mimetype": "application/msdos-windows"
        }
    },

    # Firefox MacOSX release
    {
        "id": "firefox_50-0-1_macosx_ko",
        "source": {
            "product": "firefox",
        },
        "target": {
            "version": "50.0.1",
            "platform": "macosx",
            "locale": "ko",
            "channel": "release"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/firefox/releases/50.0.1/mac/ko/"
            "Firefox 50.0.1.dmg",
            "mimetype": "application/x-apple-diskimage"
        }
    },

    # Thunderbird Windows Release
    {
        "id": "thunderbird_beta_11-0b2_win32_eu",
        "source": {
            "product": "thunderbird",
        },
        "target": {
            "version": "11.0b2",
            "platform": "win32",
            "locale": "eu",
            "channel": "beta"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/thunderbird/releases/11.0b2/win32/eu/"
            "Thunderbird Setup 11.0b2.exe",
            "mimetype": "application/msdos-windows"
        }
    },

    # Thunderbird Mac OS X Release
    {
        "id": "thunderbird_10-0-12esr_macosx_pt-br",
        "source": {
            "product": "thunderbird",
        },
        "target": {
            "version": "10.0.12esr",
            "platform": "macosx",
            "locale": "pt-BR",
            "channel": "release"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/thunderbird/releases/10.0.12esr/mac/pt-BR/"
            "Thunderbird 10.0.12esr.dmg",
            "mimetype": "application/x-apple-diskimage"
        }
    },

    # Thunderbird Release
    {
        "id": "thunderbird_17-0-8esr_linux-x86_64_gd",
        "source": {
            "product": "thunderbird",
        },
        "target": {
            "version": "17.0.8esr",
            "platform": "linux-x86_64",
            "locale": "gd",
            "channel": "release"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/thunderbird/releases/17.0.8esr/linux-x86_64/"
            "gd/thunderbird-17.0.8esr.tar.bz2",
            "mimetype": "application/x-bzip2"
        }
    },

    # Fennec
    {
        "id": "fennec_beta_39-0b5_android-api-9_sl",
        "source": {
            "product": "fennec",
        },
        "target": {
            "version": "39.0b5",
            "platform": "android-api-9",
            "locale": "sl",
            "channel": "beta"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/mobile/releases/39.0b5/android-api-9/sl/"
            "fennec-39.0b5.sl.android-arm.apk",
            "mimetype": "application/vnd.android.package-archive"
        }
    },

    # Localized Fennec
    {
        "id": "fennec_beta_42-0b2_android-api-9_fr",
        "source": {
            "product": "fennec",
        },
        "target": {
            "version": "42.0b2",
            "platform": "android-api-9",
            "locale": "fr",
            "channel": "beta"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/mobile/releases/42.0b2/android-api-9/fr/"
            "fennec-42.0b2.fr.android-arm.apk",
            "mimetype": "application/vnd.android.package-archive"
        }
    },


    # Fennec ARM
    {
        "id": "fennec_nightly_2017-05-30-10-01-27_55-0a1_android-api-15_multi",
        "source": {
            "product": "fennec",
        },
        "target": {
            "version": "55.0a1",
            "platform": "android-api-15",
            "locale": "multi",
            "channel": "nightly"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/mobile/nightly/2017/05/2017-05-30-10-01-27-"
            "mozilla-central-android-api-15/fennec-55.0a1.multi.android-arm.apk",
            "mimetype": "application/vnd.android.package-archive"
        }
    },
    {
        "id": "fennec_nightly-old-id_2017-05-30-10-01-27_55-0a1_android-api-15_multi",
        "source": {
            "product": "fennec",
        },
        "target": {
            "version": "55.0a1",
            "platform": "android-api-15",
            "locale": "multi",
            "channel": "nightly-old-id"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/mobile/nightly/2017/05/2017-05-30-10-01-27-"
            "mozilla-central-android-api-15-old-id/fennec-55.0a1.multi.android-arm.apk",
            "mimetype": "application/vnd.android.package-archive"
        }
    },

    # Fennec i386
    {
        "id": "fennec_nightly_2017-05-30-10-01-27_55-0a1_android-i386_multi",
        "source": {
            "product": "fennec",
        },
        "target": {
            "version": "55.0a1",
            "platform": "android-i386",
            "locale": "multi",
            "channel": "nightly"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/mobile/nightly/2017/05/2017-05-30-10-01-27-"
            "mozilla-central-android-x86/fennec-55.0a1.multi.android-i386.apk",
            "mimetype": "application/vnd.android.package-archive"
        }
    },
    {
        "id": "fennec_nightly-old-id_2017-05-30-10-01-27_55-0a1_android-i386_multi",
        "source": {
            "product": "fennec",
        },
        "target": {
            "version": "55.0a1",
            "platform": "android-i386",
            "locale": "multi",
            "channel": "nightly-old-id"
        },
        "download": {
            "url": "https://archive.mozilla.org/pub/mobile/nightly/2017/05/2017-05-30-10-01-27-"
            "mozilla-central-android-x86-old-id/fennec-55.0a1.multi.android-i386.apk",
            "mimetype": "application/vnd.android.package-archive"
        }
    },

]


# Build record_id from record
@pytest.mark.parametrize("record", RECORDS)
def test_build_record_id(record):
    record_id = build_record_id(record)
    assert record_id == record["id"]


RELEASE_METADATA_FILENAMES = [
    ("firefox", "52.0b7", "firefox-52.0b7.json"),
    ("fennec", "51.0b2", "fennec-51.0b2.en-US.android-i386.json"),
    ("devedition", "54.0b11", "firefox-54.0b11.json"),
]


@pytest.mark.parametrize("product,version,filename", RELEASE_METADATA_FILENAMES)
def test_is_release_metadata(product, version, filename):
    assert is_release_metadata(product, version, filename)


WRONG_RELEASE_METADATA_FILENAMES = [
    ("firefox", "52.0b7", "thunderbird-52.0b7.json"),
    ("fennec", "51.0b2", "fennec-52.0.en-US.android-i386.json"),
    ("fennec", "52.0", "fennec-52.0.en-US.android-i386.asc"),
]


@pytest.mark.parametrize("product,version,filename", WRONG_RELEASE_METADATA_FILENAMES)
def test_wrong_release_metadata(product, version, filename):
    assert not is_release_metadata(product, version, filename)


RELEASE_FILENAMES = [
    ("firefox", "firefox-53.0.tar.bz2"),
    ("firefox", "firefox-54.0a2.en-US.mac.dmg"),
    ("firefox", "firefox-52.0b6.tar.bz2"),
    ("firefox", "firefox-50.0.tar.bz2"),
    ("firefox", "firefox-52.0.tar.bz2"),
    ("firefox", "firefox-52.0esr.tar.bz2"),
    ("thunderbird", "thunderbird-17.0.8esr.tar.bz2"),
    ("fennec", "fennec-39.0b5.sl.android-arm.apk"),
    ("fennec", "fennec-42.0b2.fr.android-arm.apk"),
    ("thunderbird", "Thunderbird 10.0.12esr.dmg"),
    ("thunderbird", "Thunderbird Setup 11.0b2.exe"),
    ("firefox", "Firefox Setup 17.0b3.exe"),
    ("firefox", "Firefox 50.0.1.dmg"),
    ("devedition", "Firefox Setup 54.0b11.exe"),
    ("devedition", "firefox-54.0b11.tar.bz2"),
]


@pytest.mark.parametrize("product,filename", RELEASE_FILENAMES)
def test_is_release_filename(product, filename):
    assert is_release_filename(product, filename)


WRONG_RELEASE_FILENAMES = [
    ("firefox", "firefox-1.5.0.5.tar.gz.asc"),
    ("firefox", "firefox-52.0.win32.sdk.zip"),
    ("fennec", "fennec-21.0b1.multi.android-arm-armv6.tests.zip"),
    ("fennec", "fennec-24.0b1.en-US.android-arm.crashreporter-symbols.zip"),
    ("firefox", "Firefox Setup Stub 49.0.exe"),
]


@pytest.mark.parametrize("product,filename", WRONG_RELEASE_FILENAMES)
def test_wrong_release_filename(product, filename):
    assert not is_release_filename(product, filename)


URLS_MIMETYPES = [
    ("firefox-55.0a1.en-US.linux-x86_64.tar.bz2", "application/x-bzip2"),
    ("fennec-42.0b2.fr.android-arm.apk", "application/vnd.android.package-archive"),
    ("firefox-52.0.win32.sdk.zip", "application/zip"),
    ("firefox-54.0a2.en-US.mac.dmg", "application/x-apple-diskimage"),
    ("firefox-1.5.0.5.tar.gz", "application/x-gzip"),
    ("firefox-1.5.0.5.tar.gz.asc", None)
]


@pytest.mark.parametrize("url,expected_mimetype", URLS_MIMETYPES)
def test_guess_mimetype(url, expected_mimetype):
    mimetype = guess_mimetype(url)
    assert mimetype == expected_mimetype


@pytest.mark.parametrize("record", RECORDS)
def test_guess_channel(record):
    url = record["download"]["url"]
    version = record["target"]["version"]
    expected_channel = record["target"]["channel"]
    channel = guess_channel(url, version)
    assert channel == expected_channel


CHUNKS = [
    ([], 5, [[]]),
    ([1, 2, 3], 5, [[1, 2, 3]]),
    ([1, 2, 3, 4, 5], 2, [[1, 2], [3, 4], [5]]),
]


@pytest.mark.parametrize("iterable,size,chunks", CHUNKS)
def test_chunked(iterable, size, chunks):
    assert list(chunked(iterable, size)) == chunks


NIGHTLY_URLS = [
    # Mobile ARM not localized
    ("https://archive.mozilla.org/pub/mobile/nightly/2017/05/2017-05-30-10-01-27-"
     "mozilla-central-android-x86-old-id/fennec-55.0a1.multi.android-i386.apk",
     "https://archive.mozilla.org/pub/mobile/nightly/2017/05/2017-05-30-10-01-27-"
     "mozilla-central-android-x86-old-id/fennec-55.0a1.multi.android-i386.apk"),

    # Mobile ARM localized
    ("https://archive.mozilla.org/pub/mobile/nightly/2017/06/2017-06-01-10-02-05-"
     "mozilla-central-android-api-15-l10n/fennec-55.0a1.ar.android-arm.apk",
     "https://archive.mozilla.org/pub/mobile/nightly/2017/06/2017-06-01-10-02-05-"
     "mozilla-central-android-api-15/fennec-55.0a1.multi.android-arm.apk"),

    # Mobile i386 not localized
    ("https://archive.mozilla.org/pub/mobile/nightly/2017/05/2017-05-30-10-01-27-"
     "mozilla-central-android-x86/fennec-55.0a1.multi.android-i386.apk",
     "https://archive.mozilla.org/pub/mobile/nightly/2017/05/2017-05-30-10-01-27-"
     "mozilla-central-android-x86/fennec-55.0a1.multi.android-i386.apk"),

    # firefox Mac not localized
    ("https://archive.mozilla.org/pub/firefox/nightly/2017/05/2017-05-01-03-02-04-"
     "mozilla-central/firefox-55.0a1.en-US.mac.dmg",
     "https://archive.mozilla.org/pub/firefox/nightly/2017/05/2017-05-01-03-02-04-"
     "mozilla-central/firefox-55.0a1.en-US.mac.dmg"),

    # Firefox Mac localized
    ("https://archive.mozilla.org/pub/firefox/nightly/2017/05/2017-05-01-03-02-04-"
     "mozilla-central-l10n/firefox-55.0a1.ach.mac.dmg",
     "https://archive.mozilla.org/pub/firefox/nightly/2017/05/2017-05-01-03-02-04-"
     "mozilla-central/firefox-55.0a1.en-US.mac.dmg"),

    # Firefox linux not localized
    ("https://archive.mozilla.org/pub/firefox/nightly/2017/05/"
     "2017-05-15-10-02-38-mozilla-central/firefox-55.0a1.en-US.linux-x86_64.tar.bz2",
     "https://archive.mozilla.org/pub/firefox/nightly/2017/05/"
     "2017-05-15-10-02-38-mozilla-central/firefox-55.0a1.en-US.linux-x86_64.tar.bz2"),

    # Firefox linux localized
    ("https://archive.mozilla.org/pub/firefox/nightly/2017/05/2017-05-15-10-02-38-"
     "mozilla-central-l10n/firefox-55.0a1.ach.linux-x86_64.tar.bz2",
     "https://archive.mozilla.org/pub/firefox/nightly/2017/05/"
     "2017-05-15-10-02-38-mozilla-central/firefox-55.0a1.en-US.linux-x86_64.tar.bz2"
     )
]


@pytest.mark.parametrize("localized_url,american_url", NIGHTLY_URLS)
def test_localize_nightly_url(localized_url, american_url):
    assert localize_nightly_url(localized_url) == american_url


@pytest.mark.parametrize("record", RECORDS)
def test_record_from_url(record):
    url = record["download"]["url"]
    from_url = record_from_url(url)
    assert from_url == record


METADATA_RECORDS = [
    ({"source": {"product": "firefox"}}, None, {"source": {"product": "firefox"}}),
    ({
        "target": {"channel": "release"},
        "source": {"product": "firefox"}
     }, {
        "buildid": "201706121152",
        "moz_source_repo": "a",
        "moz_source_stamp": "b",
     }, {
        "target": {"channel": "release"},
        "source": {
            "product": "firefox",
            "revision": "b",
            "repository": "a",
            "tree": "a",
        },
        "build": {
            "date": "2017-06-12T11:05:02Z",
            "id": "201706121152"
        }
    }),
    ({
        "target": {"channel": "release"},
        "source": {"product": "firefox"}
     }, {
        "buildid": "201706121152",
        "moz_source_repo": "MOZ_SOURCE_REPO=https://hg.mozilla.org/central/beta",
        "moz_source_stamp": "b0925nfubg",
     }, {
        "target": {"channel": "release"},
        "source": {
            "product": "firefox",
            "revision": "b0925nfubg",
            "repository": "https://hg.mozilla.org/central/beta",
            "tree": "central/beta",
        },
        "build": {
            "date": "2017-06-12T11:05:02Z",
            "id": "201706121152"
        }
    }),
]


@pytest.mark.parametrize("record,metadata,expected", METADATA_RECORDS)
def test_merge_metadata(record, metadata, expected):
    result = merge_metadata(record, metadata)
    assert result == expected
