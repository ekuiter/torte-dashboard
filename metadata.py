from dataclasses import dataclass

@dataclass
class L_TotalFeatures:
    latest_kconfig: int
    latest_kclause: int
    cmp_lastYear: str # +- X %
    growth_y: str  # linear, avg growth per year
    expected_5y: int
    expected_10y: int
    
class L_sloc:
    latest: int
    expected: int
    cmp_lastYear: str # +- X %
    
class L_model_count_time:
    latest_kconfig: int
    latest_kclause: int
    cmp_lastYear: str  # +- X %
    