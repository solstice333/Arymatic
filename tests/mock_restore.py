class MockRestore():
   """Simple way for mocking and restoring back to init"""

   def __init__(self, obj, methname, mock):
      """create a MockRestore object with receiver object |obj|,
      method name string |methname|, and MagicMock |mock|. |obj|
      can obviously be any object -- instance or class.
      """

      self._mock = mock
      self._meth = methname
      self._obj = obj
      self._saved = getattr(self._obj, self._meth)

   def __enter__(self):
      """context manager (with statement) support. Bind
      the mock to the reciever object's attribute.
      """

      setattr(self._obj, self._meth, self._mock)
      return self

   def __exit__(self, exc_type, exc_val, exc_tb):
      """restore the receiver object's attribute to what
      it was before binding the mock to it.
      """

      setattr(self._obj, self._meth, self._saved)
