from forge.utils.function_parser import parse_function_call


def test_parse_simple_call():
    """Test parsing a simple function call with keyword arguments."""
    s = "click(x=0.5, y=0.75)"
    result = parse_function_call(s)
    assert len(result) == 1
    call = result[0]
    assert call.function_name == "click"
    assert call.parameters == {"x": 0.5, "y": 0.75}


def test_parse_call_with_string():
    """Test parsing a function call with a string argument."""
    s = "type(text='hello world')"
    result = parse_function_call(s)
    assert len(result) == 1
    call = result[0]
    assert call.function_name == "type"
    assert call.parameters == {"text": "hello world"}


def test_parse_call_with_integer():
    """Test parsing a function call with an integer argument."""
    s = "scroll(amount=100)"
    result = parse_function_call(s)
    assert len(result) == 1
    call = result[0]
    assert call.function_name == "scroll"
    assert call.parameters == {"amount": 100}


def test_parse_no_arguments():
    """Test parsing a function call with no arguments."""
    s = "home()"
    result = parse_function_call(s)
    assert len(result) == 1
    call = result[0]
    assert call.function_name == "home"
    assert call.parameters == {}


def test_parse_malformed_string_returns_empty():
    """Test that a malformed string does not cause a crash and returns an empty list."""
    s = "this is not a function call"
    result = parse_function_call(s)
    assert len(result) == 0
