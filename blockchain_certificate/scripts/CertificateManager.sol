// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CertificateManager {
    
    struct Certificate {
        string certID;
        string studentName;
        string studentID;
        string degreeName;
        string major;
        string year;
        string collegeName;
        string universityName;
        string cgpa;
        string date;
    }

    mapping(string => Certificate) public certificates;
    event CertificateIssued(string certID, string studentName, string date);

    function issueCertificate(
        string memory _certID,
        string memory _studentName,
        string memory _studentID,
        string memory _degreeName,
        string memory _major,
        string memory _year,
        string memory _collegeName,
        string memory _universityName,
        string memory _cgpa,
        string memory _date
    ) public {
        certificates[_certID] = Certificate(
            _certID, _studentName, _studentID, _degreeName, _major,
            _year, _collegeName, _universityName, _cgpa, _date
        );
        emit CertificateIssued(_certID, _studentName, _date);
    }

    function getCertificate(string memory _certID) public view returns (
        string memory, string memory, string memory, string memory, string memory,
        string memory, string memory, string memory, string memory, string memory
    ) {
        Certificate memory c = certificates[_certID];
        return (c.certID, c.studentName, c.studentID, c.degreeName, c.major, c.year, c.collegeName, c.universityName, c.cgpa, c.date);
    }
}