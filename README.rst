drf-triad-permissions
=====================

.. image:: https://img.shields.io/badge/packaging-poetry-purple.svg
    :alt: Packaging: poetry
    :target: https://github.com/sdispater/poetry

.. image:: https://img.shields.io/badge/code%20style-black-black.svg
    :alt: Code style: black
    :target: https://github.com/ambv/black

.. image:: https://github.com/lorinkoz/drf-triad-permissions/workflows/code/badge.svg
    :alt: Build status
    :target: https://github.com/lorinkoz/drf-triad-permissions/actions

.. image:: https://coveralls.io/repos/github/lorinkoz/drf-triad-permissions/badge.svg?branch=master
    :alt: Code coverage
    :target: https://coveralls.io/github/lorinkoz/drf-triad-permissions?branch=master

.. image:: https://badge.fury.io/py/drf-triad-permissions.svg
    :alt: PyPi version
    :target: http://badge.fury.io/py/drf-triad-permissions

.. image:: https://pepy.tech/badge/drf-triad-permissions/month
    :alt: Downloads
    :target: https://pepy.tech/project/drf-triad-permissions/

|

Django Rest Framework permissions are a powerful tool for limiting user access to views and viewsets.
However, it's not always easy or clean to set up a comprehensive permission system that can depend on multiple factors,
such as the user coming in the request, the parameters of the matched URL, or the specificities of the object being
requested by the client.

``drf-triad-permissions`` is one of the many approaches for configuring permissions in medium to large scale projects,
with elegance and reusability in mind. It bases the permission system on string triads that can be used both as
permission statements as well as permission expectations.

Triads
------

Triads are strings that can be split in three parts, usually ``resource::object::action``. The substring ``::`` acts
as separator of the parts. Each level can be attached any meaning, but the original intention is to consider that
the first level represents a resource, the second an object, and the third level an action.

For instance, the triad ``polls::all::read`` can be read as "user has access to read all polls". Another example:
``payment::owner:4368::reverse`` can be read as "user has access to reverse payments that match 'owner:4368'". The
'owner:4368' part can have any meaning, in this context, it could signify that 4368 is a user ID, whereas owner means
that the payment is owned by that specific user.

Triads as statements
++++++++++++++++++++

Triads can be used as statements for specifying which permissions a user has. For instance, a user can have this set of
triads attached to their permissions::

    payments::all::read
    payments::from:john@doe.com::all
    payments::year:2020::review

This means that the user can read all payments, do anything with payments from john at doe.com (hopefully himself) and
review all payments from year 2020.

Triads as expectations
++++++++++++++++++++++

The true power of triads come when they are used to define expectations. Suppose we have a DRF ``ModelViewSet`` that
controls the payments. In a model viewset, it's expected that users can "list", "create", "update" and "delete" items.
Additional actions can be defined, such as "review". In this case, this set of triads could be used as expectation::

    payments::all::{action}
    payments::from:{obj.author.email}::{action}
    payments::year:{url.year}::{action}

Expectation triads are assumed to be disjunctive. That is, a user would only need to match ONE of those to be allowed
to perform the action they are intending.

Notice the use of placeholders. Here, triads are relying on certain elements to be interpolated at the actual time of
checking. Placeholders will depend on the payment object being requested (``obj``) and on the year parameter of the URL
that matched the current viewset (``url``). The ``action`` placeholder will be converted to the action provided by DRF
viewsets, such as ``list``, ``update``, ``partial-update`` or ``delete``.

Let's suppose a user with the triad statements we saw before attempts to do a PUT request against the (fake) URL
https://my.domain.com/api/payments-from/2019/10802/. This URL is handled by ``PaymentsViewSet`` whose expectations are
defined in the set of triads we just saw. Since this is a PUT request against a detail endpoint, it's going to get
handled as an "update" action. Let's just assume that the payment 10802 of year 2019 has ``author.email`` equal to
john at doe.com. When DRF's permission machinery checks the permissions of the requesting user against the expected
statements, these are the concrete checks that will be used to test against the user::

    payments::all::update
    payments::from:john@doe.com::update
    payments::year:2019::update

And let's say that the expectation ``payments::from:john@doe.com::update`` will match with the permission
``payments::from:john@doe.com::all``.

Triad matching
++++++++++++++

Triad matching is done by level, with some simplistic rules.

#. Two identical strings always match.
#. The strings ``all`` and ``*`` will match with anything.
#. The string ``read`` will match with ``head``, ``options``, ``get``, ``list`` and ``retrieve``.
#. The string ``write`` will match with ``post``, ``put``, ``patch``, ``delete``, ``create``, ``update``,
   ``partial-update`` and ``destroy``.

It's important to note that matching does not occurr in both directions. If the viewset is expecting ``list`` and the
user has ``all`` the matching succeeds, but the opposite will not.

So, in the example::

    user permission     -> payments::from:john@doe.com::all
    viewset expectation -> payments::from:john@doe.com::update

The first and second level will match by rule 1, and the third level will match by rule 2.

Policies
--------

Triads can be grouped in policies for easy reutilization. This package comes with a pre-defined basic policy:

.. code-block:: python

    class BasicPolicy(Policy):
        allow = [
            "{resource}::all::{action}",
            "{resource}::new::create",
            "{resource}::id:{obj.id}::{action}",
        ]

This policy has the following meaning:

* User must have permission to perform the action on all objects.
* User must have permission to create a new resource (``new`` acts as syntactic sugar here, remember that there is no
  implicit meaning attached to each level).
* User must have permission to perform the action on the specific object, matching by id.

Policies can be used as DRF viewset permissions like this:

.. code-block:: python

    class PaymentsViewSet(ModelViewSet):
        queryset = Payment.objects.all()
        serializer = PaymentSerializer
        permission_classes = BasicPolicy.expand()

Policies are the recommended way of using triad permissions. However, if you need to create a permission class on the
fly, you can use ``drf_triad_permissions.permissions.get_triad_permission``. This function has the same parameters than
the policy class variables, which will be explained in the next section.

Parameters
++++++++++

Policies can be created with the following class variables: ``allow`` and ``deny``. Each class variable accepts a list
of triads that will be evaluated disjunctively, that is, with OR.
For instance, a read-only policy can be created with:

.. code-block:: python

    from drf_triad_permissions import Policy

    class ReadOnlyPolicy(Policy):
        allow = [
            "{resource}::all::{action}",
            "{resource}::id:{obj.id}::{action}",
        ]
        deny = [
            "{resource}::all::write",
        ]

This example of read-only policy can also be created on the fly by calling:

.. code-block:: python

    from drf_triad_permissions import get_triad_permission

    get_triad_permission(
        allow=[
            "{resource}::all::{action}",
            "{resource}::id:{obj.id}::{action}",
        ],
        deny=[
            "{resource}::all::write",
        ],
    )

As final example, if you wanted to limit the basic policy to exclude deletions, you would do this:

.. code-block:: python

    from drf_triad_permissions import BasicPolicy

    class BasicPolicyWithNoDeletions(BasicPolicy):
        deny = [
            "{resource}::all::destroy",
        ]

Triad matching in javascript
----------------------------

It might be useful to do triad matching in javascript, in order to compare the current user permissions against a given
expectation, before diplaying a frontend element or performing a call to action. This package provides a dynamic
javascript module generator, which can be used as follows.

In your Django URLs, you can use:

.. code-block:: python

    from drf_triad_permissions.views import triad_permissions_js

    urlpatterns += [
        path("triad_permissions.js", triad_permissions_js, name="triad-permissions-js")
    ]

You will have to add ``drf_triad_permissions`` to your ``INSTALLED_APPS``.

In your template, you can incorporate the generated file:

.. code-block:: html

    <script type="text/javascript" src="{% url 'triad-permissions-js' %}"></script>

Which provides three functions:

.. code-block:: javascript

    triadPermissions.match(query, perm)
    triadPermissions.matchAny(query, perms)
    triadPermissions.matchAll(query, perms)

Contributing
------------

* Join the discussion at https://github.com/lorinkoz/drf-triad-permissions/discussions.
* PRs are welcome! If you have questions or comments, please use the link above.
* To run the test suite run ``make`` or ``make coverage``. The tests for this project live inside a small django
  project called ``triads_sandbox``.

Credits
-------

* Robert Singer for `drf-access-policy`_, whose idea of policies were the missing piece in the original implementation
  of this project.

.. _drf-access-policy: https://github.com/rsinger86/drf-access-policy
