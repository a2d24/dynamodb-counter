Contributing
============

Contributions are welcome.

Getting started
---------------

To work on the dynamodb-counter codebase, you'll want to clone the project locally
and install the required dependencies via `poetry <https://poetry.eustace.io>`_.

.. code-block:: bash

    > git clone git@github.com:a2d24/dynamodb-counter.git

Installation
------------
.. code-block:: bash

    > pip install dynamodb-counter[boto]



Quickstart
----------

.. code-block:: python

    from dynamodb_counter import Counter

    # This will attempt to create a boto3 dynamodb client using any ENV variables (eg AWS_PROFILE)
    # You may pass in a custom client using the client kwarg (see source code)

    counter = Counter(table='test-table', PK='users', SK='count')

    # Reset the counter
    assert counter.reset() == 0

    # Get the next counter value
    assert counter.next() == 1

    # Custom increment
    assert counter.next(increment=5) == 6

    # Set counter to specific value
    assert counter.set(12) == 12
    assert counter.next() == 13

Documentation
-------------

