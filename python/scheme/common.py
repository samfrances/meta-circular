from typing import Tuple, Union

ParsedExpressionList = Tuple[Union[float, int, str, bool, "ParsedExpression"], ...]

ParsedExpression = Union[float, int, str, bool, ParsedExpressionList]
