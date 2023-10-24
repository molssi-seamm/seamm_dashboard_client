=======
History
=======

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
