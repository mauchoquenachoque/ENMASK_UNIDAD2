from enum import Enum


class ComplianceFramework(str, Enum):
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI_DSS"
    ISO_27001 = "ISO_27001"
    SOC2 = "SOC2"
    CCPA = "CCPA"
    GLBA = "GLBA"
    FERPA = "FERPA"
