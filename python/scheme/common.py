from typing import List, Union

ParsedExpressionList = List[Union[float, int, str, "ParsedExpression"]]

ParsedExpression = Union[
    float, int, str,
    ParsedExpressionList
]


