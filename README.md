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

## Requirements

- Python 3.6
- MySQL DB

## Installation

 - __Step 1:__ Download and Install MySQL Server - [guide](https://bit.ly/2GrUUZ9)

 - __Step 2:__ Install owasp-zap-historic
 
    > Case 1: Using setup.py (root)
    ```
    python setup.py install
    ```
    
    > Case 2: Using git (latest changes)
    ```
    pip install git+https://github.com/Accruent/owasp-zap-historic.git
    ```
- __Step 3:__ Create *owaspzaphistoric* default user with permissions - [guide](https://bit.ly/2PIOTfI)

- __Step 4:__ Create *TB_PROJECT* table
    
    > CREATE TABLE `TB_PROJECT` (
      `Project_Id` int(11) NOT NULL AUTO_INCREMENT,
      `Project_Name` text,
      `Project_Desc` text,
      `Project_Image` text,
      `Environment` text,
      `Scan_Type` text,
      `Created_Date` datetime DEFAULT NULL,
      `Last_Updated` datetime DEFAULT NULL,
      `Total_Executions` int(11) DEFAULT NULL,
      `Recent_High` int(11) DEFAULT NULL,
      `Recent_Medium` int(11) DEFAULT NULL,
      `Recent_Low` int(11) DEFAULT NULL,
      `Recent_Informational` int(11) DEFAULT NULL,
      `Version` varchar(50) DEFAULT 'Not Captured',
      PRIMARY KEY (`Project_Id`)
      ) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;
      
- __Step 5:__ Create *TB_USERS* table

    > CREATE DATABASE `accounts` /*!40100 DEFAULT CHARACTER SET latin1 */;
    > USE accounts;
    > CREATE TABLE `TB_USERS` (
      `id` int(6) unsigned NOT NULL AUTO_INCREMENT,
      `name` varchar(255) NOT NULL,
      `email` varchar(255) NOT NULL,
      `password` varchar(255) NOT NULL,
      PRIMARY KEY (`id`)
      ) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1;

- __Step 6:__ Install owasp_zap_historic.py and owasp_zap_historic.bat
    
    More instructions later
    
> _Note:_ All actions above are one time activities


   ### Help / Know More

   To know more on available commands refer to cmd help
   ```
   owaspzaphistoric --help
   ```
   
---

## How to use OZH

- __Step 1:__ Create user in OZH
  
  > You may have to bypass the security for the first time you create a user. Any user created has the authority to create another user beyond that.
    > Remove / comment out lines 57 & 97 ({% if session['name'] %} and {% endif %}
    > (from CMD) python setup.py install
    > (from CMD) owaspzaphistoric
    > (localhost:5000/register) enter a valid username and password
    > Lines 57 & 97 can be uncommented / replaced now
    
- __Step 2:__ Create project in OZH
    > Login to OZH
    > Click the *New Project* button
    > Enter a valid name for the project (it must meet __MySQL__ db naming standards

    
