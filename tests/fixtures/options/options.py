from yamlmacros import macro_options


@macro_options()
def test_abc(a, b, c):
    return [a, b, c]
