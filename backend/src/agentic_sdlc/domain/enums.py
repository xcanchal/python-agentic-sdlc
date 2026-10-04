from enum import StrEnum


class Stage(StrEnum):
    RESEARCH = "RESEARCH"
    DEFINITION = "DEFINITION"
    DESIGN = "DESIGN"
    IMPLEMENTATION = "IMPLEMENTATION"
    VERIFICATION = "VERIFICATION"
    DONE = "DONE"


class WorkItemStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DONE = "DONE"
