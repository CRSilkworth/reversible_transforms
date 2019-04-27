import reversible_transforms.waterworks.waterwork_part as wp
import reversible_transforms.waterworks.tank as ta
import reversible_transforms.tanks.utils as ut
import numpy as np


def add(a, b, type_dict=None, waterwork=None, name=None):
  """Add two objects together in a reversible manner. This function selects out the proper Add subclass depending on the types of 'a' and 'b'.

  Parameters
  ----------
  a : Tube, type that can be summed or None
      First object to be added, or if None, a 'funnel' to fill later with data.
  b : Tube, type that can be summed or None
      Second object to be added, or if None, a 'funnel' to fill later with data.
  type_dict : dict({
    keys - ['a', 'b']
    values - type of argument 'a' type of argument 'b'.
  })
    The types of data which will be passed to each argument. Needed when the types of the inputs cannot be infered from the arguments a and b (e.g. when they are None).

  waterwork : Waterwork or None
    The waterwork to add the tank (operation) to. Default's to the _default_waterwork.
  name : str or None
      The name of the tank (operation) within the waterwork

  Returns
  -------
  Tank
      The created add tank (operation) object.

  """
  type_dict = ut.infer_types(type_dict, a=a, b=b)

  missing_keys = set(['a', 'b']) - set(type_dict.keys())
  if missing_keys:
    raise ValueError("Type(s) of " + str(sorted(missing_keys)) + " not known. Must define in type_dict if nothing is passed to a, b")
  if type_dict['a'] is np.ndarray and type_dict['b'] is np.ndarray:
    return AddNP(a=a, b=b, waterwork=waterwork, name=name)
  elif type_dict['a'] is np.ndarray or type_dict['b'] is np.ndarray:
    class AddMixNPTyped(AddMixNP):
      tube_keys = {
        'target': np.ndarray,
        'non_array': type_dict['a'] if type_dict['a'] is not np.ndarray else type_dict['b'],
        'a_array': bool
      }
    return AddMixNPTyped(a=a, b=b, waterwork=waterwork, name=name)

  class AddBasicTyped(AddBasic):
    tube_keys = {
      'a': type_dict['a'],
      'target': ut.decide_type(type_dict['a'], type_dict['b'])
    }

  return AddBasicTyped(a=a, b=b, waterwork=waterwork, name=name)


class Add(ta.Tank):
  """Add base class. All subclasses must have exactly the same slot_keys, and keys to the tube_dict, although the tube_dict values can vary from subclass to subclass.

  Attributes
  ----------
  slot_keys : list of str
    The tank's (operation's) argument keys. They define the names of the inputs to the tank.
  tube_dict : dict(
    keys - strs. The tank's (operation's) output keys. THey define the names of the outputs of the tank
    values - types. The types of the arguments outputs.
  )
    The tank's (operation's) output keys and their corresponding types.

  """

  slot_keys = ['a', 'b']
  tube_dict = {
    'target': None,
    'smaller_size_array': None,
    'a_is_smaller': None
  }

  def _pour(self, a, b):
    """Raise an error if this abstract function has not been defined by the subclass."""
    raise ValueError("_pour not defined!")

  def _pump(self, *args, **kwargs):
    """Raise an error if this abstract function has not been defined by the subclass."""
    raise ValueError("_pump not defined!")


class AddBasic(Add):
  """The default add tank. Used for things like ints and floats. Will assume that the 'b' argument is the 'smaller' (i.e. has fewer elements) of two.

  Attributes
  ----------
  tube_dict : dict(
    keys - strs. The tank's (operation's) output keys. THey define the names of the outputs of the tank
    values - types. The types of the arguments outputs.
  )
    The tank's (operation's) output keys and their corresponding types.

  """

  tube_dict = {
    'target': None,
    'smaller_size_array': None,
    'a_is_smaller': bool
  }

  def _pour(self, a, b):
    """Execute the add in the pour (forward) direction .

    Parameters
    ----------
    a : int, float, other non array type
      The first argment to be summed.
    b : int, float, other non array type
      The second argment to be summed.

    Returns
    -------
    dict(
      'target': int, float, other non array type
        The result of the sum of 'a' and 'b'.
      'smaller_size_array': int, float, other non array type
        The value of 'b'.
      'a_is_smaller': bool
        Always False
    )

    """
    return {'target': a + b, 'smaller_size_array': ut.maybe_copy(b), 'a_is_smaller': False}

  def _pump(self, target, smaller_size_array, a_is_smaller):
    """Execute the add in the pump (backward) direction .

    Parameters
    ----------
    target :
      The result of the sum of 'a' and 'b'.
    smaller_size_array : int, float, other non array type
      The value of 'b'.
    a_is_smaller: bool
      Always ignored

    Returns
    -------
    dict(
      'a' : int, float, other non array type
        The first argment.
      'b' : int, float, other non array type
        The second argment.
    )

    """
    return {'a': target - smaller_size_array, 'b': ut.maybe_copy(smaller_size_array)}


class AddNP(Add):
  """The tank used to add two numpy arrays together. The 'smaller_size_array' is the whichever of the two inputs has the fewer number of elements and 'a_is_smaller' is a bool which says whether 'a' is that array.

  Attributes
  ----------
  tube_dict : dict(
    keys - strs. The tank's (operation's) output keys. THey define the names of the outputs of the tank
    values - types. The types of the arguments outputs.
  )
    The tank's (operation's) output keys and their corresponding types.

  """

  tube_dict = {
    'target': np.ndarray,
    'smaller_size_array': np.ndarray,
    'a_is_smaller': bool
  }

  def _pour(self, a, b):
    """Execute the add in the pour (forward) direction .

    Parameters
    ----------
    a : np.ndarray
      The first argment to be summed.
    b : np.ndarray
      The second argment to be summed.

    Returns
    -------
    dict(
      'target': np.ndarray
        The result of the sum of 'a' and 'b'.
      'smaller_size_array': np.ndarray
        a or b depending on which has the fewer number of elements. defaults to b.
      'a_is_smaller': bool
        If a has a fewer number of elements then it's true, otherwise it's false.
    )

    """
    a_is_smaller = a.size < b.size
    if a_is_smaller:
      smaller_size_array = ut.maybe_copy(a)
    else:
      smaller_size_array = ut.maybe_copy(b)
    return {'target': a + b, 'smaller_size_array': smaller_size_array, 'a_is_smaller': a_is_smaller}

  def _pump(self, target, smaller_size_array, a_is_smaller):
    """Execute the add in the pump (backward) direction .

    Parameters
    ----------
    target : np.ndarray
      The result of the sum of 'a' and 'b'.
    smaller_size_array : np.ndarray
      The array that have the fewer number of elements
    a_is_smaller: bool
      If a is the array with the fewer number of elements

    Returns
    -------
    dict(
      'a' : np.ndarray
        The first argment.
      'b' : np.ndarray
        The second argment.
    )

    """
    if a_is_smaller:
      a = ut.maybe_copy(smaller_size_array)
      b = target - smaller_size_array
    else:
      a = target - smaller_size_array
      b = ut.maybe_copy(smaller_size_array)

    return {'a': a, 'b': b}


class AddMixNP(Add):
  """The tank used to add a numpy arrays a non numpy array together. The 'smaller_size_array' is the whichever of the two inputs is not the numpy array and 'a_is_smaller' is a bool which says whether 'a' is that array.

  Attributes
  ----------
  tube_dict : dict(
    keys - strs. The tank's (operation's) output keys. THey define the names of the outputs of the tank
    values - types. The types of the arguments outputs.
  )
    The tank's (operation's) output keys and their corresponding types.

  """

  tube_dict = {
    'target': np.ndarray,
    'smaller_size_array': None,
    'a_is_smaller': bool
  }

  def _pour(self, a, b):
    """Execute the add in the pour (forward) direction .

    Parameters
    ----------
    a : int, float, np.ndarray or some other non array type
      The first argment to be summed.
    b : int, float, np.ndarray or some other non array type
      The second argment to be summed.

    Returns
    -------
    dict(
      'target': int, float, np.ndarray or some other non array type
        The result of the sum of 'a' and 'b'.
      'smaller_size_array': int, float, np.ndarray or some other non array type
        The value of the non np.ndarray.
      'a_is_smaller': bool
        if a is the non np.ndarray
    )

    """
    a_is_smaller = type(a) is not np.ndarray
    if not a_is_smaller:
      smaller_size_array = ut.maybe_copy(b)
    else:
      smaller_size_array = ut.maybe_copy(a)
    return {'target': a + b, 'smaller_size_array': smaller_size_array, 'a_is_smaller': a_is_smaller}

  def _pump(self, target, smaller_size_array, a_is_smaller):
    """Execute the add in the pump (backward) direction .

    Parameters
    ----------
    target : int, float, np.ndarray or some other non array type
      The result of the sum of 'a' and 'b'.
    smaller_size_array : int, float, np.ndarray or some other non array type
      The value of the non np.ndarray.
    a_is_smaller: bool
      if a is the non np.ndarray

    Returns
    -------
    dict(
      'a' : int, float, np.ndarray or some other non array type
        The first argment.
      'b' : int, float, np.ndarray or some other non array type
        The second argment.
    )

    """
    if not a_is_smaller:
      a = target - smaller_size_array
      b = ut.maybe_copy(smaller_size_array)
    else:
      a = ut.maybe_copy(smaller_size_array)
      b = target - smaller_size_array

    return {'a': a, 'b': b}
