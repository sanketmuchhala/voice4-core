import voice_orchestrator
from bolchaal_contracts import CONTRACT_VERSION, TurnEventType


def test_package_imports_and_sees_contracts() -> None:
    assert voice_orchestrator.__doc__
    assert CONTRACT_VERSION
    assert TurnEventType.BARGE_IN.value == "barge_in"
