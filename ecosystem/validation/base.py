"""
Validator base classes
"""

from ecosystem.serializable import JsonSerializable


# pylint: disable=keyword-arg-before-vararg, invalid-name)


class MemberValidator:
    """
    Base-class for members validation
     * id: Unique identifier for the validation
     * category: (one of the categories in https://qisk.it/ecosystem-checks )
     * affects: path to the member attribute affected by the validation (it can be None)
    """

    id = None
    category = None
    affects = None
    # Free strings that affect https://qisk.it/ecosystem-checks
    title = None
    applies_to = "all"
    related_to = []  # List of validator.id

    def __init__(self):
        self.passed = None
        self.details = None
        self.member = None

    @property
    def validator_class(self):
        """Returns the class name for a validator subclass"""
        return (
            f"{self.__class__.__module__.replace('ecosystem.validation.', '')}"
            f".{str(self.__class__.__name__)}"
        )

    @property
    def description(self):
        """Returns the docstring for the description in qisk.it/ecosystem-checks"""
        return self.__doc__

    def test(self):
        """Implement this method to test a validation"""
        raise NotImplementedError("This test is not implemented. Is that intentional?")

    def validate(self, member):
        """Main entry point for a MemberValidator"""
        self.member = member
        self.test()

    def assertIsNotNoneOrEmpty(self, item, msg=None, *args):
        """Checks if item is something but None"""
        self.passed = True
        if item is None:
            self.passed = False
            self.details = "The item is None"
        elif len(item) == 0:
            self.passed = False
            self.details = "The item is empty"
        else:
            pass
        if msg:
            self.details = msg.format(*args)
        if not self.passed:
            raise AssertionError(f"{self.member.name_id} [{self.id}]: {self.details}")

    def assertIn(self, item, container, msg=None, *args):
        """Checks if item is in container"""
        if item in container:
            self.passed = True
        else:
            if msg:
                self.details = msg.format(*args)
            else:
                self.details = f"{item} missing from container"
            self.passed = False
            raise AssertionError(f"{self.member.name_id} [{self.id}]: {self.details}")

    def assertSubset(self, small_set, big_set, msg=None, *args):
        """Checks if all the elements in small_set are in big_set"""
        missing = []
        self.passed = True
        for item_in_small in small_set:
            if item_in_small not in big_set:
                missing.append(item_in_small)
                self.passed = False
        if not self.passed:
            self.details = f"{self.member.name_id}: "
            if msg:
                self.details = msg.format(*args)
            else:
                self.details += f"{missing} missing from set"
            raise AssertionError(f"{self.member.name_id} [{self.id}]: {self.details}")


class FailedValidation(JsonSerializable):
    """
    [validation.L01]
    id = validation.id
    affects = (optional) validation.affects
    details = (optional) validation.details
    status =
      * WARNING = still possible to participate, but it needs attention
      * IGNORE = the failing validation can be ignored. Explain in "details" why.
      * FATAL = the reason why the member was removed from the ecosystem website
    tracking_issue = (optional) Link to the issue that tracks
                     the validation fix (submitted manually)
    last_check = ISO date
    failing_since = ISO date
    """

    def __init__(
        self,
        id_,
        status,
        details=None,
        affects=None,
        failing_since=None,
        last_check=None,
        tracking_issue=None,
        **kwargs,
    ):
        self.id = id_
        self.status = status
        self.details = details
        self.affects = affects
        self.last_check = last_check
        self.failing_since = failing_since
        self.tracking_issue = tracking_issue
        self._kwargs = kwargs
