# CHANGELOG - ceph

<!-- towncrier release notes start -->

## 4.1.0 / 2025-03-19 / Agent 7.65.0

***Added***:

* Add usage by device class metric. ([#19284](https://github.com/DataDog/integrations-core/pull/19284))

## 4.0.0 / 2024-10-04 / Agent 7.59.0

***Removed***:

* Remove support for Python 2. ([#18580](https://github.com/DataDog/integrations-core/pull/18580))

***Fixed***:

* Bump the version of datadog-checks-base to 37.0.0 ([#18617](https://github.com/DataDog/integrations-core/pull/18617))

## 3.0.0 / 2024-10-01 / Agent 7.58.0

***Changed***:

* Bump minimum version of base check ([#18733](https://github.com/DataDog/integrations-core/pull/18733))

***Added***:

* Bump the python version from 3.11 to 3.12 ([#18212](https://github.com/DataDog/integrations-core/pull/18212))

## 2.10.0 / 2024-01-05 / Agent 7.51.0

***Added***:

* Bump the Python version from py3.9 to py3.11 ([#15997](https://github.com/DataDog/integrations-core/pull/15997))

## 2.9.1 / 2023-08-18 / Agent 7.48.0

***Fixed***:

* Update datadog-checks-base dependency version to 32.6.0 ([#15604](https://github.com/DataDog/integrations-core/pull/15604))

## 2.9.0 / 2023-08-10

***Added***:

* Update generated config models ([#15212](https://github.com/DataDog/integrations-core/pull/15212))

***Fixed***:

* Fix types for generated config models ([#15334](https://github.com/DataDog/integrations-core/pull/15334))

## 2.8.0 / 2023-07-10 / Agent 7.47.0

***Added***:

* Add OSD metadata tags ([#14201](https://github.com/DataDog/integrations-core/pull/14201)) Thanks [mxmeinhold](https://github.com/mxmeinhold).

***Fixed***:

* Bump Python version from py3.8 to py3.9 ([#14701](https://github.com/DataDog/integrations-core/pull/14701))

## 2.7.0 / 2022-04-05 / Agent 7.36.0

***Added***:

* Add metric_patterns options to filter all metric submission by a list of regexes ([#11695](https://github.com/DataDog/integrations-core/pull/11695))

## 2.6.0 / 2022-02-19 / Agent 7.35.0

***Added***:

* Add `pyproject.toml` file ([#11323](https://github.com/DataDog/integrations-core/pull/11323))

***Fixed***:

* Fix namespace packaging on Python 2 ([#11532](https://github.com/DataDog/integrations-core/pull/11532))

## 2.5.1 / 2022-01-08 / Agent 7.34.0

***Fixed***:

* Add comment to autogenerated model files ([#10945](https://github.com/DataDog/integrations-core/pull/10945))

## 2.5.0 / 2021-10-04 / Agent 7.32.0

***Added***:

* Add runtime configuration validation ([#8892](https://github.com/DataDog/integrations-core/pull/8892))

## 2.4.1 / 2021-07-12 / Agent 7.30.0

***Fixed***:

* ceph agent 8 signature ([#9520](https://github.com/DataDog/integrations-core/pull/9520))

## 2.4.0 / 2021-04-19 / Agent 7.28.0

***Added***:

* Add Ceph Recovery metrics ([#8261](https://github.com/DataDog/integrations-core/pull/8261)) Thanks [mxmeinhold](https://github.com/mxmeinhold).

## 2.3.1 / 2021-03-07 / Agent 7.27.0

***Fixed***:

* Bump minimum base package version ([#8443](https://github.com/DataDog/integrations-core/pull/8443))
* Fail more gracefully ([#8456](https://github.com/DataDog/integrations-core/pull/8456))

## 2.3.0 / 2020-11-25 / Agent 7.25.0

***Added***:

* Support octopus version ([#8077](https://github.com/DataDog/integrations-core/pull/8077))

## 2.2.0 / 2020-10-31 / Agent 7.24.0

***Added***:

* [doc] Add encoding in log config sample ([#7708](https://github.com/DataDog/integrations-core/pull/7708))

## 2.1.2 / 2020-08-10 / Agent 7.22.0

***Fixed***:

* Update logs config service field to optional ([#7209](https://github.com/DataDog/integrations-core/pull/7209))

## 2.1.1 / 2020-06-29 / Agent 7.21.0

***Fixed***:

* Fix template specs typos ([#6912](https://github.com/DataDog/integrations-core/pull/6912))

## 2.1.0 / 2020-05-17 / Agent 7.20.0

***Added***:

* Allow optional dependency installation for all checks ([#6589](https://github.com/DataDog/integrations-core/pull/6589))
* Add ceph config spec ([#6563](https://github.com/DataDog/integrations-core/pull/6563))

***Fixed***:

* Capture type errors as well as key errors for osd perf metrics ([#6381](https://github.com/DataDog/integrations-core/pull/6381))

## 2.0.0 / 2020-04-04 / Agent 7.19.0

***Changed***:

* Account for "osdstats" key in newer versions ([#5855](https://github.com/DataDog/integrations-core/pull/5855))

***Fixed***:

* Fix response handling ([#6152](https://github.com/DataDog/integrations-core/pull/6152))
* Update deprecated imports ([#6088](https://github.com/DataDog/integrations-core/pull/6088))
* Remove logs sourcecategory ([#6121](https://github.com/DataDog/integrations-core/pull/6121))

## 1.8.0 / 2019-10-11 / Agent 6.15.0

***Added***:

* Adhere to logging call convention ([#4738](https://github.com/DataDog/integrations-core/pull/4738))

## 1.7.0 / 2019-08-24 / Agent 6.14.0

***Added***:

* Remove unused version command ([#4249](https://github.com/DataDog/integrations-core/pull/4249))

## 1.6.0 / 2019-07-09 / Agent 6.13.0

***Added***:

* Add log setup and configuration ([#3960](https://github.com/DataDog/integrations-core/pull/3960))

## 1.5.1 / 2019-06-05 / Agent 6.12.0

***Fixed***:

* Fix version discovery ([#3874](https://github.com/DataDog/integrations-core/pull/3874))

## 1.5.0 / 2019-05-14

***Added***:

* Adhere to code style ([#3488](https://github.com/DataDog/integrations-core/pull/3488))

## 1.4.0 / 2019-02-18 / Agent 6.10.0

***Added***:

* Support Python 3 ([#2837](https://github.com/DataDog/integrations-core/pull/2837))

***Fixed***:

* Resolve flake8 issues ([#3060](https://github.com/DataDog/integrations-core/pull/3060))

## 1.3.2 / 2018-11-30 / Agent 6.8.0

***Fixed***:

* Use raw string literals when \ is present ([#2465](https://github.com/DataDog/integrations-core/pull/2465))

## 1.3.1 / 2018-09-04 / Agent 6.5.0

***Fixed***:

* Add data files to the wheel package ([#1727](https://github.com/DataDog/integrations-core/pull/1727))

## 1.3.0 / 2018-03-23

***Added***:

* Add custom tag support for service checks.

## 1.2.0 / 2018-01-10

***Added***:

* Update the check to make it work with ceph luminous ([#926](https://github)com/DataDog/integrations-core/issues/926)
* Allow sending specific service checks using to the more detailed luminous health checks ([#926](https://github)com/DataDog/integrations-core/issues/926)
* Add metric for number of active monitors ([#956](https://github)com/DataDog/integrations-core/pull/956)

## 1.1.0 / 2017-07-18

***Added***:

* Add option to define the cluster name ([#438](https://github.com/DataDog/integrations-core/issues/438), thanks [@borisroman](https://github)com/borisroman)

## 1.0.0 / 2017-02-22

***Added***:

* adds ceph integration.
