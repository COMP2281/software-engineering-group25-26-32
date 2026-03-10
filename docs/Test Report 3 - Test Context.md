All tests were performed twice: with the server running on Windows and again on MacOS. This is because these operating systems were readily accessible to the development team and have the majority of the desktop operating system market share. Client-side testing was performed with Chromium (Google Chrome and Edge), Firefox and Safari, as these are the most used modern desktop browsers, and the ones the system was designed to support. 

Test failure severity is determined as follows:

| Low | Test failure has minimal impact on system functionality and achieving the client’s needs, however may be detrimental to user experience. |
| :---- | :---- |
| Medium | Test failure may impact some features of the system or its usability, but with no impact on achieving the “Must Have” requirements. |
| High | Test failure has a major impact on core system functions, and will prevent the “Must Have” requirements from being met. |
| Critical | Test failure introduces security vulnerabilities in the system |

The justification for the severity assigned to each test is provided with the corresponding test case in the previous section.