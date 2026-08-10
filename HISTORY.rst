=======
History
=======
2026.8.10 -- Multi-queue job submission, and two real seamm_webui compatibility bugs
    * ``Dashboard.list_queues()``: lists the queues (clusters, or a plain
      local target) the dashboard's paired JobServer can route jobs to,
      with each field's override limits -- empty (not an error) against a
      dashboard that doesn't support this. ``Dashboard.submit()`` gained
      ``queue=``/``slurm_overrides=`` keyword arguments to request a
      specific queue and per-job SLURM resource overrides; omitted
      entirely from the submitted job's parameters when not given, so
      existing callers are unaffected.
    * Bugfix: ``Dashboard.login()`` treated a blank username/password
      (``""``) differently from not providing one at all (``None``),
      POSTing empty credentials as if real -- rejected by the dashboard,
      breaking login against any dashboard running with no authentication
      required. A blank credential now skips the login attempt entirely,
      the same as ``None`` already did.
    * Bugfix: ``Dashboard.list_projects()`` only worked against the old
      Flask-based dashboard's ``GET /api/projects/list`` endpoint --
      ``seamm_webui`` has no such route at all and returned an error.
      Switched to ``GET /api/projects`` (returns full project records
      instead of bare names) and extracts the names client-side; this
      endpoint exists, with the same project-name field, on both
      dashboard implementations, so ``list_projects()`` now works
      against either without needing to know which one it's talking to.

2026.8.8 -- Bugfix: login() failed against dashboards with no CSRF cookie
   * Dashboard.login() raised DashboardLoginError if a dashboard's login response had no
     CSRF cookie, even though the login itself succeeded. Some dashboards (e.g. the new
     seamm_webui) don't use a CSRF cookie at all; a missing one is now treated as
     "nothing extra to send" rather than a failure.

2025.10.31 -- Improved handling of timeouts
   * Actually increased the default timeouts to 60s.
   * Improved error messages to help diagnose problems with timeouts.
     
2025.4.3 -- Increased timeout for HTTP requests
   * Increased the default timout to 5 seconds, and 60 seconds for submitting jobs to
     allow time to transfer files.
     
2024.6.27 -- Added support for using local files in Jobs

2024.5.23 -- Bugfix: crash opening a flowchart from a Dashboard
   * SEAMM could crash when asking the Flowchart Open dialog to get the flowchart from a
     previous job. This only happened if the Dashboard was known but the stored password
     was wrong.

2024.4.22 -- Moving user preferences to ~/.seamm.d
   * Added better output when there are failures in the Dashboard.
   * To better support Docker, moving ~/.seammrc to ~/.seamm.d/seamrc

2023.11.15 -- Bugfix: boolean options now work
   * Boolean options were not handled correctly when submitting jobs.

2023.10.24 -- Improvement for job handling.
   * Added control parameters to the data stored for the job, to support filling out
     menus identical to how the job was submitted.
     
2023.7.29 -- Bugfix: error if no required parameters
   * Apparently can't use '--' without subsequent parameters.
     
2023.7.10 -- Corrected handling of control parameters
   * Now handle control parameters with multiple values.
   * Separate the options from required parameters with '--' as required.
     
2023.6.28 -- Improved error messages for login failures.

2022.8.13 (13 August 2022)
--------------------------

* First release of a working version on PyPI.
