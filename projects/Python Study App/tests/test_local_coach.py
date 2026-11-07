import pytest
from code_practice.coach import build_coaching
from code_practice.catalog import get_catalog


def reply(source, status="wrong_answer", message="Output differs", diagnostic=None):
    return build_coaching(get_catalog()["pair-sum-indices"],source,status,message,[],diagnostic=diagnostic).as_dict()


@pytest.mark.parametrize("source,line,fix", [
    ("def f():\n    if True;\n        return 1",2,"semicolon"),
    ("def f():\n    if True\n        return 1",2,"colon"),
    ("def f():\n    return (1",2,"Close"),
    ('def f():\n    return "hello',2,"quote"),
    ("def f():\nreturn 1",2,"indentation"),
])
def test_specific_syntax_diagnoses(source,line,fix):
    result=reply(source,"syntax_error","invalid syntax")
    assert result["diagnostic"]["line"]==line
    assert fix in result["nudge"]
    assert not result["question"] and not result["canContinue"]


@pytest.mark.parametrize("kind,phrase", [("IndexError","index"),("NameError","spelling"),
    ("TypeError","incompatible"),("AttributeError","attribute"),("RecursionError","depth limit")])
def test_runtime_evidence_and_location(kind,phrase):
    result=reply("def f(x):\n    return x[5]","runtime_error",kind,
                 {"exceptionType":kind,"message":"details","line":2,"column":12})
    assert result["diagnostic"]["sourceExcerpt"]=="    return x[5]"
    assert phrase in result["nudge"]
    assert "raise" not in result["nudge"]


@pytest.mark.parametrize("source", [
    "def f():\n    a=1; return a",
    "def f():\n    while True:\n        break\n    return 1",
    "def f(nums):\n    return [nums[i] for i in range(len(nums)-1)]",
    "def f():\n    return [[i*j for i in range(3)] for j in range(3)]",
    "def f():\n    print([[1,2],[3,4]])\n    return None",
])
def test_valid_exploratory_code_gets_no_speculative_warning(source):
    result=reply(source)
    assert result["title"]=="Output comparison"
    assert not result["nudge"] and not result["diagnostic"]


def test_timeout_is_cautious_and_does_not_invent_location():
    result=reply("def f():\n    while True: pass","timeout","Exceeded limit")
    assert "Possible cause" in result["nudge"] and result["diagnostic"]["line"]==2
    result=reply("def f():\n    while True:\n        break","timeout","Exceeded limit")
    assert "uncertain" in result["nudge"] and result["diagnostic"] is None


def test_internal_error_has_no_student_line():
    result=reply("def f(): return 1","runtime_error","Error",{"exceptionType":"TypeError","message":"serialization error","line":None})
    assert result["diagnostic"]["line"] is None
