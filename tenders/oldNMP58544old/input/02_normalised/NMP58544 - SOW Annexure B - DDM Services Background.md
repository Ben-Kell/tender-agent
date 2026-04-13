# Source: NMP58544 - SOW Annexure B - DDM Services Background.pdf
# Document Type: pdf
# Normalised For: Tender agent ingestion

## Page 1

Official
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

Official

SOW ANNEXURE B DDM SERVICES BACKGROUND

Section 1 – Introduction
1. BACKGROUND
1.1 The DDM services suite utilise the Identity Bridge COTS product and SQL products with
extensive Defence scripting to provide the following services:
a. Defence Identity Service (DIS): the central point for the registration, management
and historical auditing of unique Defence Digital Identities. This is the authoritative
source used by Certificate Services and access management services used across
Defence networks.
b. Defence Corporate Directory (DCD) : The Directory provides a single point of
aggregated authoritative Defence information. Using the DCDWEB, a web dotnet
frontend, allows Defence Users ability to search. Defence application can also
access the DCD information via approved connections. The Directory also provides
information that is used by Military Messaging.
c. Pegasus Directory Service (PDS) : part of the DCD Service, which supports
external Partners. This service is primarily executed in the Secret environment but
expanding to Protected. The PDS service allows subsets of data to be shared with
the 5eyes Partner Nations (CAN, GBR, NZL, and USA).
d. Data Exchange Service: provides the Department of Defence with the business
capability to manage the migration, integration, and matching of data across multiple
environments and systems. Using data synchronisation tools, Identity  Bridge (IB)
and SQL Server Integration Services (SSIS), the required data is: Extracted from
the source; Manipulated; and Inserted into a destination for client use.
e. Address Book Sync (ABSYNC) Service: ABSYNC service supports Defence -
Wide mail through the synchronisation of mail objects and directory data between
internal and external mail systems, as well as publishes mail system entries into the
Defence Corporate Directory.
f. User Info Provisioning (UIP) Service : provides the strategic Active Directories
(DPE/DSE) update information for their users.
g. AD List/group management (ADDL) Service: provides strategic Active Directories
(DPE/DSE) by managing Distribution G roups/Group membership based on
attributes not held by the active Directories.
1.2 In addition to the above, the following DDM has the following intranet pages that require
updates and management:
a. DCD Administration
b. Directory & Data Management

## Page 2

Official
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

Official

2. GOVERNANCE
2.1 Responsibility for maintaining the DDM services suite  lies with the Directorate of Digital
Identity Services (DDIS) within Enterprise Technology Operations Branch (ETOB).
2.2 The System Owner is the Assistant Secretary Enterprise Technology Operations
(ASETO). The Business Owner is First Assistant Secretary (FAS) People Services within
Defence People Group.
3. SYSTEM INFORMATION
3.1 System Description
3.1.1 The primary functionalities of the Services are:
a. Middleware: ViewDS Identity ridge, Microsoft SQL Integration Services
b. Databases: SQL Database Instances x3
c. Operational System: Windows 2003/2012/2016/2019, RHEL
d. Infrastructure Services: Time, Certificate Services, Defence DNS, Global Switch
Load Balancer (GSLB), Dynatrace, Nagios, Microsoft IIS Services
e. Virtualisation: Platform Service manage the OS Layer for host/storage
f. Network: the services are  firewalled protected VLAN to isolate DDM hosts.
Coordination to access client DC’s and AUG also include other firewalls.
3.2 System Interfaces
3.2.1 The DDM services suite are present on the following domains:
a. DSE – Production domain users
b. DSESIT – Test domain users
c. DSEDEV – Dev domain users
d. AUG – Production Domain
e. DPE – Production domain users
f. DPESIT – Test domain users
g. DPEDEV – Dev domain users
3.2.2 The DDM services suite interfaces with a number of external extant Defence systems and
assets, including but not limited to:
a. Active Directory (AD): DPE/DSE, DST, DIE, FIE, FIS
b. Partner Border Directory Service Agents (BDSA)
c. Simple Mail Transfer Protocol (SMTP)
d. Security Information and Event Management (SIEM)
e. Military Messaging (MMHS)
f. Defence Service Management System (DSMS)
g. Service Now
h. Objective
i. PMKeyS (CDI)
j. AGSVA

## Page 3

Official
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

Official

Section 2 - Application Services
4. OPERATIONS, MAINTENANCE, AND SUPPORT
4.1 Level Zero support is provided by DCD help pages and DSMS Knowledge Articles. The
Defence ICT Service Desk provides Level One support. Level Two and Three DDM
services support is provided by the DDM  sustainment team  (being procured under t his
approach to market). Infrastructure support for DDM  is provided under other service
towers/teams/contracts. Level Four  support for DDM  software/frameworks is provided
where applicable by the manufacturer.
4.2 The DDM services suite is classified as a Service Class 3 (SC3) application supported by
Centralised Processing (CP) as per the below agreed support timeframes:
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
Table 1: Support Timeframes
5. APPLICATION SUPPORT
5.1 Defence Identity Service (DIS)
5.1.1 The Defence Identity Service (DIS) provides the Department of Defence with a central
point of registration, management and historical information of the unique ICT Identity. This
can be authoritatively used any ICT Application across both Protected and Secret
Networks for:
a. People entities are managed on Protected for both Protected and Secret
b. Non Person Entity (Generic or Functional Roles) are managed primarily on
Protected but can also be done on Secret.
5.1.2 The Digital Identity is managed within the Everybody Database (EBDB) based on
authoritative data from the HR Systems (PMKeyS and ODS). The EBDB manages the
unique digital identity to prevent duplication and to provide a perpetual authoritative record
of the digital identity.
5.1.3 The information used to create the unique Identity is based on the correct authoritative
source, which for people are:
a. Human Resources (HR) system, PMKeyS. This is managed by Defence People
Group and is updated once a day (morning).
b. Other Defence Support (ODS) system. This is an interim system managed by DDIS
for those Identities not managed by PMKeyS. It is updated in real time.
5.1.4 People can be grouped into two groups:
a. PMKeyS Managed – this can include

## Page 4

Official
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

Official

(i) Department of Defence APS/ASD/ASA
(ii) AUS military
(iii) Some attached foreign military
b. Non PMKeyS Managed
(i) Third Party Employees
(ii) AUS APS (from other government Departments)
(iii) External Service Providers (ESP)
(iv) Professional Services Providers (PSP)
(v) Contractors
(vi) Volunteers
(vii) Foreign Military (those not recorded in PMKeyS).
5.1.5 The ICT unique Identity is based on two criteria an email address and a related employee
number. This does allow for a person with multiple employments (eg. APS, Reservist) to
have two active unique Identities. The service has the following functions:
a. Create identity when not already present and set as active.
b. Update identity when changes occur in PMKeyS or ODS information. E.g. preferred
name.
c. Deactivate identity when PMKeyS or ODS indicates Identity is inactive.
5.1.6 A history of changes is kept to allow auditing of relationship between: @defence.gov.au
value and the EmployeeNumber value.

Figure 1: Defence Identity Service Overview

5.2 Defence Corporate Directory (DCD)
5.2.1 The DCD Services provides  a single point of aggregated information across defence
environments (Figure 2). It provides to Defence Clients (Figure 3):
a. An Intranet web interface for Users, which allows directory search for contact
information of Defence personnel and Functional Contacts. Information provided is
controlled by underlying network.
b. Access to Information to meet Application specific requirements, utilising Secure
LDAP, LDAPS, and LDAP protocols.
c. Authentication Service for AUG based gateways.

## Page 5

Official
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

Official

d. Hosts the Military Messaging Service (MMHS) Application information; where the
DCD (Low) is the authoritative location for the information, and the data is replicated
to the DCD (High). The MMHS DAMS component has write access to the DCD
(Low) to make any change to MMHS information.
e. T arget system for incoming external data, such as the Pegasus Partner address
books.

Figure 2: DCD Service Overview

Figure 3: DCD Service Client Overview
5.2.2 The DCD Service utilises the DIODE Service to transfer data from low to high networks.
The following table provides the DCD’s list of External Clients:
High Side Systems Low Side Systems
• Pegasus Directory Service covers
the 5eyes partner nations (CAN,
GBR, NZL, USA)
• DIXS Interface - NZDF

## Page 6

Official
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

Official

High Side Systems Low Side Systems
• Secure Network Operating
Committee (SNOC) covers other
Australian Agencies. Examples are
DFAT, Home Affairs and AFP.
• Mission Partner Environment (MPE)
• Defence Test & Evaluation Network
(DTEN)
Table 2: DCD External Clients

Figure 4: DCD Service Overview
5.2.3 The DCD Service has the following major components:
a. DCDDSA: x500 based directory service
b. DCDWEB: IIS based web frontend
c. Pegasus Directory Services: DSA Service shared with Pegasus Partners
d. DCD Content: how to manage the content with the Directory.
e. MMHS Support: Military Messaging.
5.2.4 The DCD DSA Service applies different levels of Access Control to manage access. The
DCD Service provides a distributed structure, which consists of three levels of service.
Note there are some variations for the different environments supported:
a. T1 DSA (Master) is the only point any changes can be made.
b. T1R DSA looks to manage replication from t1 to all subordinates.
c. T2 DSA (Slave) contains a full copy of the T1 master DSA content but are distributed
around the Defence networks.
d. T3 DSA’s holds a subset of the T1 DSA content which is required to meet their
client’s requirements. These DSA’s tend to support Gateway services.

## Page 7

Official
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

Official

Figure 5: DCD Structure/Replication Overview
5.2.5 The DCD Service also provides a Distributed Website, which provides Defence users with
a single search point for Defence Entities. The Directory Information Tree contains a
number of arcs:
a. Location arc contains the Active Defence Users based on entries physical location.
b. Location Services arc contains Business Services (or Functional Entries).
c. Contacts arc contains entries for internal Australian Defence systems (mail
domains).
d. Organisation arc contains the Australian Dept. of Defence Organisation View based
on Department and Position Numbers.
e. OAA arc contains entries shared by other Australian agencies.
f. Coalition arc (not on all environments contains entries provided by Pegasus
partners).
5.3 Pegasus Directory Service (PDS)
5.3.1 This covers the specific components of the DCD Service used to provide service to
Pegasus Partners. This consists of two technical services:
a. Pegasus BDSA: DCD DSA Service with AUG Service presenting AUS content for
Partners to read back into their national systems.
b. Pegasus Reader: This provide the AUS ability to read back partner’s BDSA and
update AUS Nation systems.
5.4 Data Exchange Service
5.4.1 This service covers a range of services that collect manipulate and publish into target
system data.  The target data format match client requirements:
a. DCD Content Process: This process will publish the aggregated authoritative
Information into the DCD Service hosts.

## Page 8

Official
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

Official

b. Address Book Sync: This Data exchange covers the specifics on how the target mail
systems contacts are updated from a variety of sources (Other exchange systems,
Shares Files (CSV or LDIF), Directory (partner nation)). More information in 5.5.
c. User Information Provisioning Service: More information in 5.6.
d. Exchange Distribution Lists: This provides the ability to create dynamic Distribution
Lists for groups of people using information not readily available in Active Directory.
For example, all users of a certain employeeType at a certain location or
organisation (i.e. ALL APS & ADF CASG).
e. Data Exchange – Database connections: This covers where database-to-database
connections are used to share data either one or both ways.
f. Data Extracts: Providing files for clients. Includes the generation of the extract and
delivery of the extract file to the client (Table 3, Figure 6).
D1 Clients collect from DDM FTP Site (deprecated)
D2 Clients collect for DDM FTPS Site
D3 CDMC Delivery to Client provide SMB/SFTP
D4 DDM Send extract as email attachment to client
Table 3: Data Exchange Delivery Options

Figure 6: Data Exchange Overview
5.5 Address Book Sync (ABSYNC) Service
5.5.1 This service supports Defence wide mail by synchronisation of mail objects between
internal and external mail systems.  The service covers two significate capabilities:
a. Local address look up within the email client (Outlook and/or Notes) and;
b. Message release ability with Titus. The ABSYNC service reads the following source
system’s objects:
(i) Users
(ii) Groups (Group mailbox/Resource Mailbox)
(iii) Distribution Groups (was Distribution List)
5.5.2 The example service demonstrated in Figure 6 provides synchronised entries from source
system into the required target systems as contacts entries.
a. Read from identified locations for each System

## Page 9

Official
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

Official

b. Writes into all target system contacts location entries for required source systems
5.5.3 Source/Target Systems can be:
a. Microsoft Active Directory (Exchange)
b. Directory
c. LDIF files
d. CSV Files
5.5.4 The diagram below shows an example for one System out to three targets:

Figure 7: Example ABSYNC Service Overview
5.5.5 The diagram above shows for one Source Systems is written to multiple target systems.
The source system may have any of the following entries managed:
a. User
b. Group
c. Distribution Group (Distribution Lists)
d. Generic Account (Not for all Source Systems)
5.5.6 For each Target System the Service will manage a contact folder of Source System
Entries:
a. User
b. Group
c. Distribution Group
d. Generic Account
5.5.7 The Address book Sync Service primarily synchronises directory data between Mail
Systems both inside Defence and with external Partners (Figure 2):
a. Defence Protected Environment (DPE)
b. Defence Science & Technology (DST)

## Page 10

Official
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

Official

c. Deployed Information Environment (DIE)
d. Fleet Information Environment (FIE)
e. Fleet Information System (FIS)
f. New Zealand Defence Force (NZL).

Figure 8: Defence ABSYNC Overview
5.6 User Information Provisioning (UIP) Service
5.6.1 User Information Provisioning is the update of an AD user object using information stored
in the Defence Corporate Directory. This includes the following attributes:
a. Display Name
b. Title
c. Manager
d. Mobile Phone Number
e. Physical and Postal Address
f. Defence Unit or Directorate
g. Employee Number
h. Employee Type
i. Extension attributes for downstream synchronisations

## Page 11

Official
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

Official

5.6.2 This synchronisation runs multiple times a day to both the DRN and DPE domains on the
PROTECTED network and DSN and DSE domains on the SECRET network.
5.7 AD List/group management (ADDL) Service
5.7.1 This provides the ability to create dynamic Distribution Lists for groups of people using
information not readily available in Active Directory. For example, all users of a certain
employeeType at a certain location or organisation (i.e. ALL APS & ADF CASG).
6. MONITORING AND CONTROL
6.1 Below is an approximation of statistics over 12 months for sustainment activities:
 DPE\External DSE\AUG\External
Total users 160,000 50,000
Service Requests 221 requests via DSMS
539 EBDB requests
~250 CDMC Ops email requests
34 requests via DSMS
Incidents 116 requests via DSMS
~75 CDMC Ops email requests
393 requests via DSMS
Changes 27  13
Change tasks 360  22
Problems 1 3
Table 4: Sustainment Activity Statistics
Section 3 – Glossary
Term Definition
ABSYNC Address Book Sync
AD Active Directory
ADF Australian Defence Force
AGSVA Australian Government Security Vetting Agency
APS Australian Public Servant
ASA Australian Submarine Agency
ASD Australian Signals Directorate
AUG Australian Capital Territory Unified Gateway
AUS Australia
BDSA Border Directory Service Agents
CASG Capability Acquisition and Sustainment Group
CAN Canada
CDMC Certificate and Directory Management Centre
COTS Commercial off the Shelf

## Page 12

Official
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

Official

Term Definition
CP Centralised Processing
CSV Comma Separated Value
DAC Direct Attach Copper
DAMS Defence Formal Messaging Address Management System
DC Domain Controller
DCD Defence Corporate Directory
DCDWEB Defence Corporate Directory Website
DDIS Directorate of Digital Identity Services
DDM Directory and Data Management
DIE Deployed Information Environment
DNS Domain Name System
DPE Defence Protected Environment
DPEDEV Defence Protected Environment Development
DPESIT Defence Protected Environment Systems Integration Testing
DR Disaster Recovery
DRN Defence Restricted Network
DSA Directory System Agent
DSE Defence Secret Environment
DSEDEV Defence Secret Environment Development
DSESIT Defence Secret Environment Systems Integration Testing
DSMS Defence Service Management System
DSN Defence Secret Network
DST Defence Science Technology
EBDB Everybody Database
ESA Email Security Appliance (Cisco)
ETOB Enterprise Technology Operations Branch
FIE Fleet Information Environment
FIS Fleet Information System
FTP File Transfer Protocol
Gateway A device used to securely connect two different networks, especially two networks
of different security classifications or threat levels
GBR Great Britain
GSLB Global Switch Load Balancer

## Page 13

Official
Information Communications Technology Provider Arrangement (ICTPA)
RFQ Number: NMP58544
Work Order Title: eTools and DDM Sustainment Support

Official

Term Definition
IB Identity Bridge
LDAP Lightweight Directory Access Protocol
LDAPS Lightweight Directory Access Protocol over Secure Sockets Layer
LDIF LDAP Data Interchange Format
MMHS Military Messaging Handling System
MTBF Mean Time between Failures
NPE Non-Person Entity
NZL New Zealand
ODS Other Defence Staff
OS Operating System
PDS Pegasus Directory Services
RHEL Red Hat Enterprise Linux
SIEM Security Information and Event Management
SMTP Simple Mail Transfer Protocol
SQL Structured Query Language
SSIS SQL Server Integration Services
UIP User Information Provisioning
USA United Stated of America
VLAN Virtual Local Area Network
