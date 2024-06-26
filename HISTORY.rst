=======
History
=======
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
