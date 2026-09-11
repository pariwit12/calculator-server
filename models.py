# models.py
from pydantic import BaseModel
from typing import Any
from calculator import expand_percent as calc_expand_percent

class Expression(BaseModel):
    expr: str

    # def expand_percent(self) -> str:
    #     # ทำความสะอาด String เหมือนใน main.py เดิม
    #     clean_expr = (
    #         self.expr.strip()
    #         .replace("×", "*")
    #         .replace("÷", "/")
    #         .replace("−", "-")
    #     )
    #     # นำเข้าฟังก์ชันจาก calculator.py มาช่วยแปลง %
    #     return calc_expand_percent(clean_expr)

class CalculatorLog(BaseModel):
    timestamp: str
    expr: str
    result: Any  # ใช้ Any หรือ Union[float, int] เนื่องจากผลลัพธ์การคำนวณอาจเป็นตัวเลขใดๆ ก็ได้