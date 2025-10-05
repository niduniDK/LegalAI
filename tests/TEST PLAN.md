# Legal AI

# Master Test Plan

Version 1.0

## Revision History

| Date       | Version | Description         | Author       |
| ---------- | ------- | ------------------- | ------------ |
| 03/10/2025 | 1.0     | Initial Test Report | Kasige N. D. |
|            |         |                     |              |
|            |         |                     |              |
|            |         |                     |              |

## Table of Contents

1. Evaluation Mission and Test Motivation
2. Target Test Items
3. Test Approach  
   3.1 Testing Techniques and Types  
    3.1.1 Data and Database Integrity Testing  
    3.1.2 Function Testing  
    3.1.3 User Interface Testing  
    3.1.4 Performance Profiling  
    3.1.5 Load Testing  
    3.1.6 Security and Access Control Testing  
    3.1.7 Failover and Recovery Testing  
    3.1.8 Configuration Testing
4. Deliverables  
   4.1 Test Evaluation Summaries  
   4.2 Reporting on Test Coverage
5. Risks, Dependencies, Assumptions, and Constraints
6. References

# Master Test Plan

## 1. Evaluation Mission and Test Motivation

The mission and motivation for this testing iteration of Legal AI, Simple Legal Information Retrieval System for Sri Lanka, system is to ensure that the developed system works without bugs and errors. Legal information is highly sensitive and needs to be more accurate when providing to users. Being a legal information retrieval system, Legal AI should be an accurate information provider on Sri Lankan legal context. And it should meet the basic user requirements such as relevant document retrieval for a given user query, answering natural language questions in legal context, accessing previously viewed documents and previous chats on legal context. Assessing to what extent the system meets the user and developer requirements is the key motivation of this testing iteration.

Accessing legal information for a particular situation, is a decent problem for most of the people in Sri Lanka, due to poor literacy on legal domain. Furthermore, there isn't any platform which provide the facility to get an understanding (in simple language) about different acts and laws enacted in Sri Lanka. Legal AI provides a practical and reliable solution for the above problem. There are core features in the system such as chatbot feature, document search feature, document summary retrieval, and access to previously accessed discussions and documents. In addition to the above features, we support providing document recommendations based on previous user searches and let the users to access the legal documents in their preferred language (Sinhala or English).

The architecture of the developed solution consists of web-based system having hybrid retrieval (keyword search and vector search), which is the core of it. All the other functionalities are based on the retriever module. The change is on the representation of the data being retrieved. Also, there is a summary viewing option for the documents being retrieved in the system.

The history of the project involves text extraction from the legal documents (which involves ocr extraction for some documents), cleaning the extracted texts to remove common patterns, chunking the texts, encoding the texts using embedding model(legal-bert) and building the bm25 corpus for hybrid retrieval. Additionally, it involves backend services for processing natural language queries, retrieve respective summaries, retrieve documents for a give query, get recommended documents based on the user search history and backend services for database access. So far, we have focused on developing the features to satisfy the user requirements.

In this test iteration, the mission includes the following concerns,

- Verify the core user requirements

One of the key concerns of this test iteration is to check whether the system satisfies the user requirements.

- 1. Identify the functional requirements.

  - Identify the non-functional requirements

- Find and fix the bugs

To ensure the system performs as expected, we test the system to find any errors and bugs,

- Assess perceived quality risks
- Advise about product

## 2. Target Test Items

The target test items of the system, Legal AI includes both software components and third-party APIs.

- Software Component
  - User Interface
  - Retriever Module
  - Query Processor
  - Summary Generation
  - Chatbot Functionality
  - User Authentication
  - Database System
  - Document Recommendation System
- Third-party services and APIs
  - Supabase Authentication
  - FastAPI
  - NextAuth
- Web Browser Support

[Provide a high-level list of the major target test items. This list should include both items produced directly by the project development team, and items that those products rely on; for example, basic processor hardware, peripheral devices, operating systems, third-party products or components, and so forth. Consider grouping the list by category and assigning relative importance to each motivator.]

## 3. Test Approach

The test approach we'll follow both manual and automated testing approach. We performed testing to verify and validate the performance and validate the requirements. For that we mainly perform testing for Chatbot component, user authentication system, backend services for query processor, document retrieval, text summary generation, database integration and recommended document retrieval. Furthermore, we perform user interface testing for the web application to verify that the system provides a decent user experience with our system.

- Chatbot Component
- Text Summary Generation
- Backend Services
  - Query Processor
  - Document Retrieval
  - Document Analysis with Text Summary
  - Document Search Engine
  - Recommendation Pipeline
  - Get Recent User Activity
- User Authentication
- User Interface

One aspect to consider for the test approach is the techniques to be used. This should include an outline of how each technique can be implemented, both from a manual and/or an automated perspective, and the criterion for knowing that the technique is useful and successful. For each technique, provide a description of the technique and define why it is an important part of the test approach by briefly outlining how it helps achieve the Evaluation Mission or addresses the Test Motivators.

Another aspect to discuss in this section is the Fault or Failure models that are applicable and ways to approach evaluating them.

As you define each aspect of the approach, you should update Section Test Environment Configuration, to document the test environment configuration and other resources that will be needed to implement each aspect.]

### 3.1 Testing Techniques and Types

#### 3.1.1 Data and Database Integrity Testing

[The databases and the database processes should be tested as an independent subsystem. This testing should test the subsystems without the target-of-test's User Interface as the interface to the data. Additional research into the DataBase Management System (DBMS) needs to be performed to identify the tools and techniques that may exist to support the testing identified in the following table.]

| Technique Objective    | [Exercise database access methods and processes independent of the UI so you can observe and log incorrect functioning target behavior or data corruption.]                                                                                                                                                                                                                                                                                                                                                    |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Technique              | · [Invoke each database access method and process, seeding each with valid and invalid data or requests for data.<br>· Inspect the database to ensure the data has been populated as intended and all database events have occurred properly, or review the returned data to ensure that the correct data was retrieved for the correct reasons.]                                                                                                                                                              |
| Oracles                | [Outline one or more strategies that can be used by the technique to accurately observe the outcomes of the test. The oracle combines elements of both the method by which the observation can be made and the characteristics of specific outcome that indicate probable success or failure. Ideally, oracles will be self-verifying, allowing automated tests to make an initial assessment of test pass or failure, however, be careful to mitigate the risks inherent in automated results determination.] |
| Required Tools         | [The technique requires the following tools:<br>- Test Script Automation Tool<br>- base configuration imager and restorer<br>- backup and recovery tools<br>- installation-monitoring tools (registry, hard disk, CPU, memory, and so forth)<br>- database SQL utilities and tools<br>- Data-generation tools]                                                                                                                                                                                                 |
| Success Criteria       | [The technique supports the testing of all key database access methods and processes.]                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Special Considerations | - [Testing may require a DBMS development environment or drivers to enter or modify data directly in the databases.<br>- Processes should be invoked manually.<br>- Small or minimally sized databases (limited number of records) should be used to increase the visibility of any non-acceptable events.]                                                                                                                                                                                                    |

#### 3.1.2 Function Testing

The functional testing of the system Legal AI mainly covers the validation of core functions of user authentication and other backend services. For this we follow the **white box testing technique**, which assesses the internal functions and core business logic and all the helper functions being used. For this we'll write test functions using the python library called **Pytest**.

| Technique Objective    | - Validation of the business logic: This ensures that the functions related to core business logic and internal functions work properly as expected. This includes testing core functions such as process_query(), faiss_retrieve(), etc and the helper functions such as get_pdfs().<br>- Verification of the system requirements: This verifies that the system meets requirements specified by the client and the developer.<br>- Input and Output Validation: This validates the system handles the input and output properly. |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Technique              | Execute a separate test for each function such as query processing, document retrieval etc. using Pytest and record the test logs to identify the bugs and errors.<br>Use python assert function to perform input output type validation and input valid and invalid data. (For example, queries relevant to legal domain and irrelevant to legal domain.)                                                                                                                                                                     |
| Oracles                | - The system should not give any response to queries that are irrelevant to legal domain.<br>- The system should give reasonable response for natural language queries related to legal domain.<br>- System should retrieve relevant documents for a given user query.<br>- Documents suggested by the system should match the previous user searches.                                                                                                                                                                             |
| Required Tools         | - Test scripts for backend services were written using Pytest library.<br>- GitHub Copilot to generate test data for valid and invalid user queries.                                                                                                                                                                                                                                                                                                                                                                               |
| Success Criteria       | - All functions related to the business logic of the system should work as expected. (Without being fail.)<br>- All key features such as document search, chatbot response generation with natural language query processing, document recommendation, accessing user search and chat history and user authentication should work.<br>- Proper error handling techniques are applied to make the system susceptible to any condition.                                                                                              |
| Special Considerations | The accuracy of the responses generated by the chatbot relies on the Gemini LLM.                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

#### 3.1.3 User Interface Testing

User Interface testing for Legal AI verifies that the system provides access to the legal documents and important legal information and the document search and history navigation facility. This will ensure that the system can provide positive user experience with responsive UI elements.

| Technique Objective    | - Verify accessibility of the system: This ensures that all the features such as document search, chatbot, recommendation and user history are available to every user.<br>- Verify the functionality of each UI component: This ensures that all the major user interfaces and the subcomponents are working.                |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Technique              | - Create tests for testing each user interface such as chatbot interface, search interface, recommendation interface and user history interface.<br>- Simulate the UI and testing valid and invalid inputs.                                                                                                                   |
| Oracles                | - Define expected outcomes clearly (e.g., when clicking "History", the system should show past document views).<br>- Use automated checks where possible (UI testing frameworks like Selenium, Cypress, Playwright).<br>- Be careful: automated results may miss some subtle UI/UX issues (like alignment or responsiveness). |
| Required Tools         | Selenium is used as tool for automated testing.                                                                                                                                                                                                                                                                               |
| Success Criteria       | - Every major screen (interface) is tested.<br>- Common navigation paths (searching documents, accessing history, opening menus, logging out) work reliably.<br>- Users can interact without facing stuck or inconsistent behavior.                                                                                           |
| Special Considerations | - Custom or third-party UI components (like a fancy search bar widget) may not expose all properties to test scripts.<br>- Manual inspection might be required for visual checks (like layout, font, color scheme).                                                                                                           |

#### 3.1.4 Performance Profiling

[Performance profiling is a performance test in which response times, transaction rates, and other time-sensitive requirements are measured and evaluated. The goal of Performance Profiling is to verify performance requirements have been achieved. Performance profiling is implemented and executed to profile and tune a target-of-test's performance behaviors as a function of conditions such as workload or hardware configurations.

**Note**: Transactions in the following table refer to "logical business transactions". These transactions are defined as specific use cases that an actor of the system is expected to perform using the target-of-test, such as add or modify a given contract.]

| Technique Objective    | [Exercise behaviors for designated functional transactions or business functions under the following conditions to observe and log target behavior and application performance data:<br>· normal anticipated workload<br>· anticipated worst-case workload]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Technique              | · [Use Test Procedures developed for Function or Business Cycle Testing.<br>· Modify data files to increase the number of transactions or the scripts to increase the number of iterations that occur in each transaction.<br>· Scripts should be run on one machine (best case to benchmark single user, single transaction) and should be repeated with multiple clients (virtual or actual, see Special Considerations below).]                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Oracles                | [Outline one or more strategies that can be used by the technique to accurately observe the outcomes of the test. The oracle combines elements of both the method by which the observation can be made and the characteristics of specific outcome that indicate probable success or failure. Ideally, oracles will be self-verifying, allowing automated tests to make an initial assessment of test pass or failure, however, be careful to mitigate the risks inherent in automated results determination.]                                                                                                                                                                                                                                                                                                                                                                |
| Required Tools         | [The technique requires the following tools:<br>- Test Script Automation Tool<br>- an application performance profiling tool, such as Rational Quantify<br>- installation-monitoring tools (registry, hard disk, CPU, memory, and so on<br>- resource-constraining tools; for example, Canned Heat]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Success Criteria       | The technique supports testing:<br>· Single Transaction or single user: Successful emulation of the transaction scripts without any failures due to test implementation problems.]<br>· Multiple transactions or multiple users: Successful emulation of the workload without any failures due to test implementation problems.]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Special Considerations | [Comprehensive performance testing includes having a background workload on the server.<br>There are several methods that can be used to perform this, including:<br>· "Drive transactions" directly to the server, usually in the form of Structured Query Language (SQL) calls.<br>· Create "virtual" user load to simulate many clients, usually several hundred. Remote Terminal Emulation tools are used to accomplish this load. This technique can also be used to load the network with "traffic".<br>· Use multiple physical clients, each running test scripts, to place a load on the system.<br>Performance testing should be performed on a dedicated machine or at a dedicated time. This permits full control and accurate measurement.<br>The databases used for Performance Testing should be either actual size or scaled equally.] |

#### 3.1.5 Load Testing

[Load testing is a performance test that subjects the target-of-test to varying workloads to measure and evaluate the performance behaviors and abilities of the target-of-test to continue to function properly under these different workloads. The goal of load testing is to determine and ensure that the system functions properly beyond the expected maximum workload. Additionally, load testing evaluates the performance characteristics, such as response times, transaction rates, and other time-sensitive issues).]

[**Note**: Transactions in the following table refer to "logical business transactions". These transactions are defined as specific functions that an end user of the system is expected to perform using the application, such as add or modify a given contract.]

| Technique Objective    | [Exercise designated transactions or business cases under varying workload conditions to observe and log target behavior and system performance data.]                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Technique              | · [Use Transaction Test Scripts developed for Function or Business Cycle Testing as a basis, but remember to remove unnecessary interactions and delays.<br>· Modify data files to increase the number of transactions or the tests to increase the number of times each transaction occurs.<br>· Workloads should include (for example, Daily, Weekly, Monthly and so forth) Peak loads.<br>· Workloads should represent both Average as well as Peak loads.<br>· Workloads should represent both Instantaneous and Sustained Peaks.<br>· The Workloads should be executed under different Test Environment Configurations.] |
| Oracles                | [Outline one or more strategies that can be used by the technique to accurately observe the outcomes of the test. The oracle combines elements of both the method by which the observation can be made and the characteristics of specific outcome that indicate probable success or failure. Ideally, oracles will be self-verifying, allowing automated tests to make an initial assessment of test pass or failure, however, be careful to mitigate the risks inherent in automated results determination.]                                                                                                                |
| Required Tools         | [The technique requires the following tools:<br>- Test Script Automation Tool<br>- Transaction Load Scheduling and control tool<br>- installation-monitoring tools (registry, hard disk, CPU, memory, and so on)<br>- resource-constraining tools (for example, Canned Heat)<br>- Data-generation tools]                                                                                                                                                                                                                                                                                                                      |
| Success Criteria       | [The technique supports the testing of Workload Emulation, which is the successful emulation of the workload without any failures due to test implementation problems.]                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Special Considerations | · [Load testing should be performed on a dedicated machine or at a dedicated time. This permits full control and accurate measurement.<br>· The databases used for load testing should be either actual size or scaled equally.]                                                                                                                                                                                                                                                                                                                                                                                          |

#### 3.1.6 Security and Access Control Testing

| Technique Objective    | - **Application-level Security**: Verify that an actor can only access the functions or data for which their role/user type has permissions.<br>- **System-level Security**: Verify that only authorized actors can access the system and applications, and only through approved gateways.                                                                                                                                                                                                                                                                                                   |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Technique              | - **Application-level**:<br>1. Identify and list each user type (e.g., admin, manager, user, guest).<br>2. Define permissions for each user type (functions, data access).<br>3. Create test cases for each user type to verify access (transactions allowed/denied).<br>4. Modify user type roles and re-run tests to confirm correct permission updates.<br>- **System-level**:<br>1. Attempt login/access with valid credentials → should succeed.<br>2. Attempt login/access with invalid credentials → should fail.<br>3. Attempt unauthorized remote/system access → should be blocked. |
| Oracles                | - Check if the system enforces access rules correctly:<br>• For each transaction, verify if access is **granted/denied as expected**.<br>• Logs, audit trails, or system messages confirm security enforcement.<br>• Automated scripts compare expected vs. actual access results.<br>• In case of automated oracles, ensure manual verification for edge cases.                                                                                                                                                                                                                              |
| Required Tools         | - Test Script Automation Tool (e.g., Selenium, JUnit, pytest).<br>- Security breach/probing tools (e.g., OWASP ZAP, Burp Suite, Metasploit).<br>- OS Security/Admin Tools (e.g., Active Directory, Linux user management, role-based access configs).                                                                                                                                                                                                                                                                                                                                         |
| Success Criteria       | For each actor/user type:<br>• Correct functions and data are accessible.<br>• Unauthorized functions/data are denied.<br>- At system level:<br>• Only authorized users can log in.<br>• Unauthorized access attempts are blocked and logged.<br>- Security rules remain consistent after role modifications.                                                                                                                                                                                                                                                                                 |
| Special Considerations | - Must coordinate with **network/system administrators** to align with organizational policies.<br>- Some system-level access testing may not be required if handled entirely by network/security administration.<br>- Ensure testing does not violate penetration/security policies.<br>- Avoid unapproved use of breach tools in production systems.                                                                                                                                                                                                                                        |

#### 3.1.7 Failover and Recovery Testing

| Technique Objective    | - Simulate failure conditions and exercise recovery processes (manual & automated) to restore the database, applications, and system to a known, desired state.<br>- Conditions tested include:<br>• Power interruption (client/server)<br>• Network communication loss<br>• DASD/device controller failures<br>• Interrupted processes (sync/filter)<br>• Invalid/corrupted database pointers, keys, and fields                                                                                                                                                                                                                                                                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Technique              | - Use **Function & Business Cycle test cases** as a basis for defining recovery success criteria.<br>- **Client power loss** → power PC down.<br>- **Server power loss** → simulate/initiate server power down.<br>- **Network interruption** → physically disconnect network cables or power down servers/routers.<br>- **DASD/controller interruption** → simulate or physically remove device communication.<br>- **Incomplete cycles** → abort/terminate ongoing DB processes mid-execution.<br>- **Database corruption** → manually corrupt keys, pointers, or fields, then run functional transactions to check recovery.<br>- After failure, execute additional transactions, invoke recovery processes, and verify successful restoration. |
| Oracles                | - Compare post-recovery system state against known good baseline.<br>- Check that:<br>• Database integrity is maintained (no missing/duplicate/corrupted records).<br>• Applications resume correctly after recovery.<br>• Transactions are completed or rolled back safely.<br>- Use logs, monitoring tools, and automated checks to detect inconsistencies.<br>- Automated oracles can verify system availability & data correctness, but manual verification may be needed for edge cases.                                                                                                                                                                                                                                                          |
| Required Tools         | - Base configuration imager/restorer (for rollback).<br>- Installation monitoring tools (registry, disk, CPU, memory).<br>- Backup & recovery tools (DB restore, snapshot recovery, RAID tools).<br>- Diagnostic or fault simulation software (for safer alternatives to physical disconnects).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Success Criteria       | - System, application, and database successfully recover from one or more simulated disaster scenarios.<br>- Recovery returns system to a known, consistent, desired state.<br>- No data integrity loss (or minimal acceptable data loss).<br>- Failover systems correctly take over when the primary fails.<br>- End-users can continue transactions or resume operations post-recovery.                                                                                                                                                                                                                                                                                                                                                                      |
| Special Considerations | - System, application, and database successfully recover from one or more simulated disaster scenarios.<br>- Recovery returns system to a known, consistent, desired state.<br>- No data integrity loss (or minimal acceptable data loss).<br>- Failover systems correctly take over when the primary fails.<br>- End-users can continue transactions or resume operations post-recovery.                                                                                                                                                                                                                                                                                                                                                                      |

#### 3.1.8 Configuration Testing

| Technique Objective    | - Verify the operation of the system under different **hardware and software configurations**.<br>- Observe and log system behavior while varying client workstation specs, network connections, active applications, drivers, and available resources.<br>- Identify any configuration changes that affect stability, performance, or functionality.                                                                                                                               |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Technique              | - Use existing **Function Test scripts** as baseline.<br>- Open/close non-target software (e.g., MS Excel, Word) before or during tests to simulate real usage conditions.<br>- Execute application transactions while background applications consume resources.<br>- Repeat the tests with reduced available memory and varying resource loads.<br>- Run the target system on different supported hardware and OS configurations (CPU, RAM, drivers, network conditions). |
| Oracles                | - Compare observed system behavior with expected outcomes across configurations.<br>- Check if functionality remains correct despite background load or reduced memory.<br>- Monitor system logs, resource usage (CPU, memory, disk, network), and response times.<br>- Automated scripts can detect performance drops, errors, or crashes across runs.<br>- Manual review may be needed for usability or compatibility issues (e.g., UI rendering differences).            |
| Required Tools         | - Base configuration imager/restorer (to reset system state).<br>- Installation & resource monitoring tools (registry, CPU, memory, disk, network analyzers).<br>- Virtual machines/containers for simulating different OS/hardware setups.<br>- Device driver and dependency tracking tools.                                                                                                                                                                                               |
| Success Criteria       | - Target system functions correctly on **all supported hardware/software combinations**.<br>- No unexpected crashes, data loss, or performance degradation under different configurations.<br>- The application coexists correctly with commonly used non-target software (e.g., MS Office).<br>- Behavior remains consistent across multiple test runs.                                                                                                                        |
| Special Considerations | - Identify what non-target applications are commonly present and in use (e.g., Office suite, browsers).<br>- Document the **networks, servers, databases, and OS** that form part of the test environment.<br>- Consider workload data (e.g., large spreadsheets, 100-page Word docs) that may impact memory.<br>- Ensure configurations tested reflect **real-world deployment environments** to avoid missing compatibility issues.                                           |

## 4. Deliverables

In this section, we'll highlight the test deliverables of Leagl AI. After performing all the tests, we record the results of them. And this section includes,

- Test logs
- Functional test reports
- User interface test details
- Database Performance

/

### 4.1 Test Evaluation Summaries

Test evaluation summaries provide an idea of the status of the tests performed on Legal AI. And it reflects the successes and failures of the system after making changes to the system. This is performed after each development iteration to ensure the system works as expected even after the changes are made.

### **Backend Test Logs**

### **User Interface Test Details**

### 4.2 Reporting on Test Coverage

## 5. Risks, Dependencies, Assumptions, and Constraints

[List any risks that may affect the successful execution of this **Test Plan**, and identify mitigation and contingency strategies for each risk. Also indicate a relative ranking for both the likelihood of occurrence and the impact if the risk is realized.]

| Risk                                    | Mitigation Strategy                                                                                                                                                          | Contingency (Risk is realized)                                                                                           |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Prerequisite entry criteria is not met. | <Tester> will define the prerequisites that must be met before Load Testing can start.<br><Customer> will endeavor to meet prerequisites indicated by <Tester>.              | - Meet outstanding prerequisites<br>- Consider Load Test Failure                                                         |
| Test data proves to be inadequate.      | <Customer> will ensure a full set of suitable and protected test data is available.<br><Tester> will indicate what is required and will verify the suitability of test data. | - Redefine test data<br>- Review Test Plan and modify<br>- components (that is, scripts)<br>- Consider Load Test Failure |
| Database requires refresh.              | <System Admin> will endeavor to ensure the Database is regularly refreshed as required by <Tester>.                                                                          | - Restore data and restart<br>- Clear Database                                                                           |

## 6. References

- Indicate the tool references (name, available at &lt;<URL&gt;>) used for testing
- Refer any data/ information in a standard format (eg. IEEE referencing style)
- For different algorithms/ techniques/ theories you can refer text books.
- For tools you can refer web pages.
- For similar work you can refer research paper articles that describe the work.
- You may include white paper articles for the description of technologies; web URL for the tool references. When you refer such a web page, you have to indicate the (Accessed on &lt;<date&gt;>)
