from agents.versions import previous_major_floor, version_gt, version_in_range


def test_previous_major_floor():
    assert previous_major_floor("22.1.7") == "21.0.0"


def test_version_range_is_exclusive_start():
    assert version_in_range("22.0.0", "21.0.0", "22.1.7")
    assert not version_in_range("21.0.0", "21.0.0", "22.1.7")


def test_stable_is_newer_than_prerelease():
    assert version_gt("22.0.0", "22.0.0-next.1")
