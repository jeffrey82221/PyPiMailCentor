# PyPiMailCentor

Automatically sending report about python packages for python developers. This is the derive project of [PyPi_Web_Crawl](https://github.com/jeffrey82221/PyPi_Web_Crawl).


# Goal: 

- [ ] Capture link between packages, between package and contributors, between contributors and organizations. 
- [ ] Link prediction (whether dependency would emerge between two package)
- [ ] node prediction (whether a package would continue to upgrade in the near future, whether a package would switch from pure-python to hybrid language)

# Plan:


- [ ] Important info ETL
    - [X] 1a. Get author, author_email, maintainer, maintainer_email
    - [X] 1b. Github Repo Url: check info->project_urls of latest jsons for github ur
    - [ ] 2. Popularity: use github api to get Star count. (only select the most popular 10000 packages)
        - [ ] Ref: https://tryapis.com/github/api/activity-list-stargazers-for-repo
    - [ ] 3a. License: check info->license or from github repo.
    - [ ] 3b. Get repo contributors and their organization:
        - 1. list contributors REF: https://tryapis.com/github/api/repos-list-contributors
        - 2. extract organization from contributors REF: https://tryapis.com/github/api/orgs-list-for-user
- [ ] Contributor ETL
    - [ ] 4. Get email using:
        REF: https://nelson.cloud/scrape-contributor-emails-from-any-git-repository/
        git shortlog -sea | grep -E -o "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,6}\b" | awk '{print tolower($0)}' | sort | uniq | grep -wv 'users.noreply.github.com'
- [ ] Mailing package list ordered by popularity, along with package name, github repo url, company, and licenses. 
- [ ] Generate Edge.csv of every month. 
    - [ ] Link between packages based on dependency of releases (link will persist)
    - [ ] Link between packages and contributors (link with persist)

# Done: 
- [X] Move here the ETL workflow from Pypi_Web_Crawl
- [X] Refactor: extract the json loading and saving core 
- [X] Add decryption and encryption to the json loading and saving core
- [X] Add a sample and decrypt module to be use in `check_schema.yml`
- [X] Refactor: rename `check_schema.yml` to `check_latest_schema.yml`
- [X] Add a release online sampling module and build another `check_release_schema.yml` workflow
- [X] Add monthly run workflow for `update_release_time.py`.
- [X] Debug: JSkiner - pyo3_runtime.PanicException: There should not be Union in Union
- [X] Connect all ETL together at etl.yml (do it everyday monday noon. update package_name -> update latest -> update release time). 
- [X] Using auto PR instead of branch merging 
- [X] Connect check schema together at check.yml (do it everyday midnight.) 
- [X] Using line-by-line encryption to avoid change of full json file.

