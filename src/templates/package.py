name = "@PACKAGE_NAME@"

version = "0.0.0"

authors = [
    "@USER_NAME@"
]

description = \
    """
    @DESCRIPTION@
    """

tools = [
]

requires = [
    "src"
]

uuid = @UUID@

def commands():
    env.PYTHONPATH.append("{root}/src")
    env.PATH.append("{root}/bin")
