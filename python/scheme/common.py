
from typing import Tuple, Union

ParsedExpressionList = Tuple[Union[float, int, str, "ParsedExpression"], ...]

ParsedExpression = Union[float, int, str, ParsedExpressionList]
