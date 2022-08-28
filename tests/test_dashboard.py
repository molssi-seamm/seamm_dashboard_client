#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `seamm_dashboard_client` package."""

import re

import pytest  # noqa: F401
import responses
from responses import matchers
from seamm_dashboard_client import Dashboard
import seamm_dashboard_client

url = "http://localhost:55066"  # Real server for getting response data
test_url = "http://test"  # Mock server


def test_construction():
    """Just create an object and test its type."""
    result = Dashboard("dev", url)
    assert str(type(result)) == "<class 'seamm_dashboard_client.dashboard.Dashboard'>"


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
            "http://test/api/projects/list",
            json=["default", "packmol", "recipes"],
            status=200,
        )

    result = d.list_projects()
    assert result == ["default", "packmol", "recipes"]


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
