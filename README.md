# owaspzap-historic

OWASP-ZAP-Historic (OZH) is a free, custom html report which provides historical ZAP execution results by storing execution results info in MySQL database and generating html reports from the database using Flask. It borrows heavily from the work done by adiralashiva8 for https://github.com/adiralashiva8/robotframework-historic

> MYSQL + Flask + OWASP Zed Attack Proxy

---

![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)
![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
![Open Source Love png1](https://badges.frapsoft.com/os/v1/open-source.png?v=103)
[![HitCount](http://hits.dwyl.com/neiljhowell/Accruent/owasp-zap-historic.svg)](http://hits.dwyl.com/neiljhowell/Accruent/owasp-zap-historic)

## OZH Overview

> <img src="https://i.ibb.co/tpC4snT/2020-06-05-08-18-39.png" alt="Overview">

---

## Features
- Store ZAP results historically
- Visualize ZAP results over time, by app version, by environment, etc.
- Search historical ZAP records by name / environment / scan type / execution id / etc
- Export results (Excel, CSV, Print, Copy)

---

## Why OZH?
- It is open source
- Made by QA

---

## How OZH Works:
- ZAP job runs in __Jenkins__ and produces report.html artifact and published HTML (stored in MySQL as URL_Link for access between OZH and published ZAP report)
- __Parser__ stores results for one or more applications in local / remote hosted __MySQL__ database and creates a delta report for __Jenkins__ to email out to recipient list.
- Generate report tables / reports using __Flask__

> <img src="https://i.ibb.co/RQfc7wM/2020-06-05-15-54-49.png" alt="owasp-zap-historic-dashboard">
