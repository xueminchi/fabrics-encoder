import casadi as ca

from optFabrics.exceptions.spec_exception import SpecException


def checkCompatability(a, b):
    if a.x().size() != b.x().size():
        raise SpecException(
            "Operation invalid",
            "Different dimensions: " + str(a.x().size()) + " vs. " + str(b.x().size()),
        )
    if not (ca.is_equal(a.x(), b.x())):
        raise SpecException(
            "Operation invalid",
            "Different variables: " + str(a.x()) + " vs. " + str(b.x()),
        )


def joinVariables(var1, var2):
    var = var1 + var2
    unique_items = []
    for item in var:
        already_exists = False
        for u_item in unique_items:
            if u_item.size() == item.size() and ca.is_equal(u_item, item):
                already_exists = True
                break
        if not already_exists:
            unique_items.append(item)
    return unique_items
