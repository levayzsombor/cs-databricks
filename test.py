from dataclasses import dataclass
from typing import TypeVar

# comment

@dataclass
class Test:
    name: str
    value: int

    def display(self) -> None:
        print(self.name, self.value)

class ChildTest(Test):
    pass

T = TypeVar("T", bound=Test)

def test_this_thing(x: T) -> None:
    x.display()