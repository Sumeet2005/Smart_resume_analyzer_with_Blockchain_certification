// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CertificateManager {
    struct Certificate {
        string certificateNumber;
        string studentName;
        string rollNumber;
        string degree;
        string branch;
        string graduationYear;
        string college;
        string university;
        string cgpa;
        string dateOfIssue;
    }

    mapping(string => Certificate) private certificates; // certificateNumber => Certificate
    address public issuer;

    constructor() {
        issuer = msg.sender;
    }

    modifier onlyIssuer() {
        require(msg.sender == issuer, "Only issuer can call this");
        _;
    }

    function issueCertificate(
        string memory certificateNumber,
        string memory studentName,
        string memory rollNumber,
        string memory degree,
        string memory branch,
        string memory graduationYear,
        string memory college,
        string memory university,
        string memory cgpa,
        string memory dateOfIssue
    ) public onlyIssuer {
        certificates[certificateNumber] = Certificate(
            certificateNumber,
            studentName,
            rollNumber,
            degree,
            branch,
            graduationYear,
            college,
            university,
            cgpa,
            dateOfIssue
        );
    }

    function getCertificate(string memory certificateNumber) public view returns (
        string memory,
        string memory,
        string memory,
        string memory,
        string memory,
        string memory,
        string memory,
        string memory,
        string memory,
        string memory
    ) {
        Certificate memory cert = certificates[certificateNumber];
        require(bytes(cert.certificateNumber).length != 0, "Certificate does not exist");
        return (
            cert.certificateNumber,
            cert.studentName,
            cert.rollNumber,
            cert.degree,
            cert.branch,
            cert.graduationYear,
            cert.college,
            cert.university,
            cert.cgpa,
            cert.dateOfIssue
        );
    }
}
