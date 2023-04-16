# PyPiHub

Automatically sending report about python packages for python developers. This is the derive project of [PyPi_Web_Crawl](https://github.com/jeffrey82221/PyPi_Web_Crawl).


# Goal: 

- [ ] link prediction (whether dependency would emerge between two package)
- [ ] node prediction (whether a package would continue to upgrade in the near future)

# Plan:

- [ ] Move here the ETL workflow from Pypi_Web_Crawl
- [X] Refactor: extract the json loading and saving core 
- [X] Add decryption and encryption to the json loading and saving core
- [X] Add a sample and decrypt module to be use in `check_schema.yml`
- [X] Refactor: rename `check_schema.yml` to `check_latest_schema.yml`
- [X] Add a release online sampling module and build another `check_release_schema.yml` workflow
- [X] Add monthly run workflow for `update_release_time.py`.
- [ ] Debug: JSkiner - pyo3_runtime.PanicException: There should not be Union in Union
- [X] Connect all ETL together at etl.yml (do it everyday monday noon. update package_name -> update latest -> update release time). 
- [X] Using auto PR instead of branch merging 
- [X] Connect check schema together at check.yml (do it everyday midnight.) 
- [-] Using fast checkout with workspace in the same workspace. 
- [ ] Using line-by-line encryption to avoid change of full json file.
- [ ] Generate Edge.csv & Node.csv of every month. 
