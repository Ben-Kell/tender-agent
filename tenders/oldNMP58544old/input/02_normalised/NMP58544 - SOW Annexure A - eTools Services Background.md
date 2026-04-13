# Source: NMP58544 - SOW Annexure A - eTools Services Background.pdf
# Document Type: pdf
# Normalised For: Tender agent ingestion

## Page 1

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

1
OFFICIAL: SENSITIVE
SOW Annexure A - eTools Services Background
1. eTools Overview
1.1. The eTools application suite consists of three sub-applications that share a code-base, My
Account Management Online (MAMO), the Defence Account Retirement Service (DARS)
and Defence Enterprise Administrator (DEA). These applications have been developed
and maintained internally within Defence by APS and above-the-line contractors beginning
since 2005 with DEA v1.
1.2. DEA is a locally-deployed application/client first developed in 2005 (eTools v1) providing a
front end for users to administer Active Directory and Exchange, reducing the requirement
for direct/manual changes. DEA remains a VB6 application.
1.3. In 2016 MAMO went live as part of the eTools v2 update, which also updated DEA to v2.
Replacing the previous eTools account request interface with the re-branded and heavily
updated MAMO v2. MAMO allowed users to submit requests for network account creation,
offboarding and management, and processed those requests automatically.
1.4. MAMO consists of a user -facing .NET  and Blazor  web app,  application services that
process requests written in C# utilising a SQL database.
1.5. DARS is an automated batch process service that identifies, disables and deletes standard
network accounts that do not comply with ICT security policy  (represented as a set of
configurable variables). DARS went live in production in ~May 2023 and is written in VB6.
1.6. eTools v3 development began in  late 2022. The goal of v3 was to modernise the eTools
code base, move to a microservices architecture and later also to ensure compatibiltiy with
supported software frameworks, such as .NET.  Approximately 80% of MAMO DPE has
been migrated to and is currently running v3, with just the v2  MAMO task processor and
one other service still operating under the v2 code, awaiting development and migration to
v3. MAMO DSE remains on v2 with intent to migrate to v3. DARS and DEA are also still
using the v2 codebase, with intent to migrate to v3 and consolidating to a single codebase
across all eTools applications and domains.
1.7. As indicated in the below high level archite ctural diagrams, eTools applications draw
heavily upon DDM data sources , and in some cases populate and update those data
sources, typically via stored procedures.  Note the term CDMC in the diagrams refers to
Certificate and Directory Management Centre, th e directorate  that was previously
responsible for operating DDM. CDMC  that operated DDM, and the previously separate
directorate that developed and operated eTools, were merged together to become the
Directorate of Digital Identity Services , now responsibl e for both eTools and DDM .
Therefore, CDMC in these diagrams can be read as DDM , referring to various different
DDM services/functions.
1.8. eTools has undergone consistent development and enhancement over the years to meet
urgent business and security needs. As a result, not all of the supporting documentation
been m aintained to industry standards. T here will be instances where eTools
documentation is not in full alignment with the application and code base which will require
remediation when identified during software development lifecycle.
1.9. eTools (MAMO, DARS and DEA) is present in the following Defence domains:

## Page 2

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

2
OFFICIAL: SENSITIVE
(a) DSE – Production domain users
(b) DPE – Production domain users and Pre-Prod test environment
(c) DPESIT – Non-integrated test environment, not used
(d) Local workstations – Development
1.10. eTools interfaces with a number of external extant Defence systems and assets including:
(a) Token Management System (TMS -  Jellyfish) – for data on and deprovisioning
access card logical access
(b) Personnel Access Control System  (PACS - Gallagher) – for data on and
deprovisioning access card physical access
(c) Objective – for Objective account de/provisonining/updates
(d) Active Directory – for account de/provisioning/updates
(e) Exchange – for account and mailbox de/provisioning/updates
(f) DDM – for Other Defence Support, PMKeyS, MyClearance and other data used in
account de/provisioning/updates
(g) SMTP – for sending MAMO and DARS emails to users
1.11. Below is an approximation of statistics over 12 months for sustainment activities for DPE:
Total users ~100,000+
Service Requests 722
Incidents 1275
Problems 2
Changes 14
Change tasks 20
1.12. Below is an approximation of statistics over 12 months for sustainment activities for DSE:
Total users ~50,000
Service Requests 10
Incidents 120
Problems 1
Changes 3
Change tasks 2
1.13. MAMO has been developed with redundant infrastructure and services in mind, DEA is a
locally hosted client application, and DARS is a batch application service. As a result of
these factors and despite eTools importance to the Defence enterprise, eTools has not had
any Priority 1 or 2 incidents/unplanned outages in the past year, nor any instances of
needing to attend on-site after hours.
1.14. eTools is categorised as a Service Class 3 application supported by CP as per the below
agreed support timeframes:

## Page 3

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

3
OFFICIAL: SENSITIVE
Item SC3
Support Hours 24x7x365
Availability 99%
Operational Recovery Time Objective
(ORTO)
< 24 Hours
Operational Recovery Point Objective
(ORPO)
< 10 Minutes
Mean Time To Restore Service (MTRS) < 88 Hours
Mean Time Between Failures (MTBF) 8,760 Hours
System Maintenance N, N-1 Release Latest Patches
DR Time Objective < 48 Hours
1.15. eTools support services are provided by the eTools sutainment team  (being procured
under this approach to market). Level 0 support is provided by MAMO help pages. Level 1
support is provided by the Defence ICT Service Desk. Level 2 and 3 eTools application
support is provided by the eTools sustainment team. Infrastructure support for eTools is
provided under other ser vice towers/teams/contracts. Level 4 support for eTools
software/frameworks is provided where applicable by the manufacturer, noting that as
eTools is a group of bespoke applications created by Defence this is limited – for example
contacting Microsoft for .NET or SQL support.

## Page 4

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

4
OFFICIAL: SENSITIVE
2. My Account Management Online (MAMO) Overview
2.1. As MAMO fulfils requests on behalf of end users, the system has been designed
predominantly around Microsoft architectures.
2.2. The application stack can be broken up into 3 distinct components:
(a) MAMO Web Service: The MAMO web service provides the user-centric interface for
Defence employees to request the various MAMO services. The web service is a
standard .NET web app using ASP.NET a nd Blazor and hosted on a Windows IIS
server.
(b) MAMO Application Services: When a MAMO request is submitted through the web
service, the work is assigned to one of the 9 MAMO Application Service servers.
These servers will then process the request and send t he relevant notification (if
required) to the end user once completed. These servers work in a high availability
manner, if a server is unavailable or unable to complete a request, the request will
move to the next available server. The MAMO Application services are written in C#,
and hosted on Windows Server 2016.
(c) MAMO Database:  The MAMO database stores information about submitted
requests, their status within the MAMO processing queue and other information
required for auditing purposes. The MAMO database runs on SQL Server 2017.
2.3. A list of the MAMO Production infrastructure can be found below:
Function Software Server/Hardware
MAMO Web Service .NET Web-app 1x Window Server 2016
MAMO Application Servers C# Application 9x Windows Server 2016
MAMO Database Server SQL Server 2017 1x Windows Server 2016
2.4. Due to the complexity of the Defence environment, along with mandated security and
process requirements, there are currently no commercial off -the-shelf products available
that can perform all of the tasks associated with the eTools suite of requirements. Defence
has investigated several alternative commercial solutions, but all would have required
significant customisation and none could guarantee that all of the automated functionality
that Defence required could be implemented.
2.5. eTools v2 has implemented all of Defence’s stringent security requirements to ensure that
the integrity of the Defence Information Environment  is maintained. The security
requirements included in eTools v2 are:
(a) Strong database connection strings with encryption in a secure location
(b) The implementation of appropriate identities such as Active Directory logon and SQL
permissions for access
(c) Securing data that flows across the network using Secure Sockets Layer (SSL)
(d) Compliance with Defenc e security standards in addition to the use of Integrated
Windows Authentication when utilising Internet Information Service (IIS)
2.6. MAMO is currently maintained using either Visual Studio 2017 or JetBrains Rider with
Visual Studio Team Foundation Server 2015. Dynatrace monitoring has recently been
implemented to assist the sustainment team in supporting etools, allow enhanced
performance monitoring etc.

## Page 5

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

5
OFFICIAL: SENSITIVE
2.7. Below is an overview of key eTools (currently only MAMO) v3 migration design principles:
(a) Frontend Blazor service: The front end service for the new v3 redesign is modular
in nature and uses cshtml. It utilises a pattern called “components”, which enables
developers to write once and reuse later. This allows developers to quickly input data
into a component, and have it self -render to the user, rather than pre- establishing
the title of every grid, what columns it has, what cells are displayed etc.The use of
components enables extra hand-holding through forms via real-time validation of the
data prior to submi ssion. This reduces user error and allows a streamlined
informative journey for change modify requests as well as immediate requests.
(b) Authentication Middleware: The authentication middleware automatically detects,
decodes, verifies and applies claims principals when using the MAMO service. This
verifies the JSON Web Token, confirming that it exists, is valid and was created on
the current domain with valid signing keys. It then queries  the user profile in the
eTools database and confirms  the applied roles are active, before applying
permission nodes as required.This session is then reused while the user pers ists a
signalR connection, allowing them to browse restricted areas of the application
without having to re-verify the token for a set period.
(c) Unit of work repositories: Data connections  are simplified  using the entity
framework and the unit of work design pattern. Entities are realised as database
entities, and are a direct reflection in code. They are also domain specific, and persist
in their respective domain inside the code base. Linq to Db and Linq to entities
interfaces are strictly enforced. S trict entity and context separation is enforced ,
preventing contamination of entity contexts and query segregation. Data connections
are Asynchronous providing execution context on multiple databases in parallel.
Modular connection design concepts are applied allowing resusability across multple
functional silos and external projects.
(d) Linq to LDAP: Significant changes have been applied in the LDAP protocol space
to conform to modern programming practices . As part of this work, compilers have
been made that allow the abstraction of LDAP queries into a fluent styling.
(e) Dynamic Expressions : For modern day data querying requi ring the ability to
dynamically filter data extemporaneously  eTools leverages expressions and
functional predicates applying them to data sources. This requires JIT compiling user
parameters from data grid states into functional methods, using a series of linq
expressions. The result is a completely dynamic grid with pagination, filterability per
column, multi sorting and global variable filtering. This greatly increases the
filterability of data states for the users, allowing them to quickly navigate and search
for the data that they require.
(f) API Integration: The v3 solution has been designed with security as the primary
imperative. Defence applications require strict levels of identity data. eTools v3 has
been built with a particular focus on REST API methods for all integrations. This API
design allows future projects to communicate via managed, audited, governed API
methods providing secure and reliable data flow.
2.8. During peak periods, MAMO  can have up to ~90,000 unique users a month, equating to
approximately ~50,000,000 pages loaded and ~40,000 requests.
2.9. MAMO functions/requests include the following:

## Page 6

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

6
OFFICIAL: SENSITIVE
(a) Create a network account
(b) Move a network account
(c) Request application access
(d) Request Everybody Database (EBDB) access
(e) Request a temporary MFA exclusion
(f) Extended Leave (temporary network account suspension)
(g) Create an Other Defence Support (ODS) record
(h) Renew an ODS record expiry date
(i) Update ODS record details
(j) Leaving Defence requests – ODS, APS or ADF
(k) Create a resource mailbox
(l) Manage a resource mailbox
(m) Delete a resource mailbox
(n) Pending approvals and current/previous requests
(o) Help pages
(p) Self-service reporting functionality on different types of requests
(q) Various network security functions for ICT Security
(r) Service Desk verification function
(s) MAMO/DEA role management
(t) Administrative functions for MAMO administrators
(u) Other functions.
2.10. MAMO primary end users are supervisors and contract managers for staff onboarding and
offboarding, and all staff with Defence network access to manage their account. Other key
MAMO users are:
(a) The ICT Service Desk, for caller verification and troubleshooting assistance
(b) ICT Security, for approval of some types of requests and other functions
(c) Reporting stakeholders –stakeholders across Defence consume MAMO reporting,
in particular leaving-request data to inform their own off-boarding activities
(d) DDIS MAMO administrators, for administration and troubleshooting.
2.11. Below are diagrams showing high- level process w orkflow for requests and system
architecture.

## Page 7

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

7
OFFICIAL: SENSITIVE

## Page 8

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

8
OFFICIAL: SENSITIVE

## Page 9

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

9
OFFICIAL: SENSITIVE
Defence Enterprise Administrator (DEA) Overview
2.12. DEA is a custom application designed specifically to manage the Defence Active Directory
and Exchange environment for both the Protected and Secret domains.
2.13. DEA is one of three distinct applications developed for the eTools suite of products. Written
in Visual Basic 6, DEA is currently considered a legacy design with the possibility of being
uplifted to a modern web based capability in future.
2.14. The DEA application provides extended, comprehensiv e attribute and account system
administrative functions through a single locally hosted front end user interface application.
2.15. DEA interacts with a number of corporate data sources and technology platforms providing,
but not limited to, the following:
(a) AD objects managed with the same rules and configuration as the eTools MAMO
product
(b) Email account management and administration
(c) Enforced administration in accordance with Defence policy
(d) AD objects to be centrally managed for multiple Exchange and Active Directory
environments using a single interface
(e) Distribution List management and administration
(f) User, generic and shared mailbox account management and administration
(g) Querying EBDB, ODS, PMKeyS, DCD and myClearance data.
2.16. The DEA administrative interface is tightly coupled with the eTools framework and uses a
variety of SQL configuration tables for operational purposes.
2.17. DEA user access is provisioned by team leaders with authorisation using the MAMO
application. The DEA application is installed locally as a client application packaged
through Defence’s SOE Software Centre service.
2.18. There are approximately 300 unique DEA users, performing approximately 500,000
transactions per year. DEA users are split across various teams including the ICT Service
Desk, ICT Cyber Security teams, the Central Processing COE Exchange and Active
Directory teams, the Fleet Information Systems Support Office and the eTools and DDM
Sustainment teams.
2.19. DEA has not been significantly updated in several years, other than for packaging changes
to ensure ongoing Windows SOE compatibility (as a locally hosted client application). Due
to its age DEA may require uplifting to a more modern user centric design for any significant
changes, while continuing to follow eTools v3 design principles.
2.20. The diagram below outlines the high level DEA architecture:

## Page 10

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

10
OFFICIAL: SENSITIVE

## Page 11

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

11
OFFICIAL: SENSITIVE
3. Defence Account Retirement Service (DARS) Overview
3.1. DARS is a batch application that runs as an installed windows service. It is triggered by
Windows System Scheduler to run at configured times and dates, with a typical processing
time of about 8 hours. DARS  currently runs as a single threaded application due to how
contexts must stay open with certain data sources that do not allow multiple threaded
contexts or Asynchronous communication.
3.2. DARS performs several different actions including:
(a) deletes accounts as the culmination of successful MAMO leaving requests
(b) sends email warnings to supervisors and holders of accounts that are at risk of
becoming non-compliant
(c) disables non-compliant accounts, and
(d) eventually deletes accounts that continue to be non-complaint.
3.3. The variables that determine account non-compliance, as well as when the resulting
actions are due to occur, are all configurable.
3.4. DARS disables approximately 3000 accounts per month and deletes approximately 1800
accounts per month (including routine offboards as a result of a MAMO leaving request).
DARS processes many more records than this daily, as there are many accounts that are
at risk of becoming non-compliant, are sent email warnings by DARS, but then have their
reasons for non- compliance resolved and therefore do not end up being disabled or
deleted.
3.5. Although DARS is not an accessible application with end-users like MAMO or DEA, it is an
important component in Defence’s security-in-depth layered approach, greatly reducing
trusted insider risk and Defence’s threat surface.
3.6. DARS retrieves ‘target’ account data via SQL from the MAMO database for accounts due
to be deleted as a result of leaving requests , then scans AD  for accounts meeting the
retirement rules. DARS then generates email warnings or in serious cases, disables and
schedules the accounts and access for removal.
3.7. To determine whether an account is non- compliant and requiring action DARS
communicates with Defence’s Active Directory forest, scanning all active AD controllers to
find the absolute source of truth for a user’s activity on the network. This communication is
done via LDAP, and is queried via transpiled and optimised C# mappings to dynamic
LDAP. DARS also checks HR systems like the other defence staff data sources, PMKeyS
and Everybody Database. This is done via DDM populating staging tables for DARS to
review containing relevant HR, security clearance and other types of data.
3.8. The DARS Assembly is written in VB.NET targeting VB Version 6. DARS also utilises C#
assemblies and libraries written and targeted for legacy .NET versions . This code is
compiled from modular libraries and binaries from the eTools stack, which has been cross
compiled over to . NET standard interop with VB. DARS uses transitive packages and
assemblies from various NuGet sources.
3.9. Below are high level architecutre diagrams for DARS.

## Page 12

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

12
OFFICIAL: SENSITIVE

## Page 13

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

13
OFFICIAL: SENSITIVE
The DARS Staging table is built using DDM (CDMC) stored procedures from an import of AD combined with their source data tables. The
workflow and integration of the staging table in to DARS is shown below.

## Page 14

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

14
OFFICIAL: SENSITIVE

## Page 15

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

15
OFFICIAL: SENSITIVE

## Page 16

OFFICIAL: SENSITIVE
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

16
OFFICIAL: SENSITIVE
END OF DOCUMENT
