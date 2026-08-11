#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_dashboard_client` package."""

import json
import re
from unittest.mock import MagicMock, patch

import pytest  # noqa: F401
import responses
from responses import matchers
from seamm_dashboard_client import Dashboard
import seamm_dashboard_client

url = "http://localhost:55066"  # Real server for getting response data
test_url = "http://test"  # Mock server

# A throwaway self-signed cert (CN=test-fixture, 100-year expiry, openssl
# req -x509 -newkey rsa:2048 -nodes) -- only used so
# ssl.create_default_context(cafile=...) has a real, parseable PEM file to
# load; never validated against a real connection in these unit tests
# (that's covered by real, live validation against MolSSI10 instead, not
# something to duplicate here with a new cryptography/openssl test
# dependency).
_TEST_CERT_PEM = """\
-----BEGIN CERTIFICATE-----
MIIDETCCAfmgAwIBAgIUL7gptcCZJFWN1Cm9llovTBtmT70wDQYJKoZIhvcNAQEL
BQAwFzEVMBMGA1UEAwwMdGVzdC1maXh0dXJlMCAXDTI2MDgxMTE1MjYwOVoYDzIx
MjYwNzE4MTUyNjA5WjAXMRUwEwYDVQQDDAx0ZXN0LWZpeHR1cmUwggEiMA0GCSqG
SIb3DQEBAQUAA4IBDwAwggEKAoIBAQCayfnqE3Va2n1lxSCG19yMOeYnvFxqJyOp
0qk07qy+kDEeBKINjfQ1dhpGyzT7r0Tq+WPbv2qcKo2rDJn04PDKzeHDkZhEO3Is
VAiMEEKUWVIMYdlxxL3IaQSdykJypzbSaLfa/OcnoeFGMmIWL74pY+A69vuiiXja
EuZIDcRCmoM98Cs1TzaChYx053DFyYQzM1un8Mv0i8zxNgNlLjZ1KuX+Cv3iD/Cs
ViED1sE9iUCcdfu0pLntPxZaSxhlW54B+EPAzzMKAJ9o4XMP7YpvQZW0evKXMVP6
KQOx0KngNrO5zpZ2Pjb45YyQaqaWYjYaaHYcN0LtZ4+B0a99gxrDAgMBAAGjUzBR
MB0GA1UdDgQWBBQJSVjXIHayo1NQAjetvyDhqjwR8zAfBgNVHSMEGDAWgBQJSVjX
IHayo1NQAjetvyDhqjwR8zAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUA
A4IBAQBkPGn5WfYwRLZ3J1aDlS/JdO/01igxYQaBXUoLAgo/9+06RtsjinEG64HP
/NiCop+/lijUI7hDK/ug9GlqCNPHca+z0uupra38sxPyANYAW+7DWpHRqEcg2eUy
6CPZWVnFbH8+/CKk/b4mHaScQfHNqGSQsExwkqyS0InEi7ZZ249+TOP9hERwEawG
aNU4NuvGKwW3RVW/Nf41WSLVCtpiq3vUm/Z06D41DGZjeQoarcJEQ7C6FI+p0HON
fZxkavpjgL+dBQhl5Jr/iCw8gsLUqBVcoGn9u7U9+MZv2Kqx0j+59VvchL3Aqn9a
oEqW7KJUcsOeuLuO4j/S02oATzU4
-----END CERTIFICATE-----
"""


@pytest.fixture
def cert_path(tmp_path):
    path = tmp_path / "webui.crt"
    path.write_text(_TEST_CERT_PEM)
    return str(path)


def test_construction():
    """Just create an object and test its type."""
    result = Dashboard("dev", url)
    assert str(type(result)) == "<class 'seamm_dashboard_client.dashboard.Dashboard'>"


@responses.activate
def test_login_blank_credentials_skips_token_post():
    # seamm/tk_job_handler.py's credential dialog returns "" (not None)
    # for a field left blank on OK -- must be treated as "no login
    # needed" (e.g. against a seamm_webui --auth none instance), not
    # POSTed as real (and rejected) credentials.
    d = Dashboard("test", test_url, username="", password="")

    session, csrf_token = d.login()

    assert csrf_token is None
    assert len(responses.calls) == 0  # never POSTed to /api/auth/token at all


@responses.activate
def test_jobs():
    "Test listing the projects."

    # Set true to use the real server 'url' defined above
    if False:
        d = Dashboard("test", url, username="psaxe", password="default")
        d._dump = True

        responses.add_passthru(re.compile(url + "/\\w+"))
    else:
        d = Dashboard("test", test_url)

        params = {
            "limit": "3",
            "sort_by": "id",
            "order": "asc",
        }
        responses.add(
            responses.GET,
            "http://test/api/jobs",
            match=[matchers.query_param_matcher(params)],
            json=[
                {
                    "description": "test of api",
                    "finished": "2022-02-24 10:06",
                    "flowchart_id": "1",
                    "group": None,
                    "group_id": None,
                    "id": 18,
                    "last_update": "2022-02-24 10:05",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "parameters": {
                        "cmdline": ["job:data/Users_psaxe_SEAMM_data_TiO2--anatase.cif"]
                    },
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/default/Job_000018",
                    "projects": [{"id": 1, "name": "default"}],
                    "started": "2022-02-24 10:06",
                    "status": "finished",
                    "submitted": "2022-02-24 10:05",
                    "title": "test of api",
                },
                {
                    "description": "Testing band structure of anatase.",
                    "finished": "2022-02-24 15:39",
                    "flowchart_id": "2",
                    "group": None,
                    "group_id": None,
                    "id": 19,
                    "last_update": "2022-02-24 15:38",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "parameters": {
                        "cmdline": ["job:data/Users_psaxe_SEAMM_data_TiO2--anatase.cif"]
                    },
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/default/Job_000019",
                    "projects": [{"id": 1, "name": "default"}],
                    "started": "2022-02-24 15:38",
                    "status": "finished",
                    "submitted": "2022-02-24 15:38",
                    "title": "Testing band structure of anatase.",
                },
                {
                    "description": "Testing band structure of anatase.",
                    "finished": "2022-02-24 15:39",
                    "flowchart_id": "3",
                    "group": None,
                    "group_id": None,
                    "id": 20,
                    "last_update": "2022-02-24 15:39",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "parameters": {
                        "cmdline": ["job:data/Users_psaxe_SEAMM_data_TiO2--anatase.cif"]
                    },
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/default/Job_000020",
                    "projects": [{"id": 1, "name": "default"}],
                    "started": "2022-02-24 15:39",
                    "status": "finished",
                    "submitted": "2022-02-24 15:39",
                    "title": "Testing band structure of anatase.",
                },
            ],
            status=200,
        )

    answer = """\
{
    "description": "test of api",
    "finished": "2022-02-24 10:06",
    "flowchart_id": "1",
    "group": null,
    "group_id": null,
    "id": 18,
    "last_update": "2022-02-24 10:05",
    "owner": "psaxe",
    "owner_id": 2,
    "parameters": {
        "cmdline": [
            "job:data/Users_psaxe_SEAMM_data_TiO2--anatase.cif"
        ]
    },
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/default/Job_000018",
    "projects": [
        {
            "id": 1,
            "name": "default"
        }
    ],
    "started": "2022-02-24 10:06",
    "status": "finished",
    "submitted": "2022-02-24 10:05",
    "title": "test of api"
}
{
    "description": "Testing band structure of anatase.",
    "finished": "2022-02-24 15:39",
    "flowchart_id": "2",
    "group": null,
    "group_id": null,
    "id": 19,
    "last_update": "2022-02-24 15:38",
    "owner": "psaxe",
    "owner_id": 2,
    "parameters": {
        "cmdline": [
            "job:data/Users_psaxe_SEAMM_data_TiO2--anatase.cif"
        ]
    },
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/default/Job_000019",
    "projects": [
        {
            "id": 1,
            "name": "default"
        }
    ],
    "started": "2022-02-24 15:38",
    "status": "finished",
    "submitted": "2022-02-24 15:38",
    "title": "Testing band structure of anatase."
}
{
    "description": "Testing band structure of anatase.",
    "finished": "2022-02-24 15:39",
    "flowchart_id": "3",
    "group": null,
    "group_id": null,
    "id": 20,
    "last_update": "2022-02-24 15:39",
    "owner": "psaxe",
    "owner_id": 2,
    "parameters": {
        "cmdline": [
            "job:data/Users_psaxe_SEAMM_data_TiO2--anatase.cif"
        ]
    },
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/default/Job_000020",
    "projects": [
        {
            "id": 1,
            "name": "default"
        }
    ],
    "started": "2022-02-24 15:39",
    "status": "finished",
    "submitted": "2022-02-24 15:39",
    "title": "Testing band structure of anatase."
}
"""

    result = ""
    for val in d.jobs(limit=3):
        result += str(val)
        result += "\n"

    if result != answer:
        print("---")
        print(result)
        print("---")
    assert result == answer


@responses.activate
def test_list_projects():
    "Test listing the projects."

    # Set true to use the real server 'url' defined above
    if False:
        d = Dashboard("test", url, username="psaxe", password="default")
        d._dump = True

        responses.add_passthru(re.compile(url + "/\\w+"))
    else:
        d = Dashboard("test", test_url)

        responses.add(
            responses.POST,
            "https://test/api/auth/token",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Encoding": "br",
                "Content-Length": "9",
                "Content-Type": "text/html; charset=utf-8",
                "Date": "Sat, 27 Aug 2022 19:43:14 GMT",
                "Server": "waitress",
                "Set-Cookie": "csrf_access_token=e8c8c5bd-d10d-4417-9eca-ea3a989",
                "Vary": "Accept-Encoding",
            },
            status=200,
        )

        responses.add(
            responses.GET,
            "http://test/api/projects",
            json=[
                {"id": 1, "name": "default", "path": "/x/default"},
                {"id": 2, "name": "packmol", "path": "/x/packmol"},
                {"id": 3, "name": "recipes", "path": "/x/recipes"},
            ],
            status=200,
        )

    result = d.list_projects()
    assert result == ["default", "packmol", "recipes"]


@responses.activate
def test_list_queues():
    "Test listing the queues (seamm_webui's GET /api/queues)."
    d = Dashboard("test", test_url)

    responses.add(
        responses.POST,
        "https://test/api/auth/token",
        status=200,
    )
    responses.add(
        responses.GET,
        "http://test/api/queues",
        json=[
            {
                "name": "local",
                "type": "local",
                "default": False,
                "limits": {},
            },
            {
                "name": "molssi10",
                "type": "slurm",
                "default": True,
                "limits": {
                    "ntasks": {
                        "choices": None,
                        "minimum": "1",
                        "maximum": "6",
                        "current": "1",
                    }
                },
            },
        ],
        status=200,
    )

    result = d.list_queues()
    assert [q["name"] for q in result] == ["local", "molssi10"]
    assert result[1]["default"] is True
    assert result[1]["limits"]["ntasks"]["maximum"] == "6"


@responses.activate
def test_list_queues_not_supported_returns_empty_list():
    "An old seamm_dashboard has no GET /api/queues at all -- treat as none."
    d = Dashboard("test", test_url)

    responses.add(
        responses.POST,
        "https://test/api/auth/token",
        status=200,
    )
    responses.add(
        responses.GET,
        "http://test/api/queues",
        status=404,
    )

    assert d.list_queues() == []


class _FakeStep:
    step_type = "some-step"
    data_files = []


class _FakeFlowchart:
    """Duck-types just what Dashboard.submit() actually touches -- no
    Parameter steps and no data files, so no file-transfer requests are
    made, keeping this a pure unit test of the parameters payload."""

    def get_nodes(self):
        return [_FakeStep()]

    def to_text(self):
        return "flowchart text"


@responses.activate
def test_submit_includes_queue_and_slurm_overrides():
    d = Dashboard("test", test_url)

    responses.add(
        responses.POST,
        "https://test/api/auth/token",
        status=200,
    )
    responses.add(
        responses.GET,
        "http://test/api/status",
        json={"status": "running"},
        status=200,
    )
    responses.add(
        responses.POST,
        "http://test/api/jobs",
        json={"id": 42},
        status=201,
    )

    d.submit(
        _FakeFlowchart(),
        title="a job",
        queue="molssi10",
        slurm_overrides={"ntasks": 4},
    )

    post = [c for c in responses.calls if c.request.url == "http://test/api/jobs"][0]
    body = json.loads(post.request.body)
    assert body["parameters"]["queue"] == "molssi10"
    assert body["parameters"]["slurm"] == {"ntasks": 4}


@responses.activate
def test_submit_omits_queue_and_slurm_when_not_given():
    d = Dashboard("test", test_url)

    responses.add(
        responses.POST,
        "https://test/api/auth/token",
        status=200,
    )
    responses.add(
        responses.GET,
        "http://test/api/status",
        json={"status": "running"},
        status=200,
    )
    responses.add(
        responses.POST,
        "http://test/api/jobs",
        json={"id": 43},
        status=201,
    )

    d.submit(_FakeFlowchart(), title="a job")

    post = [c for c in responses.calls if c.request.url == "http://test/api/jobs"][0]
    body = json.loads(post.request.body)
    assert "queue" not in body["parameters"]
    assert "slurm" not in body["parameters"]


@responses.activate
def test_projects():
    "Get the list of Project objects."

    # Set true to use the real server 'url' defined above
    if False:
        d = Dashboard("test", url, username="psaxe", password="default")
        d._dump = True

        responses.add_passthru(re.compile(url + "/\\w+"))
    else:
        d = Dashboard("test", test_url)

        responses.add(
            responses.POST,
            "https://test/api/auth/token",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Content-Encoding": "br",
                "Content-Length": "9",
                "Content-Type": "text/html; charset=utf-8",
                "Date": "Sat, 27 Aug 2022 19:43:14 GMT",
                "Server": "waitress",
                "Set-Cookie": "csrf_access_token=e8c8c5bd-d10d-4417-9eca-ea3a989",
                "Vary": "Accept-Encoding",
            },
            status=200,
        )

        responses.add(
            responses.GET,
            "http://test/api/projects",
            json=[
                {
                    "description": None,
                    "flowcharts": [
                        21,
                        22,
                        23,
                        24,
                        25,
                        26,
                        27,
                        28,
                        29,
                        30,
                        31,
                        32,
                        33,
                        34,
                        35,
                        36,
                        37,
                        38,
                        39,
                        40,
                    ],
                    "group": "staff",
                    "group_id": 2,
                    "id": 1,
                    "jobs": [
                        18,
                        19,
                        20,
                        21,
                        22,
                        25,
                        26,
                        41,
                        43,
                        27,
                        44,
                        47,
                        48,
                        52,
                        53,
                        55,
                        56,
                        57,
                        58,
                        67,
                        68,
                    ],
                    "name": "default",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "path": None,
                    "special_groups": [],
                    "special_users": [],
                },
                {
                    "description": "",
                    "flowcharts": [],
                    "group": "staff",
                    "group_id": 2,
                    "id": 2,
                    "jobs": [28, 30, 31, 34, 35, 36, 37, 38, 39, 40],
                    "name": "packmol",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol",
                    "special_groups": [],
                    "special_users": [],
                },
                {
                    "description": "",
                    "flowcharts": [],
                    "group": "staff",
                    "group_id": 2,
                    "id": 3,
                    "jobs": [],
                    "name": "recipes",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/recipes",
                    "special_groups": [],
                    "special_users": [],
                },
            ],
            status=200,
        )

    answer = """\
default
{
    "description": null,
    "flowcharts": [
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
        32,
        33,
        34,
        35,
        36,
        37,
        38,
        39,
        40
    ],
    "group": "staff",
    "group_id": 2,
    "id": 1,
    "jobs": [
        18,
        19,
        20,
        21,
        22,
        25,
        26,
        41,
        43,
        27,
        44,
        47,
        48,
        52,
        53,
        55,
        56,
        57,
        58,
        67,
        68
    ],
    "name": "default",
    "owner": "psaxe",
    "owner_id": 2,
    "path": null,
    "special_groups": [],
    "special_users": []
}
packmol
{
    "description": "",
    "flowcharts": [],
    "group": "staff",
    "group_id": 2,
    "id": 2,
    "jobs": [
        28,
        30,
        31,
        34,
        35,
        36,
        37,
        38,
        39,
        40
    ],
    "name": "packmol",
    "owner": "psaxe",
    "owner_id": 2,
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol",
    "special_groups": [],
    "special_users": []
}
recipes
{
    "description": "",
    "flowcharts": [],
    "group": "staff",
    "group_id": 2,
    "id": 3,
    "jobs": [],
    "name": "recipes",
    "owner": "psaxe",
    "owner_id": 2,
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/recipes",
    "special_groups": [],
    "special_users": []
}
"""
    result = ""
    for name, val in d.projects().items():
        result += name
        result += "\n"
        result += str(val)
        result += "\n"

    if result != answer:
        print("---")
        print(result)
        print("---")
    assert result == answer


@responses.activate
def test_project_jobs():
    "Test listing the projects."

    # Set true to use the real server 'url' defined above
    if False:
        d = Dashboard("test", url, username="psaxe", password="default")
        d._dump = True

        responses.add_passthru(re.compile(url + "/\\w+"))
    else:
        d = Dashboard("test", test_url)

        responses.add(
            responses.GET,
            "http://test/api/projects/2/jobs",
            json=[
                {
                    "description": "A test of the PACKMOL step.\n\nCreates a cubic periodic cell with benzene as the solute and 100 water molecules as solvent.",  # noqa: E501
                    "finished": "2022-05-21 16:34",
                    "flowchart_id": "7",
                    "group": None,
                    "group_id": None,
                    "id": 28,
                    "last_update": "2022-05-21 16:34",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "parameters": {"cmdline": []},
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000028",
                    "projects": [{"id": 2, "name": "packmol"}],
                    "started": "2022-05-21 16:34",
                    "status": "finished",
                    "submitted": "2022-05-21 16:34",
                    "title": "PACKMOL test: periodic cubic solute/solvent",
                },
                {
                    "description": "A test of the PACKMOL step.\n\nCreates a cubic region with benzene as the solute and 100 water molecules as solvent.",  # noqa: E501
                    "finished": "2022-05-21 16:36",
                    "flowchart_id": "8",
                    "group": None,
                    "group_id": None,
                    "id": 30,
                    "last_update": "2022-05-21 16:36",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "parameters": {"cmdline": []},
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000030",
                    "projects": [{"id": 2, "name": "packmol"}],
                    "started": "2022-05-21 16:36",
                    "status": "finished",
                    "submitted": "2022-05-21 16:36",
                    "title": "PACKMOL test: cubic region with solute/solvent",
                },
                {
                    "description": "A test of the PACKMOL step.\n\nCreates a spherical region with benzene as the solute and 100 water molecules as solvent.",  # noqa: E501
                    "finished": "2022-05-21 16:37",
                    "flowchart_id": "9",
                    "group": None,
                    "group_id": None,
                    "id": 31,
                    "last_update": "2022-05-21 16:36",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "parameters": {"cmdline": []},
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000031",
                    "projects": [{"id": 2, "name": "packmol"}],
                    "started": "2022-05-21 16:37",
                    "status": "finished",
                    "submitted": "2022-05-21 16:36",
                    "title": "PACKMOL test: spherical region with solute/solvent",
                },
                {
                    "description": "A test of the PACKMOL step.\n\nCreates a spherical region with benzene as the solute and 500 water molecules as solvent.",  # noqa: E501
                    "finished": "2022-05-21 16:44",
                    "flowchart_id": "11",
                    "group": None,
                    "group_id": None,
                    "id": 34,
                    "last_update": "2022-05-21 16:43",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "parameters": {"cmdline": []},
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000034",
                    "projects": [{"id": 2, "name": "packmol"}],
                    "started": "2022-05-21 16:43",
                    "status": "finished",
                    "submitted": "2022-05-21 16:43",
                    "title": "PACKMOL test: spherical region with solute/solvent",
                },
                {
                    "description": "A test of the PACKMOL step.\n\nCreates a spherical region 500 molecules of  1:1 mixture of H2O and H2S",  # noqa: E501
                    "finished": "2022-05-21 16:48",
                    "flowchart_id": "12",
                    "group": None,
                    "group_id": None,
                    "id": 35,
                    "last_update": "2022-05-21 16:47",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "parameters": {"cmdline": []},
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000035",
                    "projects": [{"id": 2, "name": "packmol"}],
                    "started": "2022-05-21 16:47",
                    "status": "finished",
                    "submitted": "2022-05-21 16:47",
                    "title": "PACKMOL test: spherical region with 1:1 H2O - H2S",
                },
                {
                    "description": "A test of the PACKMOL step.\n\nCreates a spherical region 500 molecules of a H2O - H2S mixture at 500 K and 100 atm using the ideal gas law.",  # noqa: E501
                    "finished": "2022-05-21 16:51",
                    "flowchart_id": "13",
                    "group": None,
                    "group_id": None,
                    "id": 36,
                    "last_update": "2022-05-21 16:50",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "parameters": {"cmdline": []},
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000036",
                    "projects": [{"id": 2, "name": "packmol"}],
                    "started": "2022-05-21 16:51",
                    "status": "finished",
                    "submitted": "2022-05-21 16:50",
                    "title": "PACKMOL test: spherical region with 1:1 H2O - H2S using the Ideal Gas Law",  # noqa: E501
                },
                {
                    "description": "A test of the PACKMOL step.\n\nCreates a spherical region with a diameter of 40 \u00c5 containing 500 molecules of a H2O - H2S mixture.",  # noqa: E501
                    "finished": "2022-05-21 16:54",
                    "flowchart_id": "14",
                    "group": None,
                    "group_id": None,
                    "id": 37,
                    "last_update": "2022-05-21 16:54",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "parameters": {"cmdline": []},
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000037",
                    "projects": [{"id": 2, "name": "packmol"}],
                    "started": "2022-05-21 16:54",
                    "status": "finished",
                    "submitted": "2022-05-21 16:54",
                    "title": "PACKMOL test: spherical region 40 \u00c5 diameter with 1:1 H2O - H2S",  # noqa: E501
                },
                {
                    "description": "Test for the PACKMOL step.\n\nbiphenyl::water 1::50\n\n10x20x30 \u00c5 region\n~1000 atoms",  # noqa: E501
                    "finished": "2022-05-24 17:40",
                    "flowchart_id": "15",
                    "group": None,
                    "group_id": None,
                    "id": 38,
                    "last_update": "2022-05-24 17:40",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "parameters": {"cmdline": []},
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000038",
                    "projects": [{"id": 2, "name": "packmol"}],
                    "started": "2022-05-24 17:40",
                    "status": "finished",
                    "submitted": "2022-05-24 17:40",
                    "title": "PACKMOL test flowchart 7: rectangular region w/ 1000 atoms",  # noqa: E501
                },
                {
                    "description": "Test for the PACKMOL step.\n\nbiphenyl with water solute\n\n10x20x30 \u00c5 region\n~1000 atoms",  # noqa: E501
                    "finished": "2022-05-24 17:44",
                    "flowchart_id": "16",
                    "group": None,
                    "group_id": None,
                    "id": 39,
                    "last_update": "2022-05-24 17:44",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "parameters": {"cmdline": []},
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000039",
                    "projects": [{"id": 2, "name": "packmol"}],
                    "started": "2022-05-24 17:44",
                    "status": "finished",
                    "submitted": "2022-05-24 17:44",
                    "title": "PACKMOL test flowchart 8: rectangular region w/ 1000 atoms, biphenyl solute",  # noqa: E501
                },
                {
                    "description": "Test for the PACKMOL step.\n\nbiphenyl with water solute\n\n10x20x30 \u00c5 periodic cell\n~1000 atoms",  # noqa: E501
                    "finished": "2022-05-24 17:48",
                    "flowchart_id": "17",
                    "group": None,
                    "group_id": None,
                    "id": 40,
                    "last_update": "2022-05-24 17:48",
                    "owner": "psaxe",
                    "owner_id": 2,
                    "parameters": {"cmdline": []},
                    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000040",
                    "projects": [{"id": 2, "name": "packmol"}],
                    "started": "2022-05-24 17:48",
                    "status": "finished",
                    "submitted": "2022-05-24 17:48",
                    "title": "PACKMOL test flowchart 9: rectangular cell w/ 1000 atoms, biphenyl solute",  # noqa: E501
                },
            ],
        )

    # Kludge! Create a Project object.
    project = seamm_dashboard_client.dashboard._Project(
        d,
        data={
            "description": "",
            "flowcharts": [],
            "group": "staff",
            "group_id": 2,
            "id": 2,
            "jobs": [28, 30, 31, 34, 35, 36, 37, 38, 39, 40],
            "name": "packmol",
            "owner": "psaxe",
            "owner_id": 2,
            "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol",
            "special_groups": [],
            "special_users": [],
        },
    )

    answer = """\
{
    "description": "A test of the PACKMOL step.\\n\\nCreates a cubic periodic cell with benzene as the solute and 100 water molecules as solvent.",
    "finished": "2022-05-21 16:34",
    "flowchart_id": "7",
    "group": null,
    "group_id": null,
    "id": 28,
    "last_update": "2022-05-21 16:34",
    "owner": "psaxe",
    "owner_id": 2,
    "parameters": {
        "cmdline": []
    },
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000028",
    "projects": [
        {
            "id": 2,
            "name": "packmol"
        }
    ],
    "started": "2022-05-21 16:34",
    "status": "finished",
    "submitted": "2022-05-21 16:34",
    "title": "PACKMOL test: periodic cubic solute/solvent"
}
{
    "description": "A test of the PACKMOL step.\\n\\nCreates a cubic region with benzene as the solute and 100 water molecules as solvent.",
    "finished": "2022-05-21 16:36",
    "flowchart_id": "8",
    "group": null,
    "group_id": null,
    "id": 30,
    "last_update": "2022-05-21 16:36",
    "owner": "psaxe",
    "owner_id": 2,
    "parameters": {
        "cmdline": []
    },
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000030",
    "projects": [
        {
            "id": 2,
            "name": "packmol"
        }
    ],
    "started": "2022-05-21 16:36",
    "status": "finished",
    "submitted": "2022-05-21 16:36",
    "title": "PACKMOL test: cubic region with solute/solvent"
}
{
    "description": "A test of the PACKMOL step.\\n\\nCreates a spherical region with benzene as the solute and 100 water molecules as solvent.",
    "finished": "2022-05-21 16:37",
    "flowchart_id": "9",
    "group": null,
    "group_id": null,
    "id": 31,
    "last_update": "2022-05-21 16:36",
    "owner": "psaxe",
    "owner_id": 2,
    "parameters": {
        "cmdline": []
    },
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000031",
    "projects": [
        {
            "id": 2,
            "name": "packmol"
        }
    ],
    "started": "2022-05-21 16:37",
    "status": "finished",
    "submitted": "2022-05-21 16:36",
    "title": "PACKMOL test: spherical region with solute/solvent"
}
{
    "description": "A test of the PACKMOL step.\\n\\nCreates a spherical region with benzene as the solute and 500 water molecules as solvent.",
    "finished": "2022-05-21 16:44",
    "flowchart_id": "11",
    "group": null,
    "group_id": null,
    "id": 34,
    "last_update": "2022-05-21 16:43",
    "owner": "psaxe",
    "owner_id": 2,
    "parameters": {
        "cmdline": []
    },
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000034",
    "projects": [
        {
            "id": 2,
            "name": "packmol"
        }
    ],
    "started": "2022-05-21 16:43",
    "status": "finished",
    "submitted": "2022-05-21 16:43",
    "title": "PACKMOL test: spherical region with solute/solvent"
}
{
    "description": "A test of the PACKMOL step.\\n\\nCreates a spherical region 500 molecules of  1:1 mixture of H2O and H2S",
    "finished": "2022-05-21 16:48",
    "flowchart_id": "12",
    "group": null,
    "group_id": null,
    "id": 35,
    "last_update": "2022-05-21 16:47",
    "owner": "psaxe",
    "owner_id": 2,
    "parameters": {
        "cmdline": []
    },
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000035",
    "projects": [
        {
            "id": 2,
            "name": "packmol"
        }
    ],
    "started": "2022-05-21 16:47",
    "status": "finished",
    "submitted": "2022-05-21 16:47",
    "title": "PACKMOL test: spherical region with 1:1 H2O - H2S"
}
{
    "description": "A test of the PACKMOL step.\\n\\nCreates a spherical region 500 molecules of a H2O - H2S mixture at 500 K and 100 atm using the ideal gas law.",
    "finished": "2022-05-21 16:51",
    "flowchart_id": "13",
    "group": null,
    "group_id": null,
    "id": 36,
    "last_update": "2022-05-21 16:50",
    "owner": "psaxe",
    "owner_id": 2,
    "parameters": {
        "cmdline": []
    },
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000036",
    "projects": [
        {
            "id": 2,
            "name": "packmol"
        }
    ],
    "started": "2022-05-21 16:51",
    "status": "finished",
    "submitted": "2022-05-21 16:50",
    "title": "PACKMOL test: spherical region with 1:1 H2O - H2S using the Ideal Gas Law"
}
{
    "description": "A test of the PACKMOL step.\\n\\nCreates a spherical region with a diameter of 40 Å containing 500 molecules of a H2O - H2S mixture.",
    "finished": "2022-05-21 16:54",
    "flowchart_id": "14",
    "group": null,
    "group_id": null,
    "id": 37,
    "last_update": "2022-05-21 16:54",
    "owner": "psaxe",
    "owner_id": 2,
    "parameters": {
        "cmdline": []
    },
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000037",
    "projects": [
        {
            "id": 2,
            "name": "packmol"
        }
    ],
    "started": "2022-05-21 16:54",
    "status": "finished",
    "submitted": "2022-05-21 16:54",
    "title": "PACKMOL test: spherical region 40 Å diameter with 1:1 H2O - H2S"
}
{
    "description": "Test for the PACKMOL step.\\n\\nbiphenyl::water 1::50\\n\\n10x20x30 Å region\\n~1000 atoms",
    "finished": "2022-05-24 17:40",
    "flowchart_id": "15",
    "group": null,
    "group_id": null,
    "id": 38,
    "last_update": "2022-05-24 17:40",
    "owner": "psaxe",
    "owner_id": 2,
    "parameters": {
        "cmdline": []
    },
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000038",
    "projects": [
        {
            "id": 2,
            "name": "packmol"
        }
    ],
    "started": "2022-05-24 17:40",
    "status": "finished",
    "submitted": "2022-05-24 17:40",
    "title": "PACKMOL test flowchart 7: rectangular region w/ 1000 atoms"
}
{
    "description": "Test for the PACKMOL step.\\n\\nbiphenyl with water solute\\n\\n10x20x30 Å region\\n~1000 atoms",
    "finished": "2022-05-24 17:44",
    "flowchart_id": "16",
    "group": null,
    "group_id": null,
    "id": 39,
    "last_update": "2022-05-24 17:44",
    "owner": "psaxe",
    "owner_id": 2,
    "parameters": {
        "cmdline": []
    },
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000039",
    "projects": [
        {
            "id": 2,
            "name": "packmol"
        }
    ],
    "started": "2022-05-24 17:44",
    "status": "finished",
    "submitted": "2022-05-24 17:44",
    "title": "PACKMOL test flowchart 8: rectangular region w/ 1000 atoms, biphenyl solute"
}
{
    "description": "Test for the PACKMOL step.\\n\\nbiphenyl with water solute\\n\\n10x20x30 Å periodic cell\\n~1000 atoms",
    "finished": "2022-05-24 17:48",
    "flowchart_id": "17",
    "group": null,
    "group_id": null,
    "id": 40,
    "last_update": "2022-05-24 17:48",
    "owner": "psaxe",
    "owner_id": 2,
    "parameters": {
        "cmdline": []
    },
    "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/packmol/Job_000040",
    "projects": [
        {
            "id": 2,
            "name": "packmol"
        }
    ],
    "started": "2022-05-24 17:48",
    "status": "finished",
    "submitted": "2022-05-24 17:48",
    "title": "PACKMOL test flowchart 9: rectangular cell w/ 1000 atoms, biphenyl solute"
}
"""  # noqa: E501

    result = ""
    for val in project.jobs():
        result += str(val)
        result += "\n"

    if result != answer:
        print("---")
        print(result)
        print("---")
    assert result == answer


@responses.activate
def test_login_without_csrf_cookie():
    """Not every dashboard uses a CSRF double-submit cookie -- seamm_webui
    deliberately doesn't (SameSite + CORS instead, see its auth.py). A
    successful login response with no CSRF cookie at all must still count
    as a successful login, just with no X-CSRF-TOKEN header to send
    afterward, not raise DashboardLoginError.
    """
    d = Dashboard("test", test_url, username="psaxe", password="secret")

    responses.add(
        responses.POST,
        "http://test/api/auth/token",
        json={"username": "psaxe"},
        status=200,
        # No Set-Cookie header at all -- unlike the old dashboard, which
        # always sets access/refresh + CSRF cookies together.
    )

    session, csrf_token = d.login()
    assert csrf_token is None
    assert session is not None


# --- TLS verification (verify=) -------------------------------------------
#
# Added for a real dashboard: seamm_webui generates a self-signed
# certificate for a non-loopback bind (its tls.py) -- requests' own default
# (verify=True against the system trust store) hard-rejects that with no
# way to override from dashboards.ini before this. `responses` mocks below
# the point where `verify` would matter, so these use unittest.mock
# directly on requests.Session.get/post to confirm the actual kwarg is
# threaded through, not just stored.


def _fake_response(status_code=200, json_data=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.cookies.get_dict.return_value = {}
    resp.json.return_value = json_data if json_data is not None else {}
    return resp


def test_verify_defaults_to_true():
    d = Dashboard("test", test_url)
    assert d.verify is True


def test_verify_stores_false():
    d = Dashboard("test", test_url, verify=False)
    assert d.verify is False


def test_verify_stores_cert_path():
    d = Dashboard("test", test_url, verify="/path/to/webui.crt")
    assert d.verify == "/path/to/webui.crt"


def test_login_passes_verify_to_session_post(cert_path):
    d = Dashboard("test", test_url, username="u", password="p", verify=cert_path)
    with patch("requests.Session.post", return_value=_fake_response()) as mock_post:
        d.login()

    assert mock_post.call_args.kwargs["verify"] == cert_path


def test_url_get_passes_verify_for_login_and_request(cert_path):
    """Both the internal login POST and the actual GET must carry verify --
    _url_get() logs in fresh on every call (see login())."""
    calls = []

    def fake_post(self, url, **kwargs):
        calls.append(("POST", url, kwargs.get("verify")))
        return _fake_response()

    def fake_get(self, url, **kwargs):
        calls.append(("GET", url, kwargs.get("verify")))
        return _fake_response()

    d = Dashboard("test", test_url, username="u", password="p", verify=cert_path)
    with patch("requests.Session.post", fake_post), patch(
        "requests.Session.get", fake_get
    ):
        d._url_get("/api/status")

    assert [v for (_, _, v) in calls] == [cert_path, cert_path]


def test_url_post_passes_verify_for_login_and_request(cert_path):
    calls = []

    def fake_post(self, url, **kwargs):
        calls.append((url, kwargs.get("verify")))
        # Login (POST /api/auth/token) must see 200 to be considered
        # successful; the actual request (POST /api/jobs here) is free to
        # return whatever status the real endpoint would.
        status_code = 200 if url.endswith("/api/auth/token") else 201
        return _fake_response(status_code=status_code, json_data={"id": 1})

    d = Dashboard("test", test_url, username="u", password="p", verify=cert_path)
    with patch("requests.Session.post", fake_post):
        d._url_post("/api/jobs", json_data={})

    # One POST for /api/auth/token (login), one for /api/jobs -- both
    # carrying the same verify value.
    assert len(calls) == 2
    assert all(v == cert_path for (_, v) in calls)


def test_verify_false_is_passed_through_unchanged():
    """verify=False (disable checking entirely) must survive intact, not
    be coerced to some other falsy-but-wrong value."""
    d = Dashboard("test", test_url, username="u", password="p", verify=False)
    with patch("requests.Session.post", return_value=_fake_response()) as mock_post:
        d.login()

    assert mock_post.call_args.kwargs["verify"] is False


# --- Certificate pinning (verify=<path>) ------------------------------------
#
# A path doesn't just get forwarded as requests' own verify=<path> -- that
# alone still enforces a hostname/SAN match, which a self-signed
# seamm_webui certificate can genuinely fail even though it's the right
# certificate (confirmed for real against MolSSI10: reachable only via a
# DNS alias -- molssi10.molssi.org -- distinct from the SANs tls.py put in
# the cert, molssi10/molssi10.chem.vt.edu/localhost). A path instead mounts
# _PinnedCertAdapter, which verifies the cert's signature against that
# exact file but skips the hostname check.


def test_login_mounts_pinned_adapter_for_cert_path(cert_path):
    from seamm_dashboard_client.dashboard import _PinnedCertAdapter

    d = Dashboard("test", test_url, username="u", password="p", verify=cert_path)
    with patch("requests.Session.post", return_value=_fake_response()):
        session, _ = d.login()

    adapter = session.get_adapter("https://molssi10.example.org")
    assert isinstance(adapter, _PinnedCertAdapter)
    assert adapter._certfile == cert_path


@pytest.mark.parametrize("verify", [True, False])
def test_login_does_not_mount_pinned_adapter_for_bool_verify(verify):
    from seamm_dashboard_client.dashboard import _PinnedCertAdapter

    d = Dashboard("test", test_url, username="u", password="p", verify=verify)
    with patch("requests.Session.post", return_value=_fake_response()):
        session, _ = d.login()

    adapter = session.get_adapter("https://molssi10.example.org")
    assert not isinstance(adapter, _PinnedCertAdapter)


def test_login_mounts_pinned_adapter_even_with_blank_credentials(cert_path):
    """The early "no credentials, no login POST needed" return in login()
    must not skip mounting the pinned adapter -- _url_get/_url_post reuse
    this same session for every subsequent request regardless of whether
    an actual login POST happened."""
    from seamm_dashboard_client.dashboard import _PinnedCertAdapter

    d = Dashboard("test", test_url, username="", password="", verify=cert_path)
    session, csrf = d.login()

    assert csrf is None  # confirms the early-return path was taken
    adapter = session.get_adapter("https://molssi10.example.org")
    assert isinstance(adapter, _PinnedCertAdapter)
