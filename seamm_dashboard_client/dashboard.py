#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A proxy for interacting with SEAMM Dashboards.

This package provides functions and classes for interacting with the REST api of SEAMM
dashboards.
"""

import collections.abc
import json
import logging
from pathlib import Path, PurePath
import platform
import shlex

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

logger = logging.getLogger(__name__)

# logger.setLevel("DEBUG")


def safe_filename(filename):
    if filename[0] == "~":
        path = Path(filename).expanduser()
    else:
        path = Path(filename)
    if path.anchor == "":
        result = "_".join(path.parts)
    else:
        result = "_".join(path.parts[1:])
    return "job:data/" + result


class DashboardConnectionError(Exception):
    def __init__(self, dashboard, *args):
        self.dashboard = dashboard
        super().__init__(dashboard, *args)


class DashboardLoginError(Exception):
    def __init__(self, dashboard, *args):
        self.dashboard = dashboard
        super().__init__(dashboard, *args)


class DashboardNotRunningError(Exception):
    def __init__(self, dashboard, *args):
        self.dashboard = dashboard
        super().__init__(dashboard, *args)


class DashboardSubmitError(Exception):
    def __init__(self, dashboard, *args):
        self.dashboard = dashboard
        super().__init__(dashboard, *args)


class DashboardTimeoutError(Exception):
    def __init__(self, dashboard, *args):
        self.dashboard = dashboard
        super().__init__(dashboard, *args)


class DashboardUnknownError(Exception):
    def __init__(self, dashboard, *args):
        self.dashboard = dashboard
        super().__init__(dashboard, *args)


class Dashboard(object):
    def __init__(
        self, name, url, username=None, password=None, user_agent=None, timeout=1
    ):
        """The interface to a Dashboard

        Parameters
        ----------
        """
        from seamm_dashboard_client import __version__

        self._name = name
        self._url = url

        self.username = username
        self.password = password
        self.timeout = timeout
        if user_agent is None:
            self.user_agent = (
                f"SEAMMDashboardClient/{__version__} ({platform.platform()})"
            )
        else:
            self.user_agent = (
                f"{user_agent} SEAMMDashboardClient/{__version__} "
                "({platform.platform()})"
            )
        self._dump = False

    @property
    def name(self):
        "The name of the dashboard."
        return self._name

    @property
    def url(self):
        "The base url of the dashboard"
        return self._url

    def job(self, job_id):
        """Return a single job given the id."""

        response = self._url_get(f"/api/jobs/{job_id}")

        if response.status_code != 200:
            logger.warning(
                "Encountered an error getting the job from dashboard "
                f"{self.name}, error code: {response.status_code}"
            )
            return {}

        return _Job(self, response.json())

    def jobs(self, title=None, description=None, limit=None, sort_by="id", order="asc"):
        """Return a list of Job objects."""
        data = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if limit is not None:
            data["limit"] = limit
        if sort_by is not None:
            data["sort_by"] = sort_by
        if order is not None:
            data["order"] = order

        response = self._url_get("/api/jobs", params=data)

        if response.status_code != 200:
            logger.warning(
                "Encountered an error getting the list of jobs from dashboard "
                f"{self.name}, error code: {response.status_code}"
            )
            return {}

        return [_Job(self, p) for p in response.json()]

    def add_project(self, project, description=""):
        """Add a project to the datastore for this dashboard.

        Parameters
        ----------
        project : str
            The name of the new project.
        description : str
            An optional description of the project.
        """
        data = {
            "name": project,
            "description": description,
        }

        response = self._url_post("/api/projects", json=data)

        if response.status_code != 201:
            raise DashboardUnknownError(
                self.url + "/api/projects",
                f"There was an error creating a project at {self.name}.\n"
                f"    code = {response.status_code}\n{response.json()}",
            )

    def list_projects(self):
        """Get a list of the projects."""
        response = self._url_get("/api/projects/list")

        if response.status_code != 200:
            logger.warning(
                "Encountered an error getting the project list from dashboard "
                f" '{self.name}', error code: {response.status_code}"
            )
            return []

        return response.json()

    def project(self, project_id):
        """Return a Project given the id.

        Parameters
        ----------
        project_id : int
            The id of the project.

        Returns
        -------
        _Project()
            A Project object.

        .. note::
          The Project data looks like this::

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

        response = self._url_get(f"/api/projects/{project_id}")

        if response.status_code != 200:
            logger.warning(
                f"Encountered an error getting the project {project_id} from dashboard "
                f" '{self.name}', error code: {response.status_code}"
            )
            return {}

        return _Project(self, response.json())

    def projects(self, name=None, description=None, limit=None):
        """Return a list of Project objects.

        Parameters
        ----------
        name : str
            If not None, select only projects whose name matches
        description : str
            If not None, select only projects whose description matches
        limit : int
            If not None, limit the number of projects to this value

        Returns
        -------
        [_Project]
            A list of Project object.

        .. note::
          The Project data looks like this::

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
        data = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if limit is not None:
            data["limit"] = limit

        response = self._url_get("/api/projects", params=data)

        if response.status_code != 200:
            logger.warning(
                "Encountered an error getting the project list from dashboard "
                f" '{self.name}', error code: {response.status_code}"
            )
            return {}

        return {p["name"]: _Project(self, p) for p in response.json()}

    def login(self):
        """Log the session into the dashboard.

        Parameters
        ----------
        dashboard : str
            The name of the dashboard.

        Returns
        -------
        requests.session, str
            session, and the CSRF token or None
        """
        url = self.url + "/api/auth/token"
        session = requests.session()

        if self.username is None or self.password is None:
            return session, None

        headers = {"User-Agent": self.user_agent}

        authentication = {
            "username": self.username,
            "password": self.password,
        }

        if self._dump:
            print(20 * "v")
            print("LOGIN")
            print()
            print("headers:")
            print(json.dumps(headers, indent=4))
            print()
            print("json:")
            print(json.dumps(authentication, indent=4))
            print()
            print(20 * "x")

        try:
            response = session.post(url, headers=headers, json=authentication)
        except requests.exceptions.ConnectionError as e:
            raise DashboardConnectionError(
                url, f"The dashboard '{self.name}' cannot be reached: {str(e)}"
            )
        except Exception as e:
            raise DashboardConnectionError(
                self.url,
                f"Unknown error with the dashboard '{self.name}': ({type(e)}) {str(e)}",
            )
        else:
            if response.status_code == 400:
                try:
                    result = response.json()["msg"]
                except Exception:
                    result = "unknown reason"

                raise DashboardLoginError(
                    url,
                    (
                        f"Could not log in to dashboard {self.name} as "
                        f"{self.username} / {self.password} ({result}). "
                        "Check ~/.seamm.d/seammrc for this information."
                    ),
                )  # lgtm [py/clear-text-logging-sensitive-data]
            elif response.status_code != 200:
                raise DashboardLoginError(
                    url,
                    f"The dashboard {self.name} returned an error: code = "
                    f"{response.status_code}",
                )
            else:
                cookie_jar = response.cookies
                cookies = cookie_jar.get_dict()
                if "csrf_access_token" in cookies:
                    csrf_token = cookies["csrf_access_token"]
                else:
                    raise DashboardLoginError(
                        url,
                        f"Could not log in to dashboard {self.name} -- did not get "
                        "CSRF token",
                    )
        finally:
            if self._dump:
                print()
                print("cookies:")
                print(json.dumps(response.cookies.get_dict(), indent=4))
                try:
                    print()
                    print("json:")
                    print(response.json(indent=4))
                except Exception:
                    pass
                try:
                    print()
                    print("text:")
                    print(response.text)
                except Exception:
                    pass
                print()
                print("headers:")
                print(json.dumps({**response.headers}, indent=4))
                print(20 * "^")

        return session, csrf_token

    def status(self):
        """The status of the Dashboard

        Contact the Dashboard, checking for errors, timeouts,
        etc. and report back the current status.

        Return
        ------
        status : enum (a string...)
            "running"
            "down"
            "error"
        """
        try:
            response = self._url_get("/api/status")
        except DashboardTimeoutError:
            return "down"
        except (DashboardConnectionError, DashboardUnknownError, DashboardLoginError):
            return "error"

        if response.status_code != 200:
            logger.info(
                "Encountered an error getting the status from dashboard "
                f"{self.name}, error code: {response.status_code}"
            )
            return "error"

        return response.json()["status"]

    def submit(
        self,
        flowchart,
        values={},
        project="default",
        title="",
        description="",
    ):
        """Submit the job to the dashboard."""
        logger.info(f"Submitting job to {self.name} ({self.url})")

        # Check the status of the dashboard
        status = self.status()
        if status != "running":
            raise DashboardNotRunningError(
                self.name,
                f"Cannot submit a job to Dashboard {self.name} because it is not "
                f"running. url={self.url}",
            )

        # Get all the nodes in the workflow
        steps = flowchart.get_nodes()

        # Find any Parameter steps.
        parameter_steps = []
        for step in steps:
            if step.step_type == "control-parameters-step":
                parameter_steps.append(step)

        # Prepare the command line arguments, transforming and remembering files
        files = {}
        if len(parameter_steps) == 0:
            cmdline = []
        else:
            # Build the command line
            optional = []
            required = []
            for step in parameter_steps:
                variables = step.parameters["variables"]
                for name, data in variables.value.items():
                    if data["optional"] == "Yes":
                        if data["type"] == "bool":
                            if values[name]:
                                optional.append(f"--{name}")
                        elif data["type"] == "file":
                            if data["nargs"] == "a single value":
                                filename = values[name]
                                if filename not in files:
                                    files[filename] = safe_filename(filename)
                                optional.append(f"--{name}")
                                optional.append(files[filename])
                            else:
                                optional.append(f"--{name}")
                                for filename in shlex.split(values[name]):
                                    if filename not in files:
                                        files[filename] = safe_filename(filename)
                                    optional.append(files[filename])
                        else:
                            optional.append(f"--{name}")
                            if data["nargs"] == "a single value":
                                optional.append(values[name])
                            else:
                                optional.extend(shlex.split(values[name]))
                    else:
                        if data["type"] == "file":
                            if data["nargs"] == "a single value":
                                filename = values[name]
                                if filename not in files:
                                    files[filename] = safe_filename(filename)
                                required.append(files[filename])
                            else:
                                for filename in shlex.split(values[name]):
                                    if filename not in files:
                                        files[filename] = safe_filename(filename)
                                    required.append(files[filename])
                        else:
                            if data["nargs"] == "a single value":
                                required.append(values[name])
                            else:
                                required.extend(shlex.split(values[name]))
            if len(required) > 0:
                optional.append("--")
                cmdline = optional + required
            else:
                cmdline = optional

        # Add files from any other steps
        for step in steps:
            if step in parameter_steps:
                continue
            for uri, path in step.data_files:
                filename = str(path)
                if uri.startswith("data:"):
                    newname = "job:data/" + uri[5:]
                    if filename in files and newname != files[filename]:
                        raise RuntimeError(
                            f"Duplicate file '{filename}' --> {uri[5:]} and "
                            f"{files[filename]}"
                        )
                    files[filename] = newname
                else:
                    raise RuntimeError(f"Can't handle file '{uri}'")

        # Prepare the data
        data = {
            "flowchart": flowchart.to_text(),
            "project": project,
            "title": title,
            "description": description,
            "parameters": {"cmdline": cmdline, "control parameters": values},
            "username": self.username,
        }

        response = self._url_post("/api/jobs", json=data)

        if response.status_code != 201:
            raise DashboardSubmitError(
                self.name,
                f"Error submitting the job to Dashboard {self.name} url={self.url}, "
                f"code={response.status_code}\n{response.json()}",
            )

        job_id = response.json()["id"]

        if len(files) == 0:
            logger.info("There are no files to transfer.")
        else:
            logger.info("Transferring files:")
            job = self.job(job_id)

            # Now transfer the files
            for filename, newname in files.items():
                logger.info(f"   {filename} --> {newname}")
                result = job.put_file(filename, newname)
                if result is None:
                    logger.warning(
                        f"There was a major error transferring the file {filename} to "
                        f"{self.name}."
                    )
                elif result.status_code == 400:
                    logger.warning(
                        "A bad input parameters was sent to dashboard "
                        f"{self.name} transferring the file {filename} to it."
                    )
                elif result.status_code == 403:
                    logger.warning(
                        "The user was not properly authorized on dashboard "
                        f"{self.name} transferring the file {filename} to it."
                    )
                elif result.status_code == 500:
                    logger.warning(
                        "There was an internal error in dashboard "
                        f"{self.name} transferring the file {filename} to it."
                    )
                elif result.status_code == 201:
                    pass
                else:
                    logger.warning(
                        f"The dashboard {self.name} returned error code "
                        "{results.status_code} transferring the file {filename} to it."
                    )
                    logger.debug(str(result))

        logger.info("Submitted job #{}".format(job_id))
        return job_id

    def _url_get(self, url, headers={}, params={}, timeout=None):
        """Get the url, handling errors.

        Parameters
        ----------
        url : str
            The URL to get
        headers : dict
            Dictionary of HHTP headers to send.
        params : dict
            A dictionary to sens in the query string.
        timeout : int
            A custom timeout, defaults to instance value

        Returns
        -------
        requests.response
            The requests Response object
        """
        if timeout is None:
            timeout = self.timeout

        # Login in to the Dashboard
        session, csrf_token = self.login()

        if csrf_token is not None:
            headers["X-CSRF-TOKEN"] = csrf_token
        headers["User-Agent"] = self.user_agent

        if self._dump:
            print(20 * "v")
            print("GET")
            print()
            print("headers:")
            print(json.dumps(headers, indent=4))
            print()
            print("params:")
            print(json.dumps(params, indent=4))
            print()
            print(20 * "x")

        url = self.url + url
        try:
            response = session.get(url, headers=headers, params=params, timeout=timeout)
        except requests.exceptions.Timeout:
            msg = f"A timeout occurred contacting the dashboard {self.name}"
            logger.info(msg)
            raise DashboardTimeoutError(url, msg)
        except requests.exceptions.ConnectionError:
            msg = f"A connection error occurred contacting the dashboard {self.name}"
            logger.info(msg)
            raise DashboardConnectionError(url, msg)
        except Exception as e:
            msg = (
                f"A unknown error occurred contacting the dashboard '{self.name}'\n"
                f"{type(e)} -- {str(e)}"
            )
            logger.info(msg)
            raise DashboardUnknownError(url, msg)
        finally:
            if self._dump:
                print()
                print("cookies:")
                print(json.dumps(response.cookies.get_dict(), indent=4))
                try:
                    print()
                    print("json:")
                    print(json.dumps(response.json(), indent=4))
                except Exception as e:
                    print(e)
                print()
                print("headers:")
                print(json.dumps({**response.headers}, indent=4))
                print(20 * "^")

        return response

    def _url_post(self, url, headers={}, json={}, data=None, timeout=None):
        """Post to the url, handling errors.

        Parameters
        ----------
        url : str
            The URL to get
        headers : dict
            Dictionary of HTTP headers to sned.
        json : dict
            A JSON serializable object to send in the body.
        timeout : int
            A custom timeout, defaults to instance value

        Returns
        -------
        requests.response
            The requests Response object
        """
        if timeout is None:
            timeout = self.timeout

        # Login in to the Dashboard
        session, csrf_token = self.login()

        if csrf_token is not None:
            headers["X-CSRF-TOKEN"] = csrf_token
        headers["User-Agent"] = self.user_agent

        if self._dump:
            print(20 * "v")
            print("POST")
            print()
            print("headers:")
            print(json.dumps(headers, indent=4))
            print()
            print("json:")
            print(json.dumps(json, indent=4))
            print()
            print(20 * "x")

        url = self.url + url
        try:
            if data is None:
                response = session.post(
                    url, json=json, headers=headers, timeout=timeout
                )
            else:
                response = session.post(
                    url, data=data, headers=headers, timeout=timeout
                )
        except requests.exceptions.Timeout:
            raise DashboardTimeoutError(
                url, f"A timeout occurred contacting the dashboard {self.name}"
            )
        except requests.exceptions.ConnectionError:
            raise DashboardConnectionError(
                url, f"A connection error occurred contacting the dashboard {self.name}"
            )
        except Exception as e:
            raise DashboardUnknownError(
                url,
                f"A unknown error occurred contacting the dashboard '{self.name}'\n"
                f"{type(e)} -- {str(e)}",
            )
        finally:
            if self._dump:
                print()
                print("cookies:")
                print(json.dumps(response.cookies.get_dict(), indent=4))
                print()
                print("headers:")
                print(json.dumps({**response.headers}, indent=4))
                print(20 * "^")

        return response


class _Project(collections.abc.Mapping):
    def __init__(self, dashboard, data):
        """The interface to a Project

        Parameters
        ----------
        data : dict
           The dictionary of data for the Project
        """
        self._dashboard = dashboard
        self._data = data

    def __getitem__(self, key):
        """Allow [] to access the data!"""
        return self._data[key]

    def __iter__(self) -> iter:
        """Allow iteration over the object"""
        return iter(self._data)

    def __len__(self) -> int:
        """The len() command"""
        return len(self._data)

    def __str__(self) -> str:
        "A string representation."
        return json.dumps(self._data, indent=4, sort_keys=True, ensure_ascii=False)

    @property
    def id(self):
        "The project id."
        return self._data["id"]

    @property
    def dashboard(self):
        "The dashboard for this project."
        return self._dashboard

    def jobs(self):
        """Return a list of Job objects."""
        data = {}  # placeholder for when the REST API is expanded
        response = self.dashboard._url_get(f"/api/projects/{self.id}/jobs", params=data)

        if response.status_code != 200:
            logger.warning(
                "Encountered an error getting the list of jobs for project "
                f"{self.name} from dashboard {self.name}, error code: "
                f"{response.status_code}"
            )
            return {}

        return [_Job(self.dashboard, p) for p in response.json()]


class _Job(collections.abc.Mapping):
    def __init__(self, dashboard, data):
        """The interface to a Project

        Parameters
        ----------
        data : dict
           The dictionary of data for the Job

        .. note::
          The JSON for a job looks like this::

            {
                "description": "Test for the PACKMOL step.\n\nbenzene::water $na::$...
                "finished": "2022-05-26 05:46",
                "flowchart_id": "18",
                "group": null,
                "group_id": null,
                "id": 41,
                "last_update": "2022-05-26 05:46",
                "owner": "psaxe",
                "owner_id": 2,
                "parameters": {
                  "cmdline": [
                    "--na",
                    "1",
                    "--nb",
                    "3"
                  ]
                },
                "path": "/Users/psaxe/SEAMM_DEV/Jobs/projects/default/Job_000041",
                "projects": [
                  {
                    "id": 1,
                    "name": "default"
                  }
                ],
                "started": "2022-05-26 05:46",
                "status": "finished",
                "submitted": "2022-05-26 05:46",
                "title": "PACKMOL test flowchart #16, spherical region using densi...
            },
        """
        self._dashboard = dashboard
        self._data = data

    def __getitem__(self, key):
        """Allow [] to access the data!"""
        return self._data[key]

    def __iter__(self) -> iter:
        """Allow iteration over the object"""
        return iter(self._data)

    def __len__(self) -> int:
        """The len() command"""
        return len(self._data)

    def __str__(self) -> str:
        "A string representation."
        return json.dumps(self._data, indent=4, sort_keys=True, ensure_ascii=False)

    @property
    def id(self):
        "The job id."
        return self._data["id"]

    @property
    def dashboard(self):
        "The dashboard for this project."
        return self._dashboard

    def list_files(self):
        """List the files in a job.

        Parameters
        ----------
        """
        response = self.dashboard._url_get(f"/api/jobs/{self.id}/files")

        if response.status_code != 200:
            logger.warning(
                f"Encountered an error getting the file list from job {self.id} "
                f"dashboard '{self.dashboard.name}', error code: {response.status_code}"
            )
            return []

        data = response.json()

        # Find the root path that everything is relative to.
        root = None
        for entry in data:
            if entry["parent"] == "#":
                root = PurePath(entry["id"])
                break

        result = []
        for entry in data:
            if "a_attr" in data:
                # It's a file!
                path = PurePath(data["parent"]) / data["text"]
                result.append(path.relative_to(root))

        return result

    def get_file(self, filename):
        """Get a file from a job.

        Parameters
        ----------
        filename : str
            The name of the file
        """
        params = {"filename": filename}
        response = self.dashboard._url_get(
            f"/api/jobs/{self.id}/files/download", params=params
        )

        if response.status_code != 200:
            logger.warning(
                "Encountered an error getting the status from dashboard"
                f" '{self.dashboard.name}', job {self.id}. error code: "
                f"{response.status_code}"
            )
            return None

        return response.content.decode(encoding="UTF-8")

    def put_file(self, localfile, remotefile):
        """Put a file to a job.

        Parameters
        ----------
        local : str or Path
            The local file
        remotefile : str
            The remote path from the job to the file.
        """
        m = MultipartEncoder(
            fields={"file": (remotefile, open(localfile, "rb"), "text/plain")}
        )
        headers = {"Content-Type": m.content_type}

        response = self.dashboard._url_post(
            f"/api/jobs/{self.id}/files", headers=headers, data=m
        )

        return response
